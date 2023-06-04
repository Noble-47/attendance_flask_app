from werkzeug.security import generate_password_hash
import click

from .db import init_db, db_session
from .models import Admin
from . import settings

import getpass
import os

db_path = settings.DATABASE


def get_user_prompt(firstname=None, lastname=None, password=None, username=None):
    
    firstname = firstname or input("Enter firstname: ")
   
    if not firstname:
        print("Firstname cannot be empty")
        get_user_prompt()

    lastname =  lastname or input("Enter lastname: ")
    
    if not lastname:
        print("Lastname cannot be empty")
        get_user_prompt(firstname=firstname)
    
    username = username or input("Enter username: ")
    if not username:
        print("Username cannot be empty")
        get_user_prompt(firstname, lastname, username)
    
    password = getpass.getpass("Enter password: ")
    password2 = getpass.getpass("confirm password: ")

    if len(password) < 8:
        print("Password should be 8 characters")
        get_user_prompt(firstname, lastname)

    if password != password2:
        print("password does not match")
        get_user_prompt(firstname, lastname)

    return firstname, lastname, username, password

def create_admin():
    firstname, lastname, username, password = get_user_prompt()

    password = generate_password_hash(password)
    new_admin = Admin(firstname=firstname, lastname=lastname, username=username, password=password)
    db_session.add(new_admin)
    db_session.commit()

    print("Created new admin")

@click.command('create-admin')
def create_admin_command():
    """Create an admin"""
    create_admin()

def init_app(app):
    app.cli.add_command(create_admin_command)

