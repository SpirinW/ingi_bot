from aiogram.types import ChatMemberUpdated, Message
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F, types


from db import TeachersDatabase
from crm import CRM
from config import tg_admins
from raw_texts import greeting_message_it, greeting_message_3d


router = Router()
db = TeachersDatabase()

ALLOWED_IDS = tg_admins

cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel_registration")
inline_keyboard_cancel = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_name_admin = State()
    waiting_for_phone_admin = State()
    waiting_for_crm_id = State()
    waiting_for_tg_id = State()

class Deletion(StatesGroup):
    waiting_for_crm_id = State()

def escape_md(text: str) -> str:
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return ''.join(f"\\{char}" if char in escape_chars else char for char in text)

@router.chat_member()
async def chat_member_updated(event: ChatMemberUpdated) -> None:
    if event.old_chat_member.status != event.new_chat_member.status:
        username = escape_md(event.new_chat_member.user.username)
        if event.new_chat_member.status == "member":
            await event.bot.send_message(
                chat_id=event.chat.id,
                text=greeting_message_3d.format(username),parse_mode='Markdown'
            )



@router.message(Command(commands=["start", "help"]))
async def start_help_command(message: Message, state: FSMContext) -> None:
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
        await message.answer("Вот список доступных для всех команд:\n/start - Запуск бота\n/help - Помощь\n/register - Регистрация пользоватлея")

@router.message(Command(commands=["register"]))
async def command_register(message: Message, state: FSMContext) -> None:
    # Проверка, есть ли уже преподаватель в базе данных
    if db.get_teacher_by_tg_id(message.from_user.id) is None:
        await message.answer("Введите ваше ФИО полностью (например, Иванов Иван Иванович):", reply_markup=inline_keyboard_cancel)
        await state.set_state(Registration.waiting_for_name)
    else:
        await message.answer("Вы уже зарегистрированы.")

@router.message(Registration.waiting_for_name)
async def register_name(message: Message, state: FSMContext) -> None:
    # Сохранение имени пользователя
    crm_id = CRM().teachers_raw.get(message.text, None)
    if not crm_id:
        await message.answer("Вы не найдены в базе данных CRM, обратитесь к вашему координатору и пройдите регистрацию заново")
        await state.clear()
        return
    if db.get_teacher_by_crm_id(crm_id) is None:
        await state.update_data(name=message.text)
        await message.answer("Пожалуйста, введите ваш номер телефона в формате 89995463452:")
        await state.set_state(Registration.waiting_for_phone)
    else:
        await message.answer("Вы уже зарегистрированы.")
        await state.clear()


@router.message(Registration.waiting_for_phone)
async def register_phone(message: Message, state: FSMContext) -> None:
    phone = message.text
    user_id = message.from_user.id

    if not phone.isdigit() or len(phone) != 11:
        await message.answer("Пожалуйста, введите корректный номер телефона в формате 89995463452.")
        return

    # Проверка, есть ли уже преподаватель с таким телефоном в базе данных
    if db.get_teacher_by_phone(phone) is None:
        user_data = await state.get_data()
        name = user_data.get("name")
        crm_id = CRM().teachers_raw.get(name, None)
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
async def command_register_admin(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ALLOWED_IDS:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    CRM().update_data()
    await message.answer("Введите ФИО преподавателя:", reply_markup=inline_keyboard_cancel)
    await state.set_state(Registration.waiting_for_name_admin)

@router.callback_query(F.data == "cancel_registration")
async def process_cancel_registration(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()  # Сброс всех состояний
    await callback_query.message.edit_reply_markup(reply_markup=None)  # Убираем инлайн-клавиатуру
    await callback_query.message.answer("Процесс регистрации отменен.")

@router.message(Registration.waiting_for_name_admin)
async def register_name_admin(message: Message, state: FSMContext) -> None:
    crm_id = CRM().teachers_raw.get(message.text, None)
    if not crm_id:
        button1 = InlineKeyboardButton(text='Внести вручную', callback_data=f'crm_admin_input')
        button2 = InlineKeyboardButton(text='Заново', callback_data=f'crm_admin_cancel')
        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1], [button2]]) 
        await message.answer("Преподаватель не найден в базе данных CRM. Начнете регистрацию заново?", reply_markup=inline_keyboard)
        await state.update_data(name=message.text)  # Сохраняем имя пользователя
        return
    
    # Если ID найден, продолжаем регистрацию
    await state.update_data(name=message.text)
    await state.update_data(crm_id=int(crm_id))
    await message.answer("Введите номер телефона преподавателя в формате 89995463452:")
    await state.set_state(Registration.waiting_for_phone_admin)


