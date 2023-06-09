# Create registering view for a class

from flask import (
    Blueprint, flash, g, 
    render_template, session, 
    request, url_for, redirect,
    current_app,
)


from sqlalchemy import extract, update
from werkzeug.urls import url_parse

from .utils import get_form_errors 
from .models import Student, Attendance, Event
from .auth import login_required
from .db import db_session

from collections import deque
from datetime import datetime
import functools


bp = Blueprint('register', __name__)
       
def event_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.event is None:
            flash(f"No Class slated for {datetime.now().strftime('%a %d,  %b %Y')}", "error")
            if url_parse(request.referrer).netloc == "":
                return redirect(request.referrer)
            else:
                if g.admin:
                    return redirect(url_for('admin.dashboard'))
                if g.student:
                    return redirect(url_for('auth.profile'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/enroll', methods=["POST", "GET"])
@bp.route('/enroll/<string:reg_num>', methods=["POST", "GET"])
def enroll(reg_num=None):    
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

    reg_num = reg_num.replace('_', '/') if reg_num else None
    return render_template("register/enrollment_form.html", reg_num=reg_num)
    

@bp.route('/mark-attendance', methods=["GET"])
@login_required
@event_required
def mark_attendance():
    # check if event is closed
    if g.event.is_closed:
        flash("Class has been closed for attendance", "error")
        
        # clean up seen list on redis
        current_app.redis.unlink('seen')

        return redirect(request.referrer)

    # check if student is already in event's attendance
    attendance_obj = Attendance.query.filter(
            Attendance.student==g.student, 
            Attendance.event==g.event
    ).first() 

    if attendance_obj is not None:
        flash("Attendance already taken", "info")
        
    if attendance_obj is None:
        # add student to event attendance via secondary attendance table
        attendance_obj = Attendance(event=g.event, student=g.student)
        attendance_obj.student = g.student
        arrival_time = datetime.now()
        attendance_obj.arrival_time = arrival_time
        g.event.attendance.append(attendance_obj)
        
        # save in database
        db_session.add(attendance_obj)
        db_session.commit()

        
        ## TODO: add a flag to student showing student is registered
        session['is_registered'] = True

        # get attendance json representation as record
        # publish record to attendance update channel
        # for live update of connected clients
       
        arrival_time = attendance_obj.arrival_time # delete after
        record = attendance_obj.student.to_json(mask=['id', 'level', 'phone_number'], arrival_time=arrival_time.strftime('%H : %M'))
        
        current_app.redis.publish("attendance-update", message=record)
        current_app.redis.lpush("seen", record)
        

        flash("Attendance taken", "success")

        return redirect(url_for('auth.profile'))

        
