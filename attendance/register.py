# Create registering view for a class

from flask import (
    Blueprint, flash, g, 
    render_template, session, 
    request, url_for, redirect,
)

from sqlalchemy import extract

from .models import Student, Attendance, Event
from .utils import get_form_errors
from .auth import login_required
from .db import db_session

from datetime import datetime
import functools

bp = Blueprint('register', __name__)


def event_required(view):
    t = datetime.now()
    event = Event.query.filter(
                extract('day', Event.date) == t.day,
                extract('month', Event.date) == t.month,
                extract('year', Event.date) == t.year
            ).first()

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        g.event = event
        if event is None:
            flash(f"No Class slated for {t.strftime('%a %d,  %b %Y')}", "error")
            return redirect(url_for('auth.profile'))
        else:
            db_session.add(event)
        return view(**kwargs)
    return wrapped_view

@bp.route('/enroll', methods=["POST", "GET"])
def enroll():    
    if request.method == "POST":
        form = request.form
        # check for errors
        errors = get_form_errors(form)
        if errors:
            for error in errors:
                flash(error, 'error')

        # if no errors check if student exists
        elif Student.query.filter(Student.reg_num == form['reg_num']).first():
            flash("A student is already enrolled with that registration number", "error")
      
        else:
            try:
                new_student = Student(**form)
            except Exception as e:
                flash('Something went wrong', 'error')
            else:
                db_session.add(new_student)
                db_session.commit()
                flash("Enrolled", "success")
                session.clear()
                session['student_id'] = new_student.id
                g.student = new_student
                return redirect(url_for('auth.profile'))
    return render_template("register/enrollment_form.html")
    

@bp.route('/mark-attendance', methods=["GET"])
@login_required
@event_required
def mark_attendance():
    # check if student is already in event's attendance
    if g.student in g.event.attendance:
        flash("Attendance already taken", "info")
    else:
        # add student to event attendance via secondary attendance table
        attendance_obj = Attendance()
        attendance_obj.student = g.student
        g.event.append(attendance_obj)
        db_session.add(attendance_obj)
        flash("Attendance taken", "success")

    return redirect(url_for('auth.profile'))


