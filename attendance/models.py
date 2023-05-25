
from sqlalchemy import (
        String, DateTime, Integer,
        Column, ForeignKey, Table
)

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import validates

from datetime import datetime
import re

from attendance.db import Base


attendance_table = Table(
        "attendance_table",
        Base.metadata,
        Column("student", ForeignKey("student.id"), primary_key=True),
        Column("event", ForeignKey("event.id"), primary_key=True),
        Column("arrival_time", DateTime,  default=datetime.now)
)


class Student(Base):

    __tablename__ = "student"
    VALID_LEVELS = [100, 200, 300, 400, 500]

    id = mapped_column(Integer, primary_key=True, sql_autoincrement=True)
    reg_num = mapped_column(String(11), nullable=False)
    firstname = mapped_column(String(30), nullable=False)
    lastname = mapped_column(String(30), nullable=False)
    phone_number = mapped_column(String(11), nullable=False)
    department = mapped_column(String(15), nullable=False)
    level = mapped_column(Integer, nullable=False)
    events = relationship(secondary=attendance_table, back_populates="students")

    @validates("level")
    def validate_level(self, key, level):
        if level not in VALID_LEVELS:
            raise ValuError(f"{level} is not a valid option, select any of [", *VALID_LEVELS, "]")
        return level
    
    @validates('phone_number')
    def validate_phone_number(self, key, level):
        pattern = r"^(\\+?234|0)[789]\\d{9}$"
        if re.match(pattern, phone_number) is None:
            raise ValueError(f"{phone_number} does not seem to be a valid phone number")
        return phone_number

    @validates('reg_num')
    def validate_reg_no(self, key, reg_no):
        pattern = r"^20[1-2][0-9]/\d{6}$"
        if re.match(pattern, reg_no) is not None:
            return reg_no
        raise ValueError(f"{reg_no} is not a valid registration number")


class Event(Base):
    id = mapped_column(Integer, primary_key=True, sql_autoincrement=True)
    date = mapped_column(DateTime, nullable=False, default=datetime.now)
    students = relationship(secondary=attendance_table, back_populates="classes") 
