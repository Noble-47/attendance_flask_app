from attendance.models import Student, Event
from attendance.db import db_session

from datetime import datetime

stud = Student('2018/242674', 'Onunwa', 'Goodness', 'ECE', '08099691232', 400)
e = Event(datetime.now())
