from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
from flask_hashing import Hashing
from worldwaytravel import app
import re
from .database import get_cursor

register = Blueprint("register", __name__, static_folder="static", 
                       template_folder="templates")

hashing = Hashing(app)

@register.route('/', methods=['GET', 'POST'])
def register_route():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'confirmpassword' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        confirmpassword = request.form['confirmpassword']
        # Get cursor and connection from the database module
        cursor, connection = get_cursor()
        
        cursor.execute('SELECT * FROM User WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'^[A-Za-z0-9]+$', username):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
            msg = 'Password must be at least 8 characters long and contain a mix of character types!'
        elif password != confirmpassword:
            msg = 'Password and confirm password do not match!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            hashed = hashing.hash_value(password, salt='abcd')
            default_role = 'Customer'
            default_status = 'Active'
            cursor.execute('INSERT INTO User (username, password, role, date_birth) VALUES (%s, %s, %s, %s)',(username, hashed, default_role, '1900-01-01'))
            connection.commit()  # Commit changes to the database
            
            cursor.execute('SELECT user_id FROM User WHERE username = %s', (username,))
            user_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO Customer (customer_id, first_name, last_name, email, status, credit_limit, remaining_credit) VALUES (%s, %s, %s, %s, %s, %s, %s)', (user_id, 'FirstName', 'FamilyName', email, default_status, -1, -1,))
            connection.commit()  # Commit changes to the database
            
            msg = 'You have successfully registered!'
            
        # Close cursor and connection
        cursor.close()
        connection.close()

    elif request.method == 'POST':
        msg = 'Please fill out the form!'
        
    return render_template('register.html', msg=msg)
