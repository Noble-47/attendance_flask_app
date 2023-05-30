from flask import (
    Blueprint, flash, g, 
    render_template, session, 
    request, url_for, redirect,
)

from .models import Student, Attendance, Event
from .db import db_session

bp = Blueprint("admin", __name__)


