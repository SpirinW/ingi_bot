import config
from config import tg_ids
from lesson import Lesson
from crm import crm
import datetime as dt
import logging

from typing import Dict

import asyncio
from aiogram import Bot, Dispatcher, types

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.dispatcher.router import Router
from apscheduler.triggers.cron import CronTrigger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import F
from commands import router as commands_router

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('aiogram').setLevel(logging.WARNING)

class Form(StatesGroup):
    waiting_for_message = State()
    waiting_for_feedback = State()
    waiting_for_location = State()

# Инициализация бота и диспетчера
bot = Bot(token=config.bot_token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
scheduler = AsyncIOScheduler()

# Хранилище данных о занятиях
lesson_data: Dict[int, Lesson] = {}

def calculate_distance(lat1, lon1, lat2, lon2):
    location1 = (lat1, lon1)
    location2 = (lat2, lon2)
    return geodesic(location1, location2).meters

def get_coordinates_from_address(address):
    geolocator = Nominatim(user_agent="Ingi Telegram")  
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

def get_inline_students(key: int) -> InlineKeyboardMarkup:
    buttons = []
    for i, name in enumerate(lesson_data[key].students_list):
        if name in lesson_data[key].students_selected:
            name = name + config.check_mark
        button = InlineKeyboardButton(text=name, callback_data=f'attendance_check_{key}_{i}')
        buttons.append([button])  # Добавляем кнопку в список списков
    
    # Добавление кнопок "Отменить выбор" и "Готово"
    all_button = InlineKeyboardButton(text="Отметить всех", callback_data=f'attendance_check_{key}_all')
    cancel_button = InlineKeyboardButton(text="Отменить выбор", callback_data=f'attendance_check_{key}_cancel')
    ready_button = InlineKeyboardButton(text="Готово", callback_data=f'attendance_check_{key}_ready')
    buttons.append([all_button])
    buttons.append([cancel_button])
    buttons.append([ready_button])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons) 

def get_duration(time_from: str, time_to: str) -> str:
    time_from_dt = dt.datetime.strptime(time_from, '%Y-%m-%d %H:%M:%S')
    time_to_dt = dt.datetime.strptime(time_to, '%Y-%m-%d %H:%M:%S')

    time_from_dt -= dt.timedelta(seconds=1)

    duration_minutes = int((time_to_dt - time_from_dt).total_seconds() / 60)

    academic_hours = duration_minutes // 45
    extra_minutes = duration_minutes % 45

    duration_parts = []

    if academic_hours > 0:
        if academic_hours == 1:
            duration_parts.append(f"{academic_hours} час")
        elif 2 <= academic_hours <= 4:
            duration_parts.append(f"{academic_hours} часа")
        else:
            duration_parts.append(f"{academic_hours} часов")

    if extra_minutes > 0:
        duration_parts.append(f"{extra_minutes} минут")

    final_duration = ', '.join(duration_parts)

    return final_duration

