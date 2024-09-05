import datetime as dt

import config
from crm import crm
from db import Teachers_database

# Инициализация данных CRM глобально
#: CRM = 
db = Teachers_database()
 
class Lesson():
    def __init__(self, data: dict, location: str):
        self.reminder_fail_head = None  # Идентификатор задачи для отмены сообщения
        self.reminder_fail_coordinator = None  
        self.reminder_fail_manager = None  
        self.presence_fail_head = None  
        self.presence_fail_coordinator = None  
        self.presence_fail_manager = None

        self.errors = []
        self.data = data

        # Используем глобальные переменные для инициализации атрибутов урока
        self.location = location
        self.location_type  = [k for k in config.locations_raw.keys() if data['room_id'] in config.locations_raw[k]][0]
        #print(self.location_type)

        self.classroom = self._get_classroom_name(data['room_id'])
        self.subject = self._get_subject_name(data['subject_id'])
        
        self.teacher_selected = False
        if data['teacher_ids'] == []:
            self.teacher_info = "Не указан педагог"
            self.errors.append("Не указан педагог")
        else:
            self.teacher_selected = True
            self.teacher_info = self._get_teacher_info(data['teacher_ids'][0])
            self.teacher_tg = db.get_teacher_by_crm_id(self.teacher_info.get('id', None))[2]
            #print(self.teacher_tg)
            if not self.teacher_tg:
                self.errors.append(f"Педагог не зарегистрирован в боте")
        
        self.teacher_tg = config.vlad # Убрать после теста 

        self.time_from = dt.datetime.strptime(data['time_from'], '%Y-%m-%d %H:%M:%S')
        self.time_to = dt.datetime.strptime(data['time_to'], '%Y-%m-%d %H:%M:%S')
        self.time = self.time_from.strftime('%H:%M')
        self.date = self.time_from.date()
        self.duration = self.get_duration()

        self.students_list_raw = crm.get_students_raw_info(data['customer_ids'])
        self.students_list = sorted([s['name'] for s in self.students_list_raw])
        self.students_selected = []

        self.theme = 'Не указана'
        if data['subject_id'] in config.it_subjects.keys():
            self.theme = 'IT'
            self.head_tg = config.tg_ids.head_it
            self.coordinator_tg = config.tg_ids.coordinator_it
            #Убрать после теста 
            #self.coordinator_tg = config.tg_ids.head_it
        else:
            self.theme = '3D'
            self.head_tg = config.tg_ids.head_3d
            self.coordinator_tg = config.tg_ids.coordinator_3d
            # потом убрать ниже
            #self.head_tg = config.tg_ids.head_it
            #self.coordinator_tg = config.tg_ids.head_it
         
        self.group_name = None
        self.group_id = data['group_ids'][0] if data['group_ids'] else None
        if self.group_id:
            group_info = crm.get_group_info(self.group_id)
            if group_info:
                self.group_name = group_info['name']
                self.group_link = f"[Группа в CRM](https://inginirium.s20.online/company/2/group/view?id={self.group_id})"

            else:
                self.errors.append(f"Неправильно заполнена группа")
                self.group_name = "No group"
        else:
            self.errors.append(f"Неправильно заполнена группа")
            self.group_name = "No group"
        
        if 'Менеджер школы:' in group_info['note']:
            self.location = config.transcript['schools']

        self.address = None
        self.manager_tg = None

        if self.location == config.transcript['schools']:
            try:
                raw_text = group_info['note'].split(f'|')
                self.address = raw_text[0]
                self.manager = raw_text[1]
                self.manager_tg = None
                for m in config.manager_transcript.keys():
                    if m in self.manager:
                        self.manager_tg = config.manager_transcript[m]
                        break
                #print(self.manager, self.manager_tg)
                self.classroom = raw_text[2]
            except:
                print(f'Нерпавильно заполнена группа {self.group_name}')

        self.lesson_theme = 'None'
        self.feedback = ''
        self.acceptable = len(self.errors) == 0
        #print(self.teacher_tg, self.head_tg, self.coordinator_tg, self.manager_tg)


    def _get_classroom_name(self, room_id: int) -> str:
        classroom = next((loc['name'] for loc in crm.locations if loc['id'] == room_id), "Unknown location")
        return classroom

    def _get_subject_name(self, subject_id: int) -> str:
        return crm.subjects.get(subject_id, "Unknown subject")

    def _get_teacher_info(self, teacher_id: int) -> dict:
        return next((teacher for teacher in crm.teachers if teacher['id'] == teacher_id), {"name": "Unknown teacher"})

    def get_duration(self) -> str:
        time_from_dt = self.time_from - dt.timedelta(seconds=1)
        duration_minutes = int((self.time_to - time_from_dt).total_seconds() / 60)

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
    
    def __str__(self):
        return (f"Lesson:\n"
                f"  Location: {self.location}\n"
                f"  Subject: {self.subject}\n"
                f"  Classroom: {self.classroom}\n"
                f"  Teacher: {self.teacher_info['name'] if self.teacher_selected else self.teacher_info }\n"
                f"  Time From: {self.time_from.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"  Time To: {self.time_to.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"  Time: {self.time}\n"
                f"  Duration: {self.duration}\n"
                #f"  Students (Raw): {self.students_list_raw}\n"
                f"  Students (Sorted): {', '.join(self.students_list)}\n"
                f"  Students (Selected): {', '.join(self.students_selected)}")

    def get_message_reminder(self) -> str:
        if self.location == config.transcript['schools']:
            address = self.address
            link = f"[{address}](https://yandex.ru/maps/?text={address.replace(' ', '%20')})"
            loc_info = f'{self.location}, {link}'
            message_text = config.reminder_message_text.format(loc_info, 
                                        self.classroom, self.subject,
                                        self.time, self.duration)
            return message_text
        
        message_text = config.reminder_message_text.format(
        self.location, self.classroom, self.subject,
        self.time, self.duration)
        return message_text

    def get_reminder_text(self) -> tuple:
        '''
        return message text for (head, coordinator)
        '''
        fio = self.teacher_info['name']
        if self.location != config.transcript['schools']:
            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {self.teacher_info['name']} будет завтра на занятии:\n"
                    f"Группа: {self.group_name}\n"
                    f"Время: {self.time}\n"
                    f"Аудитория: {self.classroom}"
                )
                return '', message_text
            else:
                message_text = (
                    f"Подтвердили участие в занятии по предмету {self.subject}:\n"
                    f"Преподаватель: {self.teacher_info['name']}\n"
                    f"Место: {self.location}, аудитория {self.classroom}\n"
                    f"Время: {self.time}"
                )
                return message_text, message_text
        else:
            address = self.address
            link = f"[{address}](https://yandex.ru/maps/?text={address.replace(' ', '%20')})"
            loc_info = f'{self.location}, {link}'

            message_text = (
                f"Подтвердили участие в занятии по предмету {self.subject}:\n"
                f"Преподаватель: {self.teacher_info['name']}\n"
                f"Адрес: {loc_info}\n"
                f"Аудитория: {self.classroom}\n"
                f"Время: {self.time}"
            )
            if self.theme == 'IT':
                return '', message_text
            return message_text, message_text
 
    def get_reminder_text_fail(self) -> tuple:
        '''
        return fail message text for (head, coordinator)
        '''
        fio = self.teacher_info['name']
        if self.location != config.transcript['schools']:
            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {fio} не подтвердил свое участие на занятии ❌❌❌, "
                    f"возможно, он пропустил сообщение, либо не может провести занятие в данное время ⁉️⁉️⁉️"
                )
                return message_text, message_text
            else:
                message_text = (
                    f"🆘Педагог {fio}, не отвечает на подтверждение {self.subject}\n"
                    f"{self.location} {self.classroom}, время {self.time}"
                )
                return message_text, message_text
        else:
            address = self.address
            link = f"[{address}](https://yandex.ru/maps/?text={address.replace(' ', '%20')})"
            loc_info = f'{self.location}, {link}'

            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {fio} не подтвердил свое участие на занятии ❌❌❌, "
                    f"возможно, он пропустил сообщение, либо не может провести занятие в данное время ⁉️⁉️⁉️"
                )
                return message_text, message_text
            else:
                message_text = (
                    f"🆘Педагог {fio}, не отвечает на подтверждение {self.subject}\n"
                    f"Адрес: {loc_info}, Аудитория: {self.classroom}, время {self.time}"
                )
                return message_text, message_text

    def get_presence_text(self) -> tuple:
        '''
        Преподаватель подтвердил за 5 минут до занятия
        '''
        fio = self.teacher_info['name']
        if self.location == config.transcript['schools']:
            address = self.address
            link = f"[{address}](https://yandex.ru/maps/?text={address.replace(' ', '%20')})"
            loc_info = f'{self.location}, {link}'
            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {fio} на месте.\n"
                    f"Название группы: {self.group_name}\n"
                    f"Адрес: {loc_info}\n"
                    f"Время: {self.time}"
                )
                return '', message_text           
            else:
                message_text = (
                    f"Преподаватель на месте.\n"
                    f"ФИО: {fio}\n"
                    f"Группа: {self.group_name}\n"
                    f"Предмет: {self.subject}\n"
                    f"Адрес: {loc_info}\n"
                    f"Время: {self.time}"
                )
                return message_text, message_text
        else:
            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {fio} на месте.\n"
                    f"Группа: {self.group_name}\n"
                    f"Время: {self.time}\n"
                    f"Аудитория: {self.classroom}\n"
                    f"Тема: {self.lesson_theme}"
                )
                return '', message_text
            else:
                message_text = (
                    f"Преподаватель на месте.\n"
                    f"ФИО: {fio}\n"
                    f"Предмет: {self.subject}\n"
                    f"Место: {self.location}\n"
                    f"Аудитория: {self.classroom}\n"
                    f"Время: {self.time}\n"
                    f"Тема: {self.lesson_theme}"
                )
                return message_text, message_text
    
    def get_presence_text_fail(self) -> tuple:
        '''
        Преподаватель не на месте
        '''
        fio = self.teacher_info['name']
        if self.location == config.transcript['schools']:
            address = self.address
            link = f"[{address}](https://yandex.ru/maps/?text={address.replace(' ', '%20')})"
            loc_info = f'{self.location}, {link}'

            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {fio} не на месте. 🆘🆘🆘\n"
                    f"Необходимо срочно связаться с администратором и преподавателем ‼️"
                )
                return message_text, message_text           
            else:
                message_text = (
                    f"🆘\n"
                    f"Педагога {fio}, нет на месте.\n"
                    f"Предмет: {self.subject}\n"
                    f"Адрес: {loc_info}, Аудитория: {self.classroom}, время {self.time}\n"
                    f"Необходимо срочно связаться с администратором и преподавателем ❗️❗️❗️"
                )
                return message_text, message_text
        else:
            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {fio} не на месте. 🆘🆘🆘\n"
                    f"Необходимо срочно связаться с администратором и преподавателем ‼️"
                )
                return message_text, message_text
            else:
                message_text = (
                    f"🆘\n"
                    f"Педагога {fio}, нет на месте.\n"
                    f"Предмет: {self.subject}\n"
                    f"Место: {self.location}, Аудитория: {self.classroom}, время {self.time}\n"
                    f"Необходимо срочно связаться с администратором и преподавателем ❗️❗️❗️"
                )
                return message_text, message_text    

    def get_attendance_text(self) -> str:
        '''
        Преподаватель отмечает учеников
        '''
        address = self.address
        link = f"[{address}](https://yandex.ru/maps/?text={address.replace(' ', '%20')})"
        loc_info = f'{self.location}, {link}'
        if self.theme == 'IT':
            message_text = (
                f"Наименование группы: {self.group_name}\n"
                f"Время: {self.time}\n"
                f"Дата: {self.date}\n"
                f"1. Тема занятия: {self.lesson_theme}\n"
                f"Ученики: \n{'\n'.join(self.students_list)}\n"
                f"{self.group_link}"
            )
            return '', message_text

        else:
            message_text = (
                f"Посещаемость: {loc_info}\n"
                f"Предмет: {self.subject}\n"
                f"Время: {self.time}\n"
                f"Дата: {self.date}\n"
                f"Тема: {self.lesson_theme}\n"
                f"Ученики: \n{'\n'.join(self.students_list)}\n"
                f"{self.group_link}"
            )
            return message_text, message_text
        
    def get_feedback_text(self) -> str:
        '''
        Преподаватель отправил обратную связь после занятия
        '''
        if self.theme == 'IT':
            message_text = (
                f"Группа: {self.group_name}\n"
                f"Предмет: {self.subject}\n"
                f"Время: {self.time}\n"
                f"Обратная связь: {self.feedback}"
            )
            return '', message_text

        else:
            message_text = (
                f"Обратная связь по группе: {self.group_name}\n"
                f"Время: {self.time}\n"
                f"Предмет: {self.subject}\n"
                f"Обратная связь: {self.feedback}"
            )
            return message_text, message_text