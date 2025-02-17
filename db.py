from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional, Tuple, List

Base = declarative_base()

class Teacher(Base):
    __tablename__ = 'teachers'
    
    name = Column(String)
    crm_id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    phone = Column(String)

class TeachersDatabase:
    def __init__(self, db_path='sqlite:///database.db') -> None:
        self.engine = create_engine(db_path, echo=True)
        Base.metadata.create_all(self.engine)  
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_teacher(self, name: str, crm_id: int, tg_id: int, phone: str) -> bool:
        if self.get_teacher_by_tg_id(tg_id) is None:
            new_teacher = Teacher(name=name, crm_id=crm_id, tg_id=tg_id, phone=phone)
            self.session.add(new_teacher)
            self.session.commit()
            return True
        else:
            return False

    def get_teacher_by_crm_id(self, crm_id: int) -> Optional[Tuple[str, int, int, str]]:
        teacher = self.session.query(Teacher).filter_by(crm_id=crm_id).first()
        if teacher:
            return (teacher.name, teacher.crm_id, teacher.tg_id, teacher.phone)
        return None

    def get_teacher_by_tg_id(self, tg_id: int) -> Optional[Tuple[str, int, int, str]]:
        teacher = self.session.query(Teacher).filter_by(tg_id=tg_id).first()
        if teacher:
            return (teacher.name, teacher.crm_id, teacher.tg_id, teacher.phone)
        return None

    def get_teacher_by_phone(self, phone: str) -> Optional[Tuple[str, int, int, str]]:
        teacher = self.session.query(Teacher).filter_by(phone=phone).first()
        if teacher:
            return (teacher.name, teacher.crm_id, teacher.tg_id, teacher.phone)
        return None

    def fetch_teachers(self) -> List[Tuple[str, int, int, str]]:
        teachers = self.session.query(Teacher).all()
        return [(teacher.name, teacher.crm_id, teacher.tg_id, teacher.phone) for teacher in teachers]

    def delete_teacher_by_crm_id(self, crm_id: int) -> None:
        teacher = self.session.query(Teacher).filter_by(crm_id=crm_id).first()
        if teacher:
            self.session.delete(teacher)
            self.session.commit()

    def close(self) -> None:
        self.session.close()