async def schedule_fail_notifications(key: int):
    lesson = lesson_data.get(key, None)
    
    if lesson:
        # Время для отправки fail-сообщений
        reminder_fail_time = dt.datetime.combine(dt.datetime.now().date() + dt.timedelta(days=1), dt.time(9, 0))

        presence_fail_time = lesson.time_from - dt.timedelta(minutes=15)# за 15 минут до начала занятия
        if config.test_mode:
            reminder_fail_time = dt.datetime.now() + dt.timedelta(seconds=5)# test time
            presence_fail_time = dt.datetime.now() + dt.timedelta(seconds=5)# test time

        # Планируем fail-сообщение для reminder
        reminder_fail_text_head, reminder_fail_text_coordinator = lesson.get_reminder_text_fail()
        reminder_fail = scheduler.add_job(
            send_scheduled_message, 
            'date', 
            run_date=reminder_fail_time, 
            args=(reminder_fail_text_coordinator, lesson.coordinator_tg, None, "Markdown"), 
            misfire_grace_time=30
        )
        lesson_data[key].reminder_fail_coordinator = reminder_fail.id

        reminder_fail = scheduler.add_job(
            send_scheduled_message, 
            'date', 
            run_date=reminder_fail_time, 
            args=(reminder_fail_text_head, lesson.head_tg, None, "Markdown"), 
            misfire_grace_time=30
        )
        lesson_data[key].reminder_fail_head = reminder_fail.id
        if lesson_data[key].manager_tg:
            reminder_fail = scheduler.add_job(
                send_scheduled_message, 
                'date', 
                run_date=reminder_fail_time, 
                args=(reminder_fail_text_head, lesson.manager_tg, None, "Markdown"), 
                misfire_grace_time=30
            )
            lesson_data[key].reminder_fail_manager = reminder_fail.id

        # Планируем fail-сообщение для presence
        presence_fail_text_head, presence_fail_text_coordinator = lesson.get_presence_text_fail()

        presence_fail = scheduler.add_job(
            send_scheduled_message, 
            'date', 
            run_date=presence_fail_time, 
            args=(presence_fail_text_coordinator, lesson.coordinator_tg, None, "Markdown"), 
            misfire_grace_time=30
        )
        lesson_data[key].presence_fail_coordinator = presence_fail.id

        presence_fail = scheduler.add_job(
            send_scheduled_message, 
            'date', 
            run_date=presence_fail_time, 
            args=(presence_fail_text_head, lesson.head_tg, None, "Markdown"), 
            misfire_grace_time=30
        )
        lesson_data[key].presence_fail_head = presence_fail.id
        if lesson_data[key].manager_tg:
            presence_fail = scheduler.add_job(
                send_scheduled_message, 
                'date', 
                run_date=presence_fail_time, 
                args=(presence_fail_text_head, lesson.manager_tg, None, "Markdown"), 
                misfire_grace_time=30
            )
            lesson_data[key].presence_fail_manager = presence_fail.id

async def daily_fetch():
    next_day = (dt.datetime.now()+ dt.timedelta(days=1)).strftime('%Y-%m-%d') 
    crm.update_data()
    data = crm.get_slots_info_by_date(next_day, status=1)

    key = 0
    lesson_data.clear()

    for type in config.transcript.keys():
        for l in data[type]:
            if config.test_mode and not l['teacher_ids'] == [650]:
                continue
            present_time = dt.datetime.now() + dt.timedelta(seconds=1)

            try:
                location = config.transcript[type]
                lesson = Lesson(l, location)
            except Exception as e:
                m = f'Ошибка получения карточки: {e}'
                print(m)
                await bot.send_message(config.tg_ids.head_it, m)
                continue


            if not lesson.acceptable:
                await bot.send_message(lesson.head_tg, f'Ошибки в карточке {lesson.location}, {lesson.time}, {lesson.subject}\n{lesson.group_link}: {'\n'.join(lesson.errors)}')
                continue

            # 1 Сообщение напоминалка о занятиях завтра
            button = InlineKeyboardButton(text=config.button_reminder_check, callback_data=f'reminder_check_{key}')
            inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]]) 
            message_text = lesson.get_message_reminder()
            scheduler.add_job(send_scheduled_message, 'date', run_date=present_time,
                              args=(message_text, lesson.teacher_tg, inline_keyboard, "Markdown"), misfire_grace_time=30)
            
            
            # 2 Сообщение за 5 мин до занятия, на месте ли преподаватель
            presence_button = InlineKeyboardButton(text=config.presence_message_check, callback_data=f'presence_check_{key}')
            presence_keyboard = InlineKeyboardMarkup(inline_keyboard=[[presence_button]])
            
            presence_time = lesson.time_from - dt.timedelta(minutes=20)#За 20 минут до занятия
            if config.test_mode:
                presence_time = present_time

            scheduler.add_job(send_scheduled_message, 'date', run_date=presence_time,
                              args=(config.presence_message_text, lesson.teacher_tg, presence_keyboard, "Markdown"), misfire_grace_time=30)

            lesson_data[key] = lesson
            await schedule_fail_notifications(key)
            key+=1