# Обработка callback-кнопок "Внести вручную" и "Заново"
@router.callback_query(F.data.startswith("crm_admin_"))
async def process_crm_admin_callback(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    action = callback_query.data.replace('crm_admin_', '')
    
    if action == 'input':  # Внести вручную
        await callback_query.message.answer("Пожалуйста, введите CRM ID преподавателя вручную.")
        await state.set_state(Registration.waiting_for_crm_id)  # Ожидание ввода ID вручную

    elif action == 'cancel':  # Начать заново
        await callback_query.message.answer("Начнем регистрацию заново. Введите ФИО преподавателя:")
        await state.set_state(Registration.waiting_for_name_admin)  # Вернуться к вводу имени

    # Убираем кнопки с предыдущего сообщения
    await callback_query.message.edit_reply_markup(reply_markup=None)


# Обработка ручного ввода CRM ID
@router.message(Registration.waiting_for_crm_id)
async def register_crm_id(message: Message, state: FSMContext) -> None:
    crm_id = message.text
    if not crm_id.isdigit():
        await message.answer("Пожалуйста, введите корректный CRM ID.")
        return

    # Сохраняем CRM ID и продолжаем процесс регистрации
    await state.update_data(crm_id=int(crm_id))
    await message.answer("Введите номер телефона преподавателя в формате 89995463452:")
    await state.set_state(Registration.waiting_for_phone_admin)

@router.message(Registration.waiting_for_phone_admin)
async def register_phone_admin(message: Message, state: FSMContext) -> None:
    phone = message.text
    phone = phone.translate(str.maketrans('', '', ' ()-'))
    if not phone.isdigit() or len(phone) != 11:
        await message.answer("Пожалуйста, введите корректный номер телефона.")
        return

    await state.update_data(phone=phone)
    await message.answer("Введите Telegram ID преподавателя:")
    await state.set_state(Registration.waiting_for_tg_id)

@router.message(Registration.waiting_for_tg_id)
async def register_tg_id_admin(message: Message, state: FSMContext) -> None:
    tg_id = message.text
    if not tg_id.isdigit():
        await message.answer("Пожалуйста, введите корректный Telegram ID.")
        return

    user_data = await state.get_data()
    db.add_teacher(name=user_data['name'], crm_id=user_data['crm_id'], tg_id=int(tg_id), phone=user_data['phone'])
    await message.answer("Регистрация преподавателя успешно завершена!")

    await state.clear()

@router.message(Command(commands=["teachers_db"]))
async def command_register_admin(message: Message) -> None:
    if message.from_user.id in ALLOWED_IDS:
        teachers_list = db.fetch_teachers()
        teachers_str_list = [str(teacher)[1:-1] for teacher in teachers_list]
        await message.answer(f'Вот актуальный список преподавателей в базе данных(ФИО, CRM ID, TG ID, Телефон):\n{"\n".join(teachers_str_list)}')
    else:
        await message.answer("Извините, у вас нет доступа к этой команде.")


@router.message(Command(commands=["delete_teacher"]))
async def command_delete_teacher(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ALLOWED_IDS:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    await message.answer("Введите CRM ID преподавателя, которого вы хотите удалить:")
    await state.set_state(Deletion.waiting_for_crm_id)

# Обработка CRM ID преподавателя
@router.message(Deletion.waiting_for_crm_id)
async def delete_teacher(message: Message, state: FSMContext) -> None:
    crm_id = message.text

    if not crm_id.isdigit():
        await message.answer("Пожалуйста, введите корректный CRM ID.")
        return

    teacher = db.get_teacher_by_crm_id(int(crm_id))
    
    if teacher is None:
        await message.answer("Преподаватель с таким CRM ID не найден.")
        await state.clear()
        return

    # Отправляем информацию о преподавателе и кнопки для удаления или отмены
    teacher_info = f"ФИО: {teacher[0]}, CRM ID: {teacher[1]}, TG_ID: {teacher[2]}, Телефон: {teacher[3]}"
    delete_button = InlineKeyboardButton(text="Удалить", callback_data=f'delete_confirm_{crm_id}')
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="delete_cancel")
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[delete_button], [cancel_button]])
    
    await message.answer(f"Вы хотите удалить следующего преподавателя?\n\n{teacher_info}", reply_markup=inline_keyboard)
    await state.clear()

# Обработка нажатия на кнопки "Удалить" и "Отмена"
@router.callback_query(F.data.startswith("delete_confirm_"))
async def process_delete_confirm(callback_query: types.CallbackQuery) -> None:
    crm_id = int(callback_query.data.replace("delete_confirm_", ""))
    
    # Удаление преподавателя
    db.delete_teacher_by_crm_id(crm_id)
    
    await callback_query.message.edit_reply_markup(reply_markup=None)  # Убираем кнопки
    await callback_query.message.answer(f"Преподаватель с CRM ID {crm_id} успешно удален.")

@router.callback_query(F.data == "delete_cancel")
async def process_delete_cancel(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.edit_reply_markup(reply_markup=None)  # Убираем кнопки
    await callback_query.message.answer("Удаление отменено.")