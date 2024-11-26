import json
import requests
import datetime as dt
from typing import List, Dict, Optional

from config import CRM_CREDENTIALS, locations_raw
class CRM:
    """
    An interacting with AlphaCRM (Inginirium)
    """
    def __init__(self, host="inginirium.s20.online") -> None:
        self.host = host
        self.token = None
        self.subjects = None
        self.locations = None
        self.teachers = None
        self.teachers_raw = None
        self.auth()
        self.update_data()  # Инициализация данных при создании экземпляра класса

    def auth(self) -> None:

        response = requests.post(
            f"https://{self.host}/v2api/auth/login",
            data=json.dumps(CRM_CREDENTIALS)
        )
        response.raise_for_status()  # Проверка на ошибки запроса
        answer = response.json()
        self.token = answer.get("token")  # Сохранение токена для дальнейших запросов

    def update_data(self) -> None:
        """Обновление данных из CRM."""
        self.subjects = self.get_subject_map()
        self.locations = self.get_locations_name()
        self.teachers = self.get_teacher_info()
        self.teachers_raw = {i['name']:i['id'] for i in self.teachers}

    def get_group_info(self, id: int) -> Optional[Dict]:
        """
        Getting group info from CRM by its id

        Params:
        :id: group id
        """
        response = requests.post(
            f"https://{self.host}/v2api/2/group/index",
            headers={"X-ALFACRM-TOKEN": self.token},
            data=json.dumps({
                "is_active": 1,
                "page": 0,
                "pageSize": 100,
                "status": "1",
                "id": id
        }))
        if response:
            answer = response.json()
            items = answer.get("items")
            if items:
                return items[0]
            return None
        return None
    
    def get_subject_map(self) -> Optional[Dict]:
        response = requests.post(
            f"https://{self.host}/v2api/2/subject/index",
            headers={"X-ALFACRM-TOKEN": self.token}
        )
        if response:
            answer = response.json()
            data = answer.get("items", [])
            subject_map = {item["id"]: item["name"] for item in data}
            return subject_map
        return []

    def get_groups_by_date(self,
                           start_dt: str,
                           end_dt: str,
                           status: int = 1,
                           page: int = 0,
                          ) -> List[Dict]:
        """
        Getting the closest group by time
        Date format: `dd.mm.yyyy`

        Params:
        :start_dt: start date in date format
        :end_dt: end date in date format
        :status: 1 - запланированный,
                 2 - отмененный,
                 3 - проведенный
        """
        response = requests.post(
            f"https://{self.host}/v2api/2/lesson/index",
            headers={"X-ALFACRM-TOKEN": self.token},
            data=json.dumps({
                "is_active": 1,
                "page": page,
                "pageSize": 100,
                "date_from": start_dt,
                "date_to": end_dt,
                "status":f"{status}"
        }))
        if response:
            answer = response.json()
            return answer.get("items", [])
        return []

    def get_slots_info_by_date(self, date:str, status:int = 1) -> Dict[str, List[Dict]]:
        """
        Getting the closest group by time
        Date format: `dd.mm.yyyy`

        Params:
        :start_dt: start date in date format
        :end_dt: end date in date format
        :status: 1 - запланированный,
                 2 - отмененный,
                 3 - проведенный
        rooms = {# config for room_id
        'schools': {177, None}, 
        'tp': {201, 232, 233, 234, 183, 184, 41, 42, 2, 3, 4, 40, 190},
        'water': {202, 169, 170, 171},
        'odin': {202, 169, 170, 171},
        }
        data_whitelist = [
            'status', 
            'subject_id',
            'lesson_type_id',
            'room_id',
            'date',
            'time_from',
            'time_to',
            'group_ids',
            'customer_ids',
            'teacher_ids',
        ]
        data_keys = [
            'id', 
            'streaming', 
            'details', 
            'status', 
            'custom_break_time', 
            'room_id', 
            'subject_id', 
            'time_from', 
            'group_ids', 
            'customer_ids', 
            'time_to', 
            'lesson_date', 
            'topic', 
            'teacher_ids', 
            'note', 
            'homework', 
            'lesson_type_id', 
            'branch_id'
        ]
        """
        rooms = locations_raw # config for room_id
        data_whitelist = [
            'status',
            'subject_id',
            'lesson_type_id',
            'room_id',
            'time_from',
            'time_to',
            'group_ids',
            'customer_ids',
            'teacher_ids',
            'note'
        ]
        
        date_start, date_end = date, date
        data = self.get_groups_by_date(date_start, date_end, status=status)
        res = {i: [] for i in rooms.keys()}

        for slot in data:
            room_id = slot['room_id']
            for type in rooms:
                if room_id in rooms[type]:
                    new_slot = {}
                    for key in data_whitelist:
                        try:
                            new_slot[key] = slot[key]
                        except Exception as e:
                            print(f'Нет параметра {key}, \n{e}\n{slot}')
                    res[type].append(new_slot)
        return res

    def get_teacher_info(self) -> List[Dict]:
            """
            Getting list of teachers

            Params:
            :page: number of the page
            """
            response = requests.post(
                f"https://{self.host}/v2api/2/teacher/index",
                headers={"X-ALFACRM-TOKEN": self.token},
                data=json.dumps({
                    "pageSize": 500,
            }))
            if response:
                answer = response.json()
                return answer.get("items", [])
            return []
    
    def get_student_ids(self, id: int) -> List[Dict]:
            """
            Getting indexes of student from specific group

            Params:
            :id: group id
            """
            response = requests.post(
                f"https://{self.host}/v2api/2/cgi/index?group_id={id}",
                headers={"X-ALFACRM-TOKEN": self.token},
                data=json.dumps({
                    "is_active": 1,
                    "page": 0,
                    "pageSize": 100
            }))
            if response:
                answer = response.json()
                return answer.get("items", [])
            return []
    
    def get_students(self, ids: List[int]) -> List[Dict]:
            """
            Getting information about student by their indexes in CRM
            """

            now = dt.datetime.now()
            date_format = "%d.%m.%Y"
            student_ids = [st["customer_id"] for st in ids
                        if  len(st["e_date"]) == 0 or
                        now < dt.datetime.strptime(st["e_date"], date_format)]
            if len(student_ids) == 0:
                return []

            response = requests.post(
                f"https://{self.host}/v2api/2/customer/index",
                headers={"X-ALFACRM-TOKEN": self.token},
                data=json.dumps({
                    "id": student_ids,
                    "pageSize": 100,
            }))
            if response:
                answer = response.json()
                return answer.get("items", [])
            return []

    def get_students_raw_info(self, ids:List[int]) -> List[Dict]:
            #student_ids = [st["customer_id"] for st in ids]
            response = requests.post(
                f"https://{self.host}/v2api/2/customer/index",
                headers={"X-ALFACRM-TOKEN": self.token},
                data=json.dumps({
                    "id": ids,
                    "pageSize": 500,
            }))
            if response:
                answer = response.json()
                return answer.get("items", [])
            return []

    def get_locations_name(self) -> List[Dict]:
            response = requests.post(
                f"https://{self.host}/v2api/2/room/index",
                headers={"X-ALFACRM-TOKEN": self.token},
                data=json.dumps({
                    "pageSize": 100,
            }))
            if response:
                answer = response.json()
                return answer.get("items", [])
            return []
