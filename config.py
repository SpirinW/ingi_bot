vlad = '289988172'
test_token = "6402177202:AAHVauhCoi7zgnnntjYr2QVP2pfWptKBSsg"
bot_token_old = '5798234250:AAFjVCvv-INz601SOxy0yLE9jxKGDgCBiXY'
bot_token = '7381557017:AAG8l8Xbzv1NJaHP3HFAQjQHuTdr092YOUM'
#bot_token = test_token
#crm
CRM_CREDENTIALS = {
    "email": "ks@emtc.ru",
    "api_key": "d07c6da9-82c1-11e9-a759-0cc47ae3c526"
}

# geo
GEO_TOKEN = "pk.d646a5dcaa35b724d0b297d5ce4c10e6"
geo_max_distance = 100 # В метрах
do_geo_request = True


class tg_ids:
    head_it= 6502271152 # Спирин Владислав
    coordinator_it = 6467883559 # Злобина Екатерина
    vlad_personal = 289988172

    head_3d = 509739897 # Королев Сергей
    coordinator_3d = 764502758 # Величко Дарья

    manager_smirnov = 1971878796,
    manager_ryazanova = 6131375593,
    manager_kostygova = 373394696

manager_transcript = {
    'Менеджер школы: Смирнов': 1971878796,
    'Менеджер школы: Рязанова': 6131375593
}

locations_raw = {
    'schools': {177, None}, 
    'tp': {201, 232, 233, 234, 183, 184, 41, 42, 2, 3, 4, 40, 190},
    'water': {202, 169, 170, 171},
    'odin': {202, 169, 170, 171}
}

tg_admins = {key for name, key in vars(tg_ids).items() if not name.startswith('__')}

transcript = {
    'schools': 'ГШ', 
    'tp': 'ТП Бауманская',
    'water': 'Тп Водный',
    'odin': 'Тп Одинцово',
}
check_mark = '✅'

reminder_message_text = "Привет!\nНапоминаю тебе о завтрашнем занятии:\nМесто: {}\nАудитория: {}\nПредмет: {}\nВремя: {}\nДлительность(в часах): {}\nОбязательно дай нам знать что ты готов👇"
button_reminder_check = "Прочитал, на занятии буду"

presence_message_text = "Твое занятие вот-вот начнется... \nТы на месте? Ответь внизу👇"
presence_message_check = "Я на месте!"

lesson_theme_request_text = "Супер. Отправь следующием сообщением тему занятия + описание (2-3 предложения)"

attendance_message_text = "Отлично. скажи когда будешь готов отмечать детей👇"
attendance_message_load = 'Отметь детей ниже, просто выбери всех, кто присутствует.\nЕсли кого-то нет в списке, напиши об этом своему координатору\nКогда будешь готов, Нажми на кнопку "Готово"'
attendance_message_check = "Я готов отмечать"
attendance_message_coordinator = "Посещаемость в {} по предмету {}, время {}\nТема {}\n{}"

message_last_tp = "Всех отметили, я отправлю данные администратору, а тебе хорошего занятия!"
message_last_school = "Всех отметили, я отправлю данные администратору, а тебе хорошего занятия! Если кто-то дойдёт позже, то ты сможешь отметить его уже после занятия, я тебе напишу)"

message_feedback_request_text = "Кстати. Ты можешь отправить обратную свзяь по занятию.\nСообщить о проблемах в оборудовании/детях/забыл отметить и т.д.\nНужна ли обратная связь?👇"
message_feedback_yes = "Хорошо. Отправь следующием сообщением обратную связь, я передам ее координатору направления"
message_feedback_last = "Хорошего тебе дня!"

feedback_template = "Если на занятии возникали проблемы с определенным учеником (или учениками), ты можешь написать здесь его ФИО и конкретные кейсы на занятии. Например: ФИО отвлекал всех на занятии, кричал, на замечания никак не реагировал)"

greeting_message_it = """Привет @{}! 

Добро пожаловать в IT-направление Инжинириум МГТУ им Баумана 

Просьба ознакомится с информацией ниже: 

1. Адрес нашего технопарка: Госпитальный переулок 4/6 с1 (здание общежития возле УЛК), вход где шлагбаум, на двери большая сова) 
2. [Важная информация](https://it-ingi.yonote.ru/share/4607bb98-a56d-4f93-879f-043d51aa547b) (правила для преподавателей, аудитории и технический гайд по технопарку
3. [Ссылка](https://it-ingi.yonote.ru/share/13666509-51c2-498c-a916-4819078555aa) на важные материалы (методы, курсы, расписание) 

Контакты для связи: 
[Влад](https://t.me/VV_Spirin) (руководитель направления)

[Катя](https://t.me/katerrinap) (координатор) по всем организационным вопросам 

[Максим](https://t.me/Dark_Wing) (специалист административно-хозяйственного отдела) по техническим вопросам 

❗️Информация по поло (футболкам) - её можно получить у администратора в технопарке (под роспись)

Если у тебя остались какие-то вопросы - обязательно обращайся к координатору направления"""

greeting_message_3d = """*Привет!*

Сперва, пожалуйста, ознакомьтесь с правилами для преподавателей [здесь](https://docs.google.com/document/d/1QDtvCGgVD218Zp1ZEckbBWl3EPWYTjzF/edit), если ещё этого не сделали.

Также, пожалуйста, отметьте своё расписание в таблице занятости преподавателей [по ссылке](https://docs.google.com/spreadsheets/d/1DqZGlJ2-t154jqgP-03hbzzqbN70YYCZ/edit?gid=1096906622#gid=1096906622), чтобы получать актуальные запросы, подходящие Вашей занятости.

_Вся актуальная информация, связанная с работой на инженерном направлении выкладывается в чате «Инженерное направление»._

Чат состоит из нескольких тем:

*1. Важное*
Здесь выкладываются важные объявления для всех педагогов, связанные с проведением мероприятий, работой технопарков и школ, выплатой ЗП и тд.

*2. Запросы на преподавателей*
Здесь выкладываются все актуальные запросы, которые преподаватели могут взять. Внимательно следите за сообщениями в этой теме, чтобы не пропустить удобный курс.

*3. Поиск замены*
Если вы заболели, получили травму, у вас зачёт и тд, вы можете написать в этот раздел запрос на замену после согласования с координатором или руководителем. Другие преподаватели будут видеть ваш запрос и откликаться на него при возможности.

*4. Запросы на расходники*
Если к следующему занятию вам нужны: бумага, клей, сода, картошка, макетные платы, платы-микроконтроллеры, датчики, двигатели, 3D-ручки и прочие расходники, вы пишете запрос в эту тему, указывая точное количество на вашу группу, чтобы мы смогли вам всё заранее подготовить.

*5. Флуд*
Тематика не регламентирована, можно писать обо всём, модерация в этой теме не проводится.

‼️ *Несколько правил* ‼️

Все запросы от преподавателей и к преподавателям идут только через чат. Если вам нужна замена или расходники или, если вы хотите кого-то заменить, всё это необходимо отражать в чате.
Запрещается кого-либо оскорблять/задевать/унижать.

Вопросам поиска замены, доступа к методикам, обратной связи по ученикам можете писать [Дарье](https://t.me/pec4eenka).

По всем остальным вопросам пишите [Сергею](https://t.me/korolyov94).
"""

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

