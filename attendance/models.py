from __future__ import annotations

from sqlalchemy import (
        String, DateTime, Integer,
        Column, ForeignKey, Table,
        Boolean, Text
)

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from sqlalchemy.orm import Mapped

from datetime import datetime
from typing import List
import json
import re

from .db import Base


class Attendance(Base):
    __tablename__ = "attendance"

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"), primary_key=True)
    arrival_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    student: Mapped[Student] = relationship(back_populates="events")
    event: Mapped[Event] = relationship(back_populates="attendance")
    
    def __init__(self, event, student):
        self.event = event
        self.student = student

class Student(Base):

    __tablename__ = "student"
    VALID_LEVELS = '100 200 300 400 500'.split(' ')

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reg_num: Mapped[str]  = mapped_column(String(11), nullable=False)
    firstname: Mapped[str]  = mapped_column(String(30), nullable=False)
    lastname: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(11), nullable=True)
    department: Mapped[str] = mapped_column(String(15), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    events: Mapped[List[Attendance]] = relationship(back_populates="student")

    def __init__(self, reg_num, firstname, lastname, department, level, phone_number=None):
        self.reg_num = reg_num
        self.firstname = firstname
        self.lastname = lastname
        self.phone_number = phone_number
        self.level = level
        self.department = department

    @validates("level")
    def validate_level(self, key, level):
        if level not in self.VALID_LEVELS:
            raise ValueError(f"{level} is not a valid option, select any of [", *VALID_LEVELS, "]")
        return level
    
    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        if phone_number is None:
            return None

        pattern = r"^0[789]\d{9}$"
        if re.match(pattern, phone_number) is None:
            raise ValueError(f"{phone_number} does not seem to be a valid phone number")
        return phone_number

    @validates('reg_num')
    def validate_reg_no(self, key, reg_no):
        pattern = r"^20[1-2][0-9]/\d{6}$"
        if re.match(pattern, reg_no) is not None:
            return reg_no
        raise ValueError(f"{reg_no} is not a valid registration number")
    
    def to_json(self, mask=['id'], **extra_kw):
        """
        Returns a dict representation of Student
        
        extra_kw are updated to json representation

        mask identifies attribute of students not to add to json represenation
        """
        attrs = ['id', 'reg_num', 'firstname', 'lastname', 'level', 'department', 'phone_number']
        student = {}
        for attr in attrs:
            if attr not in mask:
                student[attr] = self.__dict__.get(attr)

        student.update(extra_kw)
        return json.dumps(student)
        

    def __repr__(self):
        return f"<Student {self.lastname!r}  {self.firstname!r}, {self.reg_num!r} >"

class Event(Base):

    __tablename__ = "event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    attendance: Mapped[List[Attendance]] = relationship(back_populates="event") 
    created_by: Mapped[int] = mapped_column(ForeignKey("admin.id"))
    admin: Mapped[Admin] = relationship(back_populates="events")
    
    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return f"<Hands On Python Training Class -- {self.date.strftime('%a %b %d, %Y')}> "

class Admin(Base):

    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(11), unique=True)
    firstname: Mapped[str] = mapped_column(String(11), nullable=False)
    lastname: Mapped[str] = mapped_column(String(11), nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    events: Mapped[List[Event]] = relationship(back_populates="admin")

    def __init__(self, firstname, lastname, username, password):
        self.firstname = firstname
        self.lastname = lastname    
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<Admin {self.username!r}>"