async def send_scheduled_message(message, user_id, inline_keyboard=None, parse_mode = None):
    try:
        await bot.send_message(chat_id=user_id, text=message, reply_markup=inline_keyboard, parse_mode=parse_mode)
        #print(f"Сообщение отправлено пользователю {user_id}")  
        logging.info(f"Сообщение отправлено пользователю {user_id}")
    except Exception as e:
        logging.error(f"Сообщение пользователю {user_id} не отправлено. Ошибка: {e}")

async def process_reminder_callback(callback_query: types.CallbackQuery):
    key = int(callback_query.data.replace('reminder_check_', ''))
    lesson = lesson_data.get(key, None)

    if lesson:
        job_id = lesson_data[key].reminder_fail_coordinator
        if job_id and scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        job_id = lesson_data[key].reminder_fail_head
        if job_id and scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        job_id = lesson_data[key].reminder_fail_manager
        if job_id and scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

        message_head, message_coor = lesson.get_reminder_text()
        if message_head:
            await bot.send_message(chat_id=lesson.head_tg, text=message_head, parse_mode='Markdown')
        
        await bot.send_message(chat_id=lesson.coordinator_tg, text=message_coor, parse_mode='Markdown')
        if lesson.manager_tg:
            await bot.send_message(chat_id=lesson.manager_tg, text=message_coor, parse_mode='Markdown')
        
        logging.info(f"Напоминание подтверждено для {lesson.teacher_fio} на {lesson.time} для группы {lesson.group_name}")

    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text="Ошибка: информация о занятии не найдена.")

async def process_presence_callback(callback_query: types.CallbackQuery, state = FSMContext):
    key = int(callback_query.data.replace('presence_check_', ''))
    lesson = lesson_data.get(key, None)

    if lesson:
        job_id = lesson_data[key].presence_fail_coordinator
        if job_id and scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        job_id = lesson_data[key].presence_fail_head
        if job_id and scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        job_id = lesson_data[key].presence_fail_manager
        if job_id and scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

        #Сказать координатору что на месте, отправить все для отметки детей 
        await state.update_data(key=key)
        if lesson.location_type == 'schools':
            if config.do_geo_request:
                await request_geo(callback_query.message, state)
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=config.attendance_message_check, 
                                                                               callback_data=f'attendance_check_{key}_load')]])
                await bot.send_message(chat_id=lesson.teacher_tg, text=config.attendance_message_text, reply_markup=keyboard)
            pass
        else:
            await bot.send_message(chat_id=callback_query.from_user.id, text=config.lesson_theme_request_text)
            await state.set_state(Form.waiting_for_message)
        logging.info(f"Присутсвие подтверждено для {lesson.teacher_fio} на {lesson.time} для группы {lesson.group_name}")
            # Продолжить процесс
            #await process_lesson_confirmation(callback_query, state)

        # Запрашиваем тем для занятия
        '''
        -----
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=config.attendance_message_check, 
                                                                               callback_data=f'attendance_check_{key}_load')]])
        await bot.send_message(chat_id=lesson.teacher_tg, text=config.attendance_message_text, reply_markup=keyboard)
        '''
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"Ошибка: информация о занятии не найдена. {lesson_data}\n{callback_query.data}")

async def request_geo(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text="Пожалуйста, отправь свою геолокацию.\nНе забудь выключить VPN!")
    await state.set_state(Form.waiting_for_location)

