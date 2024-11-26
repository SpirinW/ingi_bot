import sqlite3
from typing import Optional, Tuple, List

class TeachersDatabase:
    def __init__(self, db_path='database.db') -> None:
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self) -> None:
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers(
                name TEXT,
                crm_id INTEGER,
                tg_id INTEGER UNIQUE,
                phone TEXT
            )
        ''') 
        self.conn.commit()

    def add_teacher(self, name: str, crm_id: int, tg_id: int, phone: str) -> bool:
        # Проверка на наличие преподавателя по tg_id
        if self.get_teacher_by_tg_id(tg_id) is None:
            self.cursor.execute('''
                INSERT INTO teachers (name, crm_id, tg_id, phone) 
                VALUES (?, ?, ?, ?)
            ''', (name, crm_id, tg_id, phone))
            self.conn.commit()
            return True
        else:
            return False

    def get_teacher_by_crm_id(self, crm_id: int) -> Optional[Tuple[str, int, int, str]]:
        self.cursor.execute('''
            SELECT * FROM teachers WHERE crm_id = ?
        ''', (crm_id,))
        return self.cursor.fetchone()

    def get_teacher_by_tg_id(self, tg_id: int) -> Optional[Tuple[str, int, int, str]]:
        self.cursor.execute('''
            SELECT * FROM teachers WHERE tg_id = ?
        ''', (tg_id,))
        return self.cursor.fetchone()

    def get_teacher_by_phone(self, phone: str) -> Optional[Tuple[str, int, int, str]]:
        self.cursor.execute('''
            SELECT * FROM teachers WHERE phone = ?
        ''', (phone,))
        return self.cursor.fetchone()

    def fetch_teachers(self) -> List[Tuple[str, int, int, str]]:
        self.cursor.execute('select * from teachers')
        return self.cursor.fetchall()

    def delete_teacher_by_crm_id(self, crm_id: int) -> None:
        self.cursor.execute('''
            DELETE FROM teachers WHERE crm_id = ?
        ''', (crm_id,))
        self.conn.commit()
    
    def close(self) -> None:
        self.conn.close()

