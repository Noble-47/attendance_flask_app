from flask import (
    Blueprint, flash, g, 
    render_template, session, 
    request, url_for, redirect,
)
from sqlalchemy import update

from .models import Student, Attendance, Event
from .utils import get_form_errors
from .db import db_session

import functools


bp = Blueprint('auth', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.student is None:
            flash("First input you registration number for identification", "error")
            return redirect(url_for('auth.login'))
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
        flash(f"Logged in as {g.student.firstname}", "info")
        return redirect(url_for('auth.profile'))

    if request.method == "POST":
        reg_num = request.form['reg_num']
        stud = Student.query.filter(Student.reg_num == reg_num).first()
        if stud is None:
            flash(f"You have to enroll first", "error")
            return redirect(url_for('register.enroll', reg_num=reg_num.replace('/', '_')))
        else:
            session.clear()
            session['student_id'] = stud.id
            return redirect(url_for('auth.profile'))
            
    return render_template("auth/reg_number_form.html")

@bp.route('/profile')
@login_required
def profile():
    return render_template("auth/profile.html")

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == "POST":
        form = request.form
        errors = get_form_errors(form)
        if errors is not None:
            reg_num = form.get('reg_num')
            student = Student.query.filter(Student.reg_num == reg_num).first()
            if student is not None:
                update_stmt = (
                    update(Student)
                    .where(Student.reg_num == reg_num)
                    .values(**form)        
                )
                db_session.execute(update_stmt)
                db_session.commit()
                return redirect(url_for('auth.profile')) 
            else:   
                error = f"No student with registration number {reg_num!r} was registered"
        flash(error, 'error')
        return redirect(url_for('auth.edit_profile'))
    
    return render_template('auth/edit_profile.html')

@bp.route('/logout')
def logout():
    g.student = None
    session.clear()
    return redirect(url_for('auth.login'))
