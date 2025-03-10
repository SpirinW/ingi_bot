from dotenv import load_dotenv
import os

test_mode = True
do_geo_request = False
geo_max_distance = 100 # В метрах
do_it_head_notifications = False
do_3d_head_notifications = True
lesson_delay = 25 #mins
responce_threshold = 10 #mins

load_dotenv()

test_token = os.getenv("TEST_TOKEN")
bot_token_old = os.getenv("BOT_TOKEN_OLD")
bot_token = os.getenv("BOT_TOKEN")
if test_mode:
    bot_token = test_token
geo_token = os.getenv("GEO_TOKEN")
CRM_CREDENTIALS = {
    "email": os.getenv("CRM_EMAIL"),
    "api_key": os.getenv("CRM_API_KEY"),
}


class TgIds:
    head_it = int(os.getenv("HEAD_IT", 0))
    coordinator_it = int(os.getenv("COORDINATOR_IT", 0))
    vlad_personal = int(os.getenv("VLAD_PERSONAL", 0))
    coordinator_it = head_it
    head_3d = int(os.getenv("HEAD_3D", 0))
    coordinator_3d = int(os.getenv("COORDINATOR_3D", 0))

    manager_smirnov = int(os.getenv("MANAGER_SMIRNOV", 0))
    manager_ryazanova = int(os.getenv("MANAGER_RYAZANOVA", 0))
    manager_kostygova = int(os.getenv("MANAGER_KOSTYGOVA", 0))

    ing_admin = int(os.getenv("ING_ADMIN", 0))
    
manager_transcript = {
    'Менеджер школы: Смирнов': TgIds.manager_smirnov,
    'Менеджер школы: Рязанова': TgIds.manager_ryazanova,
    'Менеджер школы: Костыгова': TgIds.manager_kostygova
}

locations_raw = {
    'schools': {177, None}, 
    'tp': {201, 232, 233, 234, 183, 184, 41, 42, 2, 3, 4, 40, 190, 241},
    'water': {202, 169, 170, 171},
    'odin': {172, 173, 174},
    'web': {182}
}

tg_admins = {key for name, key in vars(TgIds).items() if not name.startswith('__')}

transcript = {
    'schools': 'ГШ', 
    'tp': 'ТП Бауманская',
    'water': 'Тп Водный',
    'odin': 'Тп Одинцово',
    'web': 'Вебинар'
}


'''
Типы уроков в CRM
 personal
 Индивидуальный [ID 1]	 
 interview
 Пробный [ID 3]	 

 group
 Групповой [ID 2]	 
 Школа 2 транспорт [ID 4]	 
 Школа 3 пеший [ID 5]	 
 Школа 3 транспорт [ID 6]	 
 Школа интенсив [ID 7]	 
 Разовый МК/Интенсив [ID 8]	 
 Выездной МК [ID 9]	 
 МК ТП [ID 10]	 
 WS [ID 11]	 
 Урок технологии [ID 12]	 
 Учебный день  [ID 13]	 
 Лагерь [ID 14]	 
 Школа 2 пеший [ID 15]	 
 Детский сад [ID 16]	 
 Краткий курс [ID 17]	 
 Вебинар [ID 18]	 
 Проверка задания [ID 19]	 
 Перерыв [ID 20]	 
 Групповое восстановление [ID 21]	 
 Индивидуальное восстановление [ID 22]	 
 Выездной лагерь [ID 23]
'''

it_subjects = {
    235 : "IT: AR",
    233 : 'IT: Летний интенсив',
    234 : 'IT: Предпроф. олимпиада',
    212 : '«C++. Базовый уровень»',
    210 : '«C++. Начальный уровень»',
    211 : '«Python. Базовый уровень»',
    213 : '«Python. Начальный уровень»',
    229 : 'Мастер-класс: Roblox программирование 1-4 класс',
    227 : 'Мастер-класс: WEB программирование 5-8 класс',
    224 : 'Мастер-класс: Программирование Python 5-8 класс',
    226 : 'Мастер-класс: Программирование С++ 9-11 класс',
    138 : 'IT: Python',
    187 : 'IT: Python 2.0',
    196 : 'IT:Python в Minecraft',
    171 : 'IT: Большие данные',
    141 : 'IT: Искусственный интеллект',
    7 : 'IT: C++',
    142 : 'IT: Геймдизайн',
    176 : 'IT: Java',
    199 : 'IT: Олимпиадное программирование',
    193 : 'IT: Алгоритмы и ДП',
    217 : 'IT:Construct',
    139 : 'IT: Web',
    181 : 'IT: Проект',
    170 : 'IT: Информационная безопасность',
    140 : 'IT: Основы компьютерной грамотности',
    6 : 'IT: Scratch',
    194 : 'IT: Roblox',
    208 : 'IT: Программирование',
    172 : 'IT: Предпроф.экзамен',
    169 : 'IT: ИИ Онлайн',
    129 : 'IT: C++ Онлайн',
    130 : 'IT: Python Онлайн',
    175 : 'IT: Figma',
    115 : 'IT: Видеопроизводство',
    40 : 'IT: Граф.дизайн',
    198 : 'Графический дизайн',
    183 : 'UX/UI дизайн',
    192 : 'VR',
    10 : 'Математика',
    20 : 'Физика 2.0',
    12 : 'Физика',
    117 : 'Инженерный бизнес и менеджмент (ИБМ)',
    30 : 'Нейротехнологии',
    48 : 'Онлайн Геймдизайн',
    134 : 'онлайн Программирование Scratch',
    21 : 'Программирование',
    137 : 'Геймдизайн (Unity) онлайн',
    162 : 'Программирование SCRATCH 1-4, Робототехника EV3 5-8',
    161 : 'Программирование PYTHON 5-8',
    163 : 'Программирование SCRATCH 1-4',
    133 : 'Разработка  приложений дополненной реальности онлайн',
    5 : 'Основы программирования',
    14 : 'Промышленный дизайн',
    132 : 'Создание приложений Android онлайн',
    131 : 'Создание игр Unity онлайн',
    204 : 'C++. Начальный уровень',
    201 : 'Python. Базовый уровень.',
    38 : 'IT: Python Онлайн замена',
    17 : 'IT: Публикация поста',
    39 : 'IT: С++ Онлайн замена',
    51 : 'IT: С++ Онлайн Закрытый клуб',
    203 : 'C++. Базовый уровень',
    202 : 'Python. Начальный уровень',
    18 : 'IT: Python Онлайн Закрытый клуб'
}

