from flask import (
    Blueprint, flash, g, 
    render_template, session, 
    request, url_for, redirect,
    jsonify, Response, current_app,
    stream_with_context
)

from werkzeug.security import check_password_hash
from sqlalchemy import extract

from .models import Student, Attendance, Event, Admin
from .register import event_required
from .db import db_session
from .utils import json_serialize

from collections import deque
import functools
import datetime
import json


bp = Blueprint("admin", __name__, url_prefix='/admin')

def is_admin(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            flash("Not Allowed", "error")
            return redirect(url_for('admin.admin_login'))
        return view(**kwargs)
    return wrapped_view


@bp.before_app_request
def load_admin():
    admin_id = session.get("admin_id")
    if admin_id is None:
        g.admin = None
    else:
        g.admin = db_session.get(Admin, admin_id)


@bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.query.filter(Admin.username == username).first()
        if not admin:
            flash(f"No Admin with username {username}", "error")
            return render_template("admin/login.html")

        if not check_password_hash(admin.password, password):
            error = "Incorrect password"

        if error is None:
            # remove student if any
            g.student = None
            session.clear()

            session['admin_id'] = admin.id
            flash('logged In as Admin', 'success')
            return redirect(url_for('admin.dashboard'))

        flash(error, 'error')
    return render_template('admin/login.html')

@bp.route('/logout')
def admin_logout():
    g.admin = None
    session.clear()
    flash("logged out", "info")
    return redirect(url_for('admin.admin_login'))

@bp.route('/')
@is_admin
def dashboard():
    return render_template('admin/board.html')

@bp.route('/live-attendance-update')
@is_admin
@event_required
def get_live_attendance_update():
    # TODO : use redis instead of deque
    # TODO : implement a way of closing communication if event is closed for attendance

    # add user to attendance-update channel
    pubsub = current_app.redis.pubsub()
    pubsub.subscribe('attendance-update')
    timeout = 0  # forever keep redis connection open
    retry = 5 # retry to open connection after 5 secs

    @stream_with_context
    def attendance_stream():
        # infinite loop for stream
        while True:
            # listen for messages published on attendance-update channel
            for pubsub_message in pubsub.listen():
                # disregard subscribed and unsubscribed messages
                message = {}
                if pubsub_message['type'] == 'message':
                    item = pubsub_message['data']
             
                    # get data dictionary
                    data = json.loads(item)
                    
                    message['event'] = 'new_attendance'
                    message['retry'] = retry
                    message['data'] = data

                    # make message a valid JSON data
                    message = json_serialize(message)
                    
                    # send stream data
                    yield message
    
    # create a response with event stream content type
    response = Response(attendance_stream(), mimetype='text/event-stream')

    # Set additional headers to enable server sent events
    response.headers['Cache-control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    #response.headers['Content-Encoding'] = 'text/event-stream'
    response.headers['X-Accel-Bufferring'] = 'no'

    #return response
    return response

@bp.route('/live-attendance')
@is_admin
@event_required
def live_attendance():
    # check for seen attendance record
    records = current_app.redis.lrange('seen', 0, -1)
    # convert to list of dictionary
    records = [json.loads(record) for record in records]
    return render_template("admin/live_attendance.html", records=records)

@bp.route('/start_class')
@is_admin
def start_class():
    if not g.event:
        t = datetime.datetime.now()
        admin = g.admin

        new_event = Event(date=t)
        new_event.created_by = g.admin.id
        new_event.admin = g.admin

        db_session.add(new_event)
        db_session.commit()
        g.event = new_event

        flash(f"{new_event} Opened for attendance", "success")
    else:
        flash("There is already a class scheduled for today", "error")
        return redirect(url_for('admin.dashboard'))

    return redirect(url_for('admin.live_attendance'))

@bp.route('/schedule_class', methods=['GET', 'POST'])
@is_admin
def schedule_class():
    if request.method == "POST":
        form = request.form
        date = form.get('date') # in the form 2023-06-01
        time = form.get('time') # in the form 15:30
         
        year, month, day = date.split('-')
        hour, minute = time.split(':')
        print(date)
        # remove leading zeros and convert to interger
        day = int(day)
        month = int(month)
        year = int(year)
        hour = int(hour)
        minute = int(minute)

        event_time = datetime.datetime(year, month, day, hour, minute)
        # check if an open event is scheduled for the same day, month and year
        # can only have an open event per day
        clashing_event = Event.query.filter(
                    extract('day', Event.date) == event_time.day,
                    extract('month', Event.date) == event_time.month,
                    extract('year', Event.date) == event_time.year
                ).first()

        if clashing_event:
            flash(f"Cannot schedule class for {event_time.strftime('%a %d, %b %Y')}, clashes with another", "error")
        else: 
            new_event = Event(event_time)
            new_event.admin = g.admin
            db_session.add(new_event)
            db_session.commit()
            flash(f"Added new class {new_event!r} to class schedules", "info")
            
            # make new event current event 
            g.event = new_event
        # redirect to scheduled class list
        return redirect(url_for('admin.dashboard'))
    else:
        return render_template('admin/schedule_class_form.html')