@dp.message(Form.waiting_for_location)
async def process_location_message(message: types.Message, state: FSMContext):
    user_location = message.location
    data = await state.get_data()
    key = data.get('key')
    lesson = lesson_data.get(key, None)

    if lesson:
        # Получаем координаты из адреса
        lesson_lat, lesson_lon = get_coordinates_from_address(lesson.address)

        if lesson_lat is None or lesson_lon is None:
            await bot.send_message(chat_id=message.chat.id, text="Не удалось определить координаты места занятия. Пожалуйста, обратитесь к координатору.")
            return

        # Проверяем расстояние
        distance = calculate_distance(user_location.latitude, user_location.longitude, lesson_lat, lesson_lon)
        if distance <= 100:  # Например, допускается расстояние до 100 метров
            await bot.send_message(chat_id=message.chat.id, text=f"Отлично, ты на месте")
            await process_lesson_confirmation(message, state)
        else:
            await bot.send_message(chat_id=message.chat.id, text=f"Вы слишком далеко от места занятия ({int(distance)} метров). Пожалуйста, подойдите ближе.")

async def process_lesson_confirmation(message, state: FSMContext):
    data = await state.get_data()
    key = data.get('key')
    lesson = lesson_data.get(key, None)

    # Запрашиваем тему занятия
    await bot.send_message(chat_id=message.chat.id, text=config.lesson_theme_request_text)
    await state.set_state(Form.waiting_for_message)
    '''
    message_head, message_coor = lesson.get_presence_text()
    if message_head:
        await bot.send_message(chat_id=lesson.head_tg, text=message_head, parse_mode='Markdown')
    
    await bot.send_message(chat_id=lesson.coordinator_tg, text=message_coor, parse_mode='Markdown')
    await bot.send_message(chat_id=lesson.manager_tg, text=message_coor, parse_mode='Markdown')
    
    '''

    if lesson.location != config.transcript['schools']:
        # Если это гш, запускаем алгоритм по отметке детей
        await send_message_feedback(key)

@dp.message(Form.waiting_for_message)
async def handle_next_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key = data.get('key')
    lesson_data[key].lesson_theme = message.text
    #await message.answer(f"Вы отправили: {message.text} для урока с ключом {key}")
    # Сбрасываем состояние
    await state.clear()
    
    message_head, message_coor = lesson_data[key].get_presence_text()
    if message_head:
        await bot.send_message(chat_id=lesson_data[key].head_tg, text=message_head, parse_mode='Markdown')
    
    await bot.send_message(chat_id=lesson_data[key].coordinator_tg, text=message_coor, parse_mode='Markdown')
    if not lesson_data[key].manager_tg:
        await bot.send_message(chat_id=lesson_data[key].manager_tg, text=message_coor, parse_mode='Markdown')

    if lesson_data[key].location == config.transcript['schools']:
        # Если это гш, запускаем алгоритм по отметке детей
        await send_message_attendance(message, key)
    else:
        await send_message_feedback(key)

async def send_message_attendance(message: types.Message, key:int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=config.attendance_message_check, 
                                                                               callback_data=f'attendance_check_{key}_load')]])
    await bot.send_message(chat_id=message.chat.id, text=config.attendance_message_text, reply_markup=keyboard)

async def send_message_feedback(key:int):
    lesson = lesson_data.get(key, None)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Да', callback_data=f'feedback_{key}_yes'),
        InlineKeyboardButton(text='Нет', callback_data=f'feedback_{key}_no')]])

    await bot.send_message(lesson.teacher_tg, config.message_feedback_request_text, reply_markup=keyboard)

async def process_attendance_callback(callback_query: types.CallbackQuery):
    key, index = callback_query.data.replace('attendance_check_', '').split('_')
    key = int(key)
    #print(lesson_data, callback_query.data, key, type(key))
    if index == 'load':
        keyboard = get_inline_students(key)
        await bot.send_message(callback_query.from_user.id, text = config.attendance_message_load, reply_markup=keyboard)
        return None
    elif index == 'cancel':
        lesson_data[key].students_selected = []
    elif index.isdigit():
        index = int(index)
        selected_student = lesson_data[key].students_list[index]
        if selected_student not in lesson_data[key].students_selected:
            lesson_data[key].students_selected.append(selected_student)
        else:
            lesson_data[key].students_selected.remove(selected_student)
    elif index == 'all':
        lesson_data[key].students_selected = set(lesson_data[key].students_list)
    elif index == 'ready':
        #coordinator = config.vlad
        #Отправить координатору список присудствующих
        message_head, message_coor = lesson_data[key].get_attendance_text()
        if message_head != '':
            await bot.send_message(chat_id=lesson_data[key].head_tg, text=message_head, parse_mode='Markdown')
        
        await bot.send_message(chat_id=lesson_data[key].coordinator_tg, text=message_coor, parse_mode='Markdown')
        if lesson_data[key].manager_tg:
            await bot.send_message(chat_id=lesson_data[key].manager_tg, text=message_coor, parse_mode='Markdown')
        
        await send_message_feedback(key)

        logging.info(f"Посещаемость отправлена от {lesson_data[key].teacher_fio} на {lesson_data[key].time} для группы {lesson_data[key].group_name}")
        return None
    keyboard = get_inline_students(key)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    #Здесь