robo_3d_subjects = {
 265: 'Робо: Wedo',
 32: 'Летний интенсив',
 178: 'ГШ: предпроф.экзамен',
 179: 'ГШ: проект',
 177: 'ГШ: предпроф.олимпиада',
 180: 'ГШ: премия',
 42: 'ГШ: Криология',
 26: 'ГШ: Инженерия космических систем (ИКС)',
 197: 'КМИ',
 184: '3D: Компас',
 186: 'Программирование в 3D',
 189: 'Подводная автономная робототехника',
 185: 'Космическая инженерия',
 191: 'Криология',
 209: 'Сортировка наборов',
 206: 'Новогодний мастер класс',
 188: 'Подводная телеуправляемая робототехника',
 216: 'Боевые роботы',
 214: 'КЮИ 2.0',
 190: 'Субтрактивные технологии',
 182: 'Электротехника и микроконтроллеры',
 215: 'Игронавтика',
 35: '3D -ручки',
 149: '3D: Blender',
 83: '3D: Inventor',
 73: '3D: TinkerCad',
 29: '3D: Инженерная графика',
 155: '3D: КМИ 2.0',
 110: '3D: Лазеры',
 164: 'КМИ 2.0',
 116: 'КЮИ',
 2: '3D: КМИ',
 113: 'Робо: Kuka',
 154: 'Робо: Spike',
 1: 'Робо: EV3',
 159: 'Робо: КМИ',
 158: 'Робо: КМИ 2.0',
 15: 'Робо: Схемотехника',
 44: 'Робо: Мобильная',
 100: 'Робо: Промышленная',
 8: 'Робо:WeDo',
 16: 'Робо: Arduino',
 13: 'Композиты',
 165: 'Новогодний интенсив',
 150: 'Интенсив',
 144: 'Робототехника WEDO 2.0'
}

rest_subjects = {
'программирование AVR',
'IT: КМИ',
'Гидравлика и пневматика',
'Новогодний интенсив',
'Интенсив',
'Онлайн-интенсив',
'Предпроф. олимпиада',
'Ракетостроение',
'Ракеты',
'Софья 3д',
'Робототехника WEDO 2.0',
'Робототехника WEDO дошкольники',
'Видео',
'Холодильники',
'Рождественский интенсив',
'Летний интенсив',
'ГШ: предпроф.экзамен',
'ГШ: проект',
'ГШ: предпроф.олимпиада',
'ГШ: премия',
'ГШ: Криология',
'ГШ: Инженерия космических систем (ИКС)',
'КМИ',
'3D Программирование',
'3D: Компас',
'Программирование в 3D',
'Подводная автономная робототехника',
'Космическая инженерия',
'Криология',
'Инжик',
'Новогодний мастер класс',
'Отработка',
'Шахматы',
'Подводная телеуправляемая робототехника',
'Субтрактивные технологии',
'Электротехника и микроконтроллеры',
'3D -ручки',
'3D онлайн: TinkerCad',
'3D: SolidWorks -',
'3D: AutoCAD',
'3D: Blender',
'3D: Fusion360',
'3D: Inventor',
'3D: TinkerCad',
'3D: Инженерная графика',
'3D: КМИ 2.0',
'3D: Лазеры',
'КМИ 2.0',
'КЮИ',
'3D: КМИ',
'Робо: Kuka',
'Робо: Spike',
'Робо: EV3',
'Робо: КМИ',
'Робо: КМИ 2.0',
'Робо: Схемотехника',
'Робо: Мобильная',
'Робо: Промышленная',
'Робо: WeDo',
'Робо: Arduino',
'Композиты',
'Мастер-класс: Робо-мастерская 1-4 класс',
'Мастер-класс: Робо-мастерская 5-8 класс',
'Мастер-класс: Создание слайма 1-4 класс',
'Мастер-класс: Флаг в пробирке 1-4 класс',
'Мастер-класс: Юные инженеры 5-7 лет',
'Сортировка наборов',
'Учебный день',
'Био: Биотехнология',
'Био: КМИ',
'Био: Лабораторный и медицинский анализ',
'Био: Медицинский социальный уход',
'Био: Генетика',
'Экзамен. Теория.',
'Экзамен. Практика.',
'Боевые роботы',
'Игронавтика',
'КЮИ 2.0',
'Мастер-класс: 3D моделирование 1-4 класс',
'Мастер-класс: 3D моделирование 5-8 класс',
'Мастер-класс: Бизнес игра 5-8 класс',
'Мастер-класс: Извлечение ДНК и плазмолиз 5-8 класс',
'Мастер-класс: Картина из стабилизированного мха 1-4 класс',
'Мастер-класс: Молекулярная кухня 1-4 класс',
}

