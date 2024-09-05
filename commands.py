from aiogram.types import ChatMemberUpdated, Message
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import ChatMemberUpdatedFilter, Command

from aiogram.fsm.state import State, StatesGroup
 
from db import Teachers_database
from crm import crm
from config import tg_admins, greeting_message_it, greeting_message_3d


router = Router()
db = Teachers_database()

ALLOWED_IDS = tg_admins

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_name_admin = State()
    waiting_for_phone_admin = State()
    waiting_for_crm_id = State()
    waiting_for_tg_id = State()

import logging

def escape_md(text: str) -> str:
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return ''.join(f"\\{char}" if char in escape_chars else char for char in text)

@router.chat_member()
async def chat_member_updated(event: ChatMemberUpdated):
    if event.old_chat_member.status != event.new_chat_member.status:
        #print(f"Status changed from {event.old_chat_member.status} to {event.new_chat_member.status}")
        username = escape_md(event.new_chat_member.user.username)
        if event.new_chat_member.status == "member":
            #print(f"New member detected: {username}")
            await event.bot.send_message(
                chat_id=event.chat.id,
                text=greeting_message_3d.format(username),parse_mode='Markdown'
            )



@router.message(Command(commands=["start", "help"]))
async def start_help_command(message: Message, state: FSMContext):
    if message.chat.type != 'private':  # Проверяем, что чат является личным
        return
    '''
    
    if message.from_user.id not in ALLOWED_IDS:  # Проверяем, что пользователь в списке разрешенных
        await message.answer("Извините, у вас нет доступа к этой команде.")
        return
    '''

    if message.text == "/start":
        await message.answer("Привет! Это бот для выполнения определенных задач. \nСтарт будет позже")
    elif message.text == "/help":
        await message.answer("Вот список доступных для всех команд:\n/start - Запуск бота\n/help - Помощь\n/registration - Регистрация пользоватлея")

@router.message(Command(commands=["register"]))
async def command_register(message: Message, state: FSMContext):
    crm.update_data()
    # Проверка, есть ли уже преподаватель в базе данных
    if db.get_teacher_by_tg_id(message.from_user.id) is None:
        await message.answer("Введите ваше ФИО полностью (например, Иванов Иван Иванович):")
        await state.set_state(Registration.waiting_for_name)
    else:
        await message.answer("Вы уже зарегистрированы.")

@router.message(Registration.waiting_for_name)
async def register_name(message: Message, state: FSMContext):
    # Сохранение имени пользователя
    crm_id = crm.teachers_raw.get(message.text, None)
    
    if not crm_id:
        await message.answer("Вы не найдены в базе данных CRM, обратитесь к вашему координатору и пройдите регистрацию заново")
        await state.clear()
        return
    await state.update_data(name=message.text)
    await message.answer("Пожалуйста, введите ваш номер телефона в формате 89995463452:")
    await state.set_state(Registration.waiting_for_phone)

@router.message(Registration.waiting_for_phone)
async def register_phone(message: Message, state: FSMContext):
    phone = message.text
    user_id = message.from_user.id

    if not phone.isdigit() or len(phone) != 11:
        await message.answer("Пожалуйста, введите корректный номер телефона в формате 89995463452.")
        return

    # Проверка, есть ли уже преподаватель с таким телефоном в базе данных
    if db.get_teacher_by_phone(phone) is None:
        user_data = await state.get_data()
        name = user_data.get("name")
        crm_id = crm.teachers_raw.get(name, None)
        if not crm_id:
            await message.answer("Вы не найдены в базе данных CRM, обратитесь к вашему координатору")
            await state.clear()

        # Сохранение преподавателя в базе данных
        db.add_teacher(name=name, crm_id=crm_id, tg_id=user_id, phone=phone)
        await message.answer("Регистрация успешно завершена!")
    else:
        await message.answer("Этот номер телефона уже зарегистрирован.")

    await state.clear()

@router.message(Command(commands=["register_admin"]))
async def command_register_admin(message: Message, state: FSMContext):
    if message.from_user.id not in ALLOWED_IDS:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    crm.update_data()
    await message.answer("Введите ФИО преподавателя:")
    await state.set_state(Registration.waiting_for_name_admin)

@router.message(Registration.waiting_for_name_admin)
async def register_name_admin(message: Message, state: FSMContext):
    crm_id = crm.teachers_raw.get(message.text, None)
    if not crm_id:
        await message.answer("Преподаватель не найден в базе данных CRM? начните регистрацию заново")
        await state.clear()
        return
    await state.update_data(name=message.text)
    await state.update_data(crm_id=int(crm_id))
    await message.answer("Введите номер телефона преподавателя в формате 89995463452:")
    await state.set_state(Registration.waiting_for_phone_admin)

@router.message(Registration.waiting_for_crm_id)
async def register_crm_id(message: Message, state: FSMContext):
    crm_id = message.text
    if not crm_id.isdigit():
        await message.answer("Пожалуйста, введите корректный ID.")
        return

    await state.update_data(crm_id=int(crm_id))
    await message.answer("Введите номер телефона преподавателя в формате 89995463452:")
    await state.set_state(Registration.waiting_for_phone_admin)

@router.message(Registration.waiting_for_phone_admin)
async def register_phone_admin(message: Message, state: FSMContext):
    phone = message.text
    phone = phone.translate(str.maketrans('', '', ' ()-'))
    if not phone.isdigit() or len(phone) != 11:
        await message.answer("Пожалуйста, введите корректный номер телефона.")
        return

    await state.update_data(phone=phone)
    await message.answer("Введите Telegram ID преподавателя:")
    await state.set_state(Registration.waiting_for_tg_id)

@router.message(Registration.waiting_for_tg_id)
async def register_tg_id_admin(message: Message, state: FSMContext):
    tg_id = message.text
    if not tg_id.isdigit():
        await message.answer("Пожалуйста, введите корректный Telegram ID.")
        return

    user_data = await state.get_data()
    db.add_teacher(name=user_data['name'], crm_id=user_data['crm_id'], tg_id=int(tg_id), phone=user_data['phone'])
    await message.answer("Регистрация преподавателя успешно завершена!")

    await state.clear()

@router.message(Command(commands=["teachers_db"]))
async def command_register_admin(message: Message):
    if message.from_user.id in ALLOWED_IDS:
        teachers_list = db.fetch_teachers()
        teachers_str_list = [f"ФИО: {teacher[0]}, CRM ID: {teacher[1]}, TG ID: {teacher[2]}, Телефон: {teacher[3]}" for teacher in teachers_list]
        await message.answer(f'Вот актуальный список преподавателей в базе данных:\n{"\n".join(teachers_str_list)}')
    else:
        await message.answer("Извините, у вас нет доступа к этой команде.")


