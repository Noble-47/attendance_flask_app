# Create registering view for a class

from flask import (
    Blueprint, flash, g, 
    render_template, session, 
    request, url_for, redirect,
    url_for
)

from sqlalchemy import extract

from .models import Student, Attendance, Event
from .utils import get_form_errors
from .db import db_session

from datetime import datetime
import functools

bp = Blueprint('register', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.student is None:
            flash("First input you registration number for identification", "error")
            return redirect(url_for('register.login'))
        return view(**kwargs)
    return wrapped_view

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
            return redirect(url_for('register.profile'))
        else:
            db_session.add(event)
        return view(**kwargs)
    return wrapped_view

@bp.before_app_request
def load_student():
    student_id = session.get("student_id")
    if student_id is None:
        g.student = None
    else:
        g.student = db_session.get(Student, student_id)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.student is not None:
        flash("Logged in as {g.student.firstname}", "info")
        return redirect(url_for('register.profile'))

    if request.method == "POST":
        reg_num = request.form['reg_num']
        stud = Student.query.filter(Student.reg_num == reg_num).first()
        if stud is None:
            flash(f"You have to enroll first", "error")
            return redirect(url_for('register.enroll'))
        else:
            session.clear()
            session['student_id'] = stud.id
            return redirect(url_for('register.profile'))
            
    return render_template("register/reg_number_form.html")

@bp.route('/profile')
@login_required
def profile():
    return render_template("register/profile.html")

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
                return redirect(url_for('register.profile'))
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

    return redirect(url_for('register.profile'))


