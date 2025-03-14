check_mark = '✅'
reminder_message_text = (
    "Привет!\nНапоминаю тебе о завтрашнем занятии:\nМесто: {}\nАудитория: {}\n"
    "Предмет: {}\nВремя: {}\nДлительность(в часах): {}\n"
    "Обязательно дай нам знать что ты готов👇"
)
button_reminder_check = "Прочитал, на занятии буду"

presence_message_text = "Твое занятие вот-вот начнется... \nТы на месте? Ответь внизу👇"
presence_message_check = "Я на месте!"

lesson_theme_request_text = "Супер. Отправь следующием сообщением тему занятия + описание (2-3 предложения)"

attendance_message_text = (
    "Отлично. скажи когда будешь готов отмечать детей👇"
)
attendance_message_load = (
    "Отметь детей ниже, просто выбери всех, кто присутствует.\n"
    "Если кого-то нет в списке, напиши об этом своему координатору\n"
    "Когда будешь готов, нажми на кнопку 'Готово'"
)
attendance_message_check = "Я готов отмечать"
attendance_message_coordinator = (
    "Посещаемость в {} по предмету {}, время {}\nТема {}\n{}"
)

message_last_tp = "Всех отметили, я отправлю данные администратору, а тебе хорошего занятия!"
message_last_school = (
    "Всех отметили, я отправлю данные администратору, а тебе хорошего занятия! "
    "Если кто-то дойдёт позже, то ты сможешь отметить его уже после занятия, я тебе напишу)"
)

message_feedback_request_text = (
    "Кстати. Ты можешь отправить обратную свзяь по занятию.\n"
    "Сообщить о проблемах в оборудовании/детях(опоздали, забыл отметить)/забыл отметить и т.д.\n"
    "Нужна ли обратная связь?👇"
)
message_feedback_yes = (
    "Хорошо. Отправь следующим сообщением обратную связь, я передам ее координатору направления"
)
message_feedback_last = "Хорошего тебе дня!"

feedback_template = (
    "Если на занятии возникали проблемы с определенным учеником (или учениками), "
    "ты можешь написать здесь его ФИО и конкретные кейсы на занятии. Например: ФИО отвлекал всех "
    "на занятии, кричал, на замечания никак не реагировал)"
)


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