async def process_feedback_callback(callback_query: types.CallbackQuery, state = FSMContext):
    key, index = callback_query.data.replace('feedback_', '').split('_')
    key = int(key)
    lesson = lesson_data.get(key, None)

    if index == 'yes':
        await state.clear()
        await state.update_data(key=key)
        await bot.send_message(lesson.teacher_tg, config.feedback_template)
        await state.set_state(Form.waiting_for_feedback)
    elif index == 'no':
        await bot.send_message(lesson.teacher_tg, config.message_feedback_last)

@dp.message(Form.waiting_for_feedback)
async def process_feedback_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key = data.get('key')
    lesson = lesson_data[key]

    # Проверяем, прислал ли пользователь изображение с подписью или текстовое сообщение
    if message.content_type == 'photo':
        lesson.feedback = message.caption
        # Добавляем атрибут photo динамически
        lesson.photo = message.photo[-1].file_id
    elif message.content_type == 'text':
        lesson.feedback = message.text

    # Сбрасываем состояние
    await state.clear()

    # Отправляем подтверждение преподавателю
    await bot.send_message(lesson.teacher_tg, config.message_feedback_last)

    # Формируем и отправляем сообщение с обратной связью для руководителя и координатора
    message_head, message_coor = lesson.get_feedback_text()

    # Если изображение присутствует, отправляем его руководителю и координатору
    if hasattr(lesson, 'photo'):
        if message_head != '':
            await bot.send_photo(chat_id=lesson.head_tg, photo=lesson.photo, caption=message_head, parse_mode='Markdown')
        await bot.send_photo(chat_id=lesson.coordinator_tg, photo=lesson.photo, caption=message_coor, parse_mode='Markdown')
    else:
        if message_head != '':
            await bot.send_message(chat_id=lesson.head_tg, text=message_head, parse_mode='Markdown')
        
        await bot.send_message(chat_id=lesson.coordinator_tg, text=message_coor, parse_mode='Markdown')

async def on_startup(dp: Dispatcher):
    scheduler.start()

    # Пример тестовой задачи
    #await send_scheduled_message("Тестовое сообщение для проверки вручную", config.vlad)
    #
    if config.test_mode:
        await daily_fetch()
    else:
        scheduler.add_job(daily_fetch, CronTrigger(hour=21, minute=0))
    #scheduler.add_job(daily_fetch, 'cron', hour=0, minute=0)

async def main():
    print("Starting main()")  # Отладочный вывод
    router = Router()
    router.callback_query.register(process_reminder_callback, F.data.startswith('reminder_check'))
    router.callback_query.register(process_presence_callback, F.data.startswith('presence_check'))
    router.callback_query.register(process_attendance_callback, F.data.startswith('attendance_check_'))
    router.callback_query.register(process_feedback_callback, F.data.startswith('feedback_'))
    dp.include_router(router)
    dp.include_router(commands_router)  # Подключение команды

    await on_startup(dp)

    print("Запуск polling")  # Отладочный вывод
    await dp.start_polling(bot)

if __name__ == '__main__':
    print("Запуск программы")  # Отладочный вывод
    asyncio.run(main())
