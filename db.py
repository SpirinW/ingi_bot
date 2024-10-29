import sqlite3
 
class Teachers_database:
    def __init__(self, db_path='database.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers(
                name TEXT,
                crm_id INTEGER,
                tg_id INTEGER UNIQUE,
                phone TEXT
            )
        ''') 
        self.conn.commit()

    def add_teacher(self, name: str, crm_id: int, tg_id: int, phone: str):
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

    def get_teacher_by_crm_id(self, crm_id: int):
        self.cursor.execute('''
            SELECT * FROM teachers WHERE crm_id = ?
        ''', (crm_id,))
        return self.cursor.fetchone()

    def get_teacher_by_tg_id(self, tg_id: int):
        self.cursor.execute('''
            SELECT * FROM teachers WHERE tg_id = ?
        ''', (tg_id,))
        return self.cursor.fetchone()

    def get_teacher_by_phone(self, phone: str):
        self.cursor.execute('''
            SELECT * FROM teachers WHERE phone = ?
        ''', (phone,))
        return self.cursor.fetchone()

    def fetch_teachers(self):
        self.cursor.execute('select * from teachers')
        return self.cursor.fetchall()

    def delete_teacher_by_crm_id(self, crm_id: int):
        self.cursor.execute('''
            DELETE FROM teachers WHERE crm_id = ?
        ''', (crm_id,))
        self.conn.commit()
    
    def close(self):
        self.conn.close()

# Подключение к базе данных SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
# Создание таблицы для хранения запланированных сообщений
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scheduled_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        crm_id TEXT,
        message TEXT,
        send_time TEXT,
        job_id TEXT
    )
''')
conn.commit()

def add_scheduled_message(user_id, message, send_time, job_id):
    cursor.execute('''
        INSERT INTO scheduled_messages (user_id, message, send_time, job_id)
        VALUES (?, ?, ?, ?)
    ''', (user_id, message, send_time, job_id))
    conn.commit()

def remove_scheduled_message(job_id):
    cursor.execute('DELETE FROM scheduled_messages WHERE id = ?', (job_id,))
    conn.commit()

def get_scheduled_messages():
    cursor.execute('SELECT * FROM scheduled_messages WHERE send_time <= datetime("now")')
    return cursor.fetchall()
