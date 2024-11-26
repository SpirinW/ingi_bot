import datetime as dt
from geopy.geocoders import Nominatim

import config
import raw_texts
from config import do_it_head_notifications
from crm import CRM
from db import TeachersDatabase
import re
from typing import Optional, Tuple, List, Dict
# Инициализация данных CRM глобально
#: CRM = 
db = TeachersDatabase()



class Lesson():
    
    def __init__(self) -> None:
        self.reminder_fail_head = None  # Идентификатор задачи для отмены сообщения
        self.reminder_fail_coordinator = None  
        self.reminder_fail_manager = None  
        self.presence_fail_head = None  
        self.presence_fail_coordinator = None  
        self.presence_fail_manager = None

        self.errors = []


        self.lesson_type_id = None
        self.group_type = None
        
        self.teacher_selected = False

        self.address = None
        self.manager_tg = None

        self.lesson_theme = 'None'
        self.feedback = ''
        self.group_name = None

    @staticmethod
    def escape_markdown(text: str, version: str = "MarkdownV1") -> str:
        """
        Экранирует специальные символы для Markdown или MarkdownV2.
        """
        if version == "MarkdownV2":
            escape_chars = r"_|*[]()~`>#+-=|{}.!"
        else:
            escape_chars = r"_*[]()"
        return re.sub(rf"([{re.escape(escape_chars)}])", r"\\\1", text)

    @staticmethod
    def get_coordinates_from_address(address: str) -> tuple[float, float]:
        """Получить координаты из адреса."""
        geolocator = Nominatim(user_agent="Ingi Telegram")
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        return None, None

    @staticmethod
    def create_yandex_maps_link(address: str) -> str:
        """Создать ссылку для Яндекс.Карт с координатами, если они есть."""
        latitude, longitude = Lesson.get_coordinates_from_address(address)
        if latitude and longitude:
            return f"https://yandex.ru/maps/?ll={longitude},{latitude}&z=16"
        return f"https://yandex.ru/maps/?text={address.replace(' ', '+')}"  # Заменяем пробелы на '+' для лучшей работы на телефонах
    
    def parse_data(self, data: dict, location: str, crm: CRM) -> None:
        

        self.data = data

        self.location = location
        #self.location_type  = [k for k in config.locations_raw.keys() if data['room_id'] in config.locations_raw[k]][0]
        self.location_type = next((k for k, v in config.locations_raw.items() if data['room_id'] in v), None)
        

        if self.data['lesson_type_id'] == 1:
            self.lesson_type_id = 'private'
            if self.data['room_id'] == 182:
                self.group_type = 'web'
            else:
                self.group_type = 'tp'

        elif self.data['lesson_type_id'] == 3:
            self.lesson_type_id = 'interview'
            if self.data['room_id'] == 182:
                self.group_type = 'web'
            else:
                self.group_type = 'tp'

        elif self.data['lesson_type_id'] in {4, 5, 6, 7, 15}:
            self.lesson_type_id = 'group'
            if self.data['room_id'] == 182:
                self.group_type = 'web'
            else:
                self.group_type = 'school'

        elif self.data['lesson_type_id'] in range(2, 18) and self.data['lesson_type_id'] not in {4, 5, 6, 7, 15, 3}:
            self.lesson_type_id = 'group'
            if self.data['room_id'] == 182:
                self.group_type = 'web'
            else:
                self.group_type = 'tp'
        
        self.classroom = self._get_classroom_name(data['room_id'], crm)
        self.subject = self._get_subject_name(data['subject_id'], crm)
        
        if data['teacher_ids'] == []:
            self.teacher_info = "Не указан педагог"
            self.errors.append("Не указан педагог")
        else:
            self.teacher_selected = True
            self.teacher_info = self._get_teacher_info(data['teacher_ids'][0], crm)
            self.teacher_tg = db.get_teacher_by_crm_id(self.teacher_info.get('id', None))[2]
            self.teacher_fio = self.teacher_info['name']

            if not self.teacher_tg:
                self.errors.append(f"Педагог не зарегистрирован в боте")
        #Тестирование бота
        if config.test_mode:
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
            self.head_tg = config.TgIds.head_it
            self.coordinator_tg = config.TgIds.coordinator_it
            #Убрать после теста 
            #self.coordinator_tg = config.TgIds.head_it
        elif data['subject_id'] in config.robo_3d_subjects.keys():
            self.theme = '3D'
            self.head_tg = config.TgIds.head_3d
            self.coordinator_tg = config.TgIds.coordinator_3d
            # потом убрать ниже
            #self.head_tg = config.TgIds.head_it
            #self.coordinator_tg = config.TgIds.head_it
        else:
            self.errors.append(f'Предмета нет в БД для ИТ и 3D {data}')


        if self.lesson_type_id == 'group':
            self.group_name = data.get('group_name', 'Групповое занятие')
        elif self.lesson_type_id == 'private':
            student_name = ', '.join(self.students_list) if self.students_list else "Ученик не указан"
            self.group_name = f"Индивидуальное занятие с {student_name}"
        elif self.lesson_type_id == 'interview':
            student_name = ', '.join(self.students_list) if self.students_list else "Ученик не указан"
            self.group_name = f"Собеседование с {student_name}"
        elif self.location == 'web':
            self.group_name = f"Вебинар по ссылке"
        else:
            self.group_name = "Занятие без группы"
        

        if self.lesson_type_id == 'group':
            self._get_group_data(data, crm)
        elif self.lesson_type_id == 'private':
            self._get_private_data(data)
        

        
        self.acceptable = len(self.errors) == 0

    def _get_private_data(self, data) -> None:
        self.group_name = "Индивидуальное занятие"
        self.group_id = None
        self.address = "Вебинар" if self.location == 'web' else "Не указано"  # Обновлено для типа 'web'
        self.loc_info = f'{self.location}, [Ссылка на Вебинар]({data['note']})'

    def _get_group_data(self, data, crm: CRM) -> None:
        self.group_id = data['group_ids'][0] if data['group_ids'] else None
        if self.group_id:
            group_info = crm.get_group_info(self.group_id)
            if group_info:
                self.group_name = Lesson.escape_markdown(group_info['name'])
                self.group_link = f"[Группа в CRM](https://inginirium.s20.online/company/2/group/view?id={self.group_id})"

            else:
                self.errors.append(f"Неправильно заполнена группа")
                self.group_name = "No group"
        else:
            self.errors.append(f"Неправильно заполнена группа")
            self.group_name = "No group"
    
        if 'Менеджер школы:' in group_info['note']:
            self.location = config.transcript['schools']
            self.group_type = 'school'

        if self.group_type == 'school':
            try:
                raw_text = group_info['note'].split(f'|')
                self.address = raw_text[0]
                self.manager = raw_text[1]
                self.manager_tg = None
                for m in config.manager_transcript.keys():
                    if m in self.manager:
                        self.manager_tg = config.manager_transcript[m]
                        break
                self.classroom = raw_text[2]
                link = Lesson.create_yandex_maps_link(self.address)  # Используем новую функцию для создания ссылки
                self.loc_info = f'{self.location}, [{self.address}]({link})'
            except:
                print(f'Нерпавильно заполнена группа {self.group_name}')

    @staticmethod
    def _get_classroom_name(room_id: int, crm:CRM) -> str:
        classroom = next((loc['name'] for loc in crm.locations if loc['id'] == room_id), "Unknown location")
        return classroom

    @staticmethod
    def _get_subject_name(subject_id: int, crm:CRM) -> str:
        return crm.subjects.get(subject_id, "Unknown subject")
    
    @staticmethod
    def _get_teacher_info(teacher_id: int, crm:CRM) -> dict:
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
    
    def __str__(self) -> str:
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
        student_names = ', '.join(self.students_list) if self.students_list else "Ученик не указан"
        #print(self.lesson_type_id, self.location)
        self.loc_info = getattr(self, 'loc_info', self.location)
        if self.lesson_type_id == 'private' and self.group_type == 'tp':
            # Индивидуальное занятие
            message_text = (
                f"Привет!\nНапоминаю тебе о завтрашнем индивидуальном занятии:\n"
                f"Ученик: {student_names}\n"
                f"Предмет: {self.subject}\nАудитория: {self.classroom}\nВремя: {self.time}\nДлительность: {self.duration}\n"
                f"Пожалуйста, подтверди готовность!👇"
            )
        elif self.lesson_type_id in ('private', 'interview') and self.group_type == 'web':
            # Вебинар
            webinar_link = self.data.get('note', None)
            if webinar_link != '':
                webinar_link = f"[Ссылка]({webinar_link}) на вебинар"
            else: 
                webinar_link = f'Ссылка на вебинар не указана в срм, обратись к [администратору](https://t.me/inginirium_adminn)'
            message_text = (
                f"Привет!\nНапоминаю тебе о завтрашнем вебинаре:\n"
                f"Ученик: {student_names}\n"
                f"Предмет: {self.subject}\nВремя: {self.time}\n{webinar_link}\n"
                f"Пожалуйста, подтверди готовность!👇"
            )
        elif self.lesson_type_id == 'interview':
            # Собеседование
            message_text = (
                f"Привет!\nНапоминаю тебе о завтрашнем собеседовании с:\n"
                f"Ученик: {student_names}\n"
                f"Предмет: {self.subject}\nАудитория: {self.classroom}\nВремя: {self.time}\n"
                f"Пожалуйста, подтверди готовность!👇"
            )
        elif self.lesson_type_id == 'group' and self.group_type == 'web':
            webinar_link = self.data.get('note', None)
            if webinar_link != '':
                webinar_link = f"[Ссылка]({webinar_link}) на вебинар"
            else: 
                webinar_link = f'Ссылка на вебинар не указана в срм, обратись к [администратору](https://t.me/inginirium_adminn)'
            message_text = (
                f"Привет!\nНапоминаю тебе о завтрашнем вебинаре:\n"
                f"Предмет: {self.subject}\nВремя: {self.time}\n{webinar_link}\n"
                f"Пожалуйста, подтверди готовность!👇"
            )
        
        else:
            # Групповое занятие
            message_text = raw_texts.reminder_message_text.format(
                self.loc_info if self.location == config.transcript['schools'] else self.location,
                self.classroom, self.subject, self.time, self.duration
            )
        
        return message_text



    def get_reminder_text(self) -> Tuple[str, str]:
        """
        Текст напоминания о предстоящем занятии для куратора.
        """
        student_names = ', '.join(self.students_list) if self.students_list else "Ученик не указан"
        
        if self.lesson_type_id == 'group':
            # Групповое занятие
            message_text = (
                f"🟡Подтвердили участие в занятии по предмету {self.subject}:\n"
                f"Преподаватель: {self.teacher_fio}\n"
                f"Группа: {self.group_name}\n"#.replace('_', '\\_')
                f"Место: {self.location}, аудитория {self.classroom}\n"
                f"Время: {self.time}\n"
                f"Дата: {self.date}"

            )
        elif self.lesson_type_id == 'private':
            # Индивидуальное занятие
            message_text = (
                f"Подтвердили участие в индивидуальном занятии:\n"
                f"Преподаватель: {self.teacher_fio}\n"
                f"Ученик: {student_names}\n"
                f"Предмет: {self.subject}\n"
                f"Место: {self.location}, аудитория {self.classroom}\n"
                f"Время: {self.time}"
            )
        elif self.lesson_type_id == 'interview':
            # Собеседование
            message_text = (
                f"Подтвердили участие в собеседовании:\n"
                f"Преподаватель: {self.teacher_fio}\n"
                f"Ученик: {student_names}\n"
                f"Предмет: {self.subject}\n"
                f"Время: {self.time}"
            )
        else:
            # Обработка остальных типов занятий, если необходимо
            message_text = (
                f"Подтвердили участие в занятии по предмету {self.subject}:\n"
                f"Преподаватель: {self.teacher_fio}\n"
                f"Место: {self.location}, аудитория {self.classroom}\n"
                f"Время: {self.time}\n"
            )
        if not do_it_head_notifications:
            return '', message_text 
        return message_text, message_text
 
    def get_reminder_text_fail(self) -> Tuple[str, str]:
        '''
        return fail message text for (head, coordinator)
        '''
        if self.location != config.transcript['schools']:
            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {self.teacher_fio} не подтвердил свое участие на занятии ❌❌❌, "
                    f"возможно, он пропустил сообщение, либо не может провести занятие в данное время ⁉️⁉️⁉️"
                )
            else:
                message_text = (
                    f"🆘Педагог {self.teacher_fio}, не отвечает на подтверждение {self.subject}\n"
                    f"{self.location} {self.classroom}, время {self.time}"
                )
        else:

            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {self.teacher_fio} не подтвердил свое участие на занятии ❌❌❌, "
                    f"возможно, он пропустил сообщение, либо не может провести занятие в данное время ⁉️⁉️⁉️"
                )
            else:
                message_text = (
                    f"🆘Педагог {self.teacher_fio}, не отвечает на подтверждение {self.subject}\n"
                    f"Адрес: {self.loc_info}, Аудитория: {self.classroom}, время {self.time}"
                )
        if not do_it_head_notifications:
            return '', message_text 
        return message_text, message_text
    
    def get_presence_text(self) -> Tuple[str, str]:
        """
        Преподаватель подтвердил за 5 минут до занятия.
        """
        student_names = ', '.join(self.students_list) if self.students_list else "Ученик не указан"
        
        if self.location == config.transcript['schools']:
            if self.lesson_type_id == 'group':
                message_text = (
                    f"Преподаватель на месте.\n"
                    f"ФИО: {self.teacher_fio}\n"
                    f"Группа: {self.group_name.replace('_', '\\_')}\n"
                    f"Предмет: {self.subject}\n"
                    f"Адрес: {self.loc_info}\n"
                    f"Время: {self.time}"
                )
            else:
                message_text = (
                    f"Преподаватель на месте.\n"
                    f"ФИО: {self.teacher_fio}\n"
                    f"Ученик: {student_names}\n"
                    f"Предмет: {self.subject}\n"
                    f"Адрес: {self.loc_info}\n"
                    f"Время: {self.time}"
                )
        else:
            if self.lesson_type_id == 'group':
                message_text = (
                    f"Преподаватель на месте.\n"
                    f"ФИО: {self.teacher_fio}\n"
                    f"Группа: {self.group_name.replace('_', '\\_')}\n"
                    f"Предмет: {self.subject}\n"
                    f"Место: {self.location}\n"
                    f"Аудитория: {self.classroom}\n"
                    f"Время: {self.time}\n"
                    f"Тема: {self.lesson_theme}"
                )
            
            else:
                message_text = (
                    f"Преподаватель на месте.\n"
                    f"ФИО: {self.teacher_fio}\n"
                    f"Ученик: {student_names}\n"
                    f"Предмет: {self.subject}\n"
                    f"Место: {self.location}\n"
                    f"Аудитория: {self.classroom}\n"
                    f"Время: {self.time}\n"
                    f"Тема: {self.lesson_theme}"
                )

        if not do_it_head_notifications:
            return '', message_text 
        return message_text, message_text
    
 
    def get_presence_text_fail(self) -> Tuple[str, str]:
        '''
        Преподаватель не на месте
        '''
        if self.location == config.transcript['schools']:
        

            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {self.teacher_fio} не на месте. 🆘🆘🆘\n"
                    f"Необходимо срочно связаться с администратором и преподавателем ‼️"
                )
            else:
                message_text = (
                    f"🆘\n"
                    f"Педагога {self.teacher_fio}, нет на месте.\n"
                    f"Предмет: {self.subject}\n"
                    f"Адрес: {self.loc_info}, Аудитория: {self.classroom}, время {self.time}\n"
                    f"Необходимо срочно связаться с администратором и преподавателем ❗️❗️❗️"
                )
        else:
            if self.theme == 'IT':
                message_text = (
                    f"Преподаватель {self.teacher_fio} не на месте. 🆘🆘🆘\n"
                    f"Необходимо срочно связаться с администратором и преподавателем ‼️"
                )
            else:
                message_text = (
                    f"🆘\n"
                    f"Педагога {self.teacher_fio}, нет на месте.\n"
                    f"Предмет: {self.subject}\n"
                    f"Место: {self.location}, Аудитория: {self.classroom}, время {self.time}\n"
                    f"Необходимо срочно связаться с администратором и преподавателем ❗️❗️❗️"
                )
        return message_text, message_text    

    def get_attendance_text(self) -> Tuple[str, str]: 
        '''
        Преподаватель отмечает учеников
        '''
        if self.theme == 'IT':
            message_text = (
                f"🟢Наименование группы: {self.group_name}\n"
                f"Преподаватель: {self.teacher_fio}\n"
                f"Время: {self.time}\n"
                f"Дата: {self.date}\n"
                f"1. Тема занятия: {self.lesson_theme}\n"
                f"Ученики: \n{'\n'.join(self.students_selected)}\n"
                f"{self.group_link}"
            )

        else:
            message_text = (
                f"🟢Наименование группы: {self.group_name}\n"
                f"Посещаемость: {self.loc_info}\n"
                f"Преподаватель: {self.teacher_fio}\n"
                f"Предмет: {self.subject}\n"
                f"Время: {self.time}\n"
                f"Дата: {self.date}\n"
                f"Тема: {self.lesson_theme}\n"
                f"Ученики: \n{'\n'.join(self.students_selected)}\n"
                f"{self.group_link}"
            )
        if not do_it_head_notifications:
            return '', message_text 
        return message_text, message_text

    def get_feedback_text(self) -> Tuple[str, str]:
        '''
        Преподаватель отправил обратную связь после занятия
        '''
        if self.theme == 'IT':
            message_text = (
                f"🟣Группа: {self.group_name.replace('_', '\\_')}\n"
                f"Предмет: {self.subject}\n"
                f"Время: {self.time}\n"
                f"Обратная связь: {self.feedback}"
            )

        else:
            message_text = (
                f"🟣Обратная связь по группе: {self.group_name}\n"
                f"Время: {self.time}\n"
                f"Предмет: {self.subject}\n"
                f"Обратная связь: {self.feedback}"
            )
        return message_text, message_text