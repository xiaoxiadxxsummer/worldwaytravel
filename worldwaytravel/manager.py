from worldwaytravel import app
from worldwaytravel import Blueprint
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify,current_app
from flask_hashing import Hashing
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, date, time
import os
import re
from . import connect
from .database import get_cursor, get_dict_cursor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from plotly.offline import plot
import plotly.graph_objects as go
import decimal


manager = Blueprint("manager", __name__, static_folder="static", 
                       template_folder="templates")

hashing = Hashing(app)

@manager.route('/')
def manager_dashboard():
    if 'loggedin' in session: # Ensuring the user is a logged-in manager
        user_role = session.get('role', None)
        user_id = session.get('id', None)
        cursor, connection = get_cursor() 

        #Fetch manager profile info
        cursor.execute('SELECT * FROM Manager WHERE manager_id = %s', (session['id'],))
        manager_profile = cursor.fetchone()

         
        #Fetch user account info
        cursor.execute('SELECT * FROM User WHERE user_id = %s',(session['id'],))
        manager_info = cursor.fetchone()

        cursor.close()  
        connection.close() 
        

        return render_template('manager_dashboard.html',manager_info = manager_info, manager_profile = manager_profile)
    return redirect(url_for('login.login_page'))

@manager.route('/profile')
def manager_profile():
    if 'loggedin' in session: # Ensuring the user is a logged-in manager
        user_role = session.get('role', None)
        user_id = session.get('id', None)
        cursor, connection = get_cursor() 

        #Fetch manager profile info
        cursor.execute('SELECT * FROM Manager WHERE manager_id = %s', (session['id'],))
        manager_profile = cursor.fetchone()

        #Fetch user account info
        cursor.execute('SELECT * FROM User WHERE user_id = %s',(session['id'],))
        manager_info = cursor.fetchone()

        cursor.close()  
        connection.close() 


        return render_template('manager_profile.html',manager_info = manager_info, manager_profile = manager_profile)
    else:
        return redirect(url_for('login.login_page'))

@manager.route('/manager/manager_profile_edit', methods=['GET', 'POST'])
def manager_profile_edit():
    if 'loggedin' in session :
        user_role = session.get('role', None)
        user_id = session.get('id', None)
        cursor, connection = get_cursor() 
        if request.method == 'POST':
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            image_url = request.files.get('image_url')
            image_path = upload(image_url)

            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Invalid email address format.', 'error')
                return redirect(request.url)
            nz_phone_pattern = re.compile(r"^(\+64|0)([2-9]\d{1}|[27]\d{2})[-\s]?\d{3}[-\s]?\d{4}$")
            if not nz_phone_pattern.match(phone_number):
                flash('Phone number must be in New Zealand format.', 'error')
                return redirect(request.url)

            if image_path:

                cursor.execute('''
                               UPDATE Manager
                               SET title=%s, first_name=%s, last_name=%s, phone_number=%s, email=%s, image_url=%s
                            WHERE manager_id=%s
                           ''', (title, first_name, last_name, phone_number, email, image_path, user_id))

            else:

                #update manager info
                cursor.execute('''
                                UPDATE Manager
                                SET title=%s, first_name=%s, last_name=%s, phone_number=%s, email=%s
                                WHERE manager_id=%s
                           ''', (title, first_name, last_name, phone_number, email, user_id))
            flash('Profile updated successfully', 'success')
            return redirect(url_for('manager.manager_profile', image_path=image_path))
        else:
            cursor.execute('SELECT * FROM User WHERE user_id = %s',(session['id'],))
            manager_info = cursor.fetchone()
            #fetch current manager profile for edit
            cursor.execute('SELECT * FROM Manager WHERE manager_id = %s', (session['id'],))
            manager_profile = cursor.fetchone()


            cursor.close()  
            connection.close() 

            return render_template('manager_profile_edit.html', manager_profile=manager_profile, manager_info=manager_info)
    else:
        return redirect(url_for('login.login_page'))
    
def upload(file):
    if file and file.filename:
                filename = secure_filename(file.filename)
                uploads_dir =os.path.join(current_app.root_path,'static','uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                filepath = os.path.join(uploads_dir, filename)
                file.save(filepath.replace("\\", "/"))
                return os.path.join('uploads', filename).replace("\\", "/")
    return None


@manager.route("/change_password", methods=["POST"])
def change_password():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))

    cursor, connection = get_cursor()
    new_password = request.form['newPassword']
    confirm_password = request.form['confirmPassword']

    if new_password != confirm_password:
        flash('New password and confirm password do not match.')
        return redirect(url_for('manager.manager_profile'))

    if not new_password or (len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password)):
        flash('Password must be at least 8 characters long and contain both letters and numbers.')
        return redirect(url_for('manager.manager_profile'))

    hashed = hashing.hash_value(new_password, salt='abcd')

    update_account_query = '''
        UPDATE User
        SET password = %s
        WHERE user_id = %s
    '''
    cursor.execute(update_account_query, (hashed, session['id']))
    connection.commit()

    flash('Your password has been successfully updated.')
    return redirect(url_for('manager.manager_profile'))

# Manage customers
@manager.route("/managecustomer")
def manage_customer():
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor, connection = get_cursor()
        # Select all users info to show the list
        sql = """SELECT * FROM User LEFT JOIN Customer ON User.user_id = Customer.customer_id WHERE role = 'Customer';"""
        cursor.execute(sql)
        accountlist = cursor.fetchall()
        # Show the manage users page with account info
        return render_template('manage_customer.html', accountlist=accountlist)
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))

@manager.route("/searchcustomer", methods=["GET","POST"])
def search_customer():
    if 'loggedin' in session:
        if request.method == "POST":
            searchterm = request.form.get('search')
            searchtermupdated = f"%{searchterm}%"
            cursor, connection = get_cursor()
            # Select all searched members and order them by family name and then first name
            search_query = """SELECT * FROM User 
            LEFT JOIN Customer ON User.user_id = Customer.customer_id 
            WHERE Role = 'Customer' 
            AND (first_name LIKE %s OR last_name LIKE %s) 
            ORDER BY last_name, first_name;"""
            cursor.execute(search_query,(searchtermupdated,searchtermupdated))
            accountlist = cursor.fetchall()
            return render_template("manage_customer.html", accountlist = accountlist)
        return redirect(url_for('manager.manage_customer'))
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page')) 

@manager.route("/viewcustomer/<id>")
def view_customer(id):
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor, connection = get_cursor()
        # Select customer info to show the profile
        # Fetch user account info
        cursor.execute('SELECT * FROM User WHERE user_id = %s', (id,))
        account = cursor.fetchone()
        
        # Fetch customer info for the user
        cursor.execute('SELECT * FROM Customer WHERE customer_id = %s', (id,))
        customer_info = cursor.fetchone()
        # Show the manage users page with account info
        return render_template('view_customer.html', account=account, customer_info=customer_info )
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))


@manager.route("/updatecustomer/<id>", methods=['GET', 'POST'])
def update_customer(id):
    cursor, connection = get_cursor()
        # Select customer info to show the profile
        # Fetch user account info
    cursor.execute('SELECT * FROM User WHERE user_id = %s', (id,))
    account = cursor.fetchone()
        
        # Fetch customer info for the user
    cursor.execute('SELECT * FROM Customer WHERE customer_id = %s', (id,))
    customer_info = cursor.fetchone()
    if 'loggedin' in session:
        msg=''
        if request.method == "POST":
            username = request.form.get('username')
            title = request.form.get('title')
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            birthdate = request.form.get('birthdate')
            points = request.form.get('points')
            credit = request.form.get('credit')
            remain_credit = request.form.get('remain_credit')
            filename = None

            profile_image = request.files.get('profile_image')
            print("File is not being processed...")
            if profile_image and profile_image.filename:
                print("File is being processed...")
                filename = secure_filename(profile_image.filename)
                filepath = os.path.join('worldwaytravel', 'static', 'uploads', filename)
                
                print("Filepath:", filepath)
                profile_image.save(filepath)

                cursor.execute('''
                               UPDATE Customer
                               SET image_url=%s
                               Where customer_id=%s
                               ''',(filename,id)

                )
            update_sql = """UPDATE Customer SET title = %s, first_name=%s, last_name=%s, email=%s, address=%s, 
            phone_number=%s, date_birth =%s, points_balance=%s, credit_limit=%s, remaining_credit=%s WHERE customer_id = %s"""
            cursor.execute(update_sql, (title,firstname,lastname, email, address, phone, birthdate, points, credit, remain_credit, id))
            
            #check phone number in nz format
            nz_phone_pattern = re.compile(r"^(\+64|0)([2-9]\d{1}|[27]\d{2})[-\s]?\d{3}[-\s]?\d{4}$")
            if not nz_phone_pattern.match(phone):
                flash('Phone number must be in New Zealand format.', 'error')
                return redirect(request.url)
            # Check if the new username is already taken
            check_username_query = '''SELECT COUNT(*) FROM User WHERE username = %s AND user_id != %s'''
            cursor.execute(check_username_query, (username, id))
            result = cursor.fetchone()
            if result[0] > 0:
                msg = 'Username is already taken!'
            else:
                # Update the database
                update_user_query = "UPDATE User SET username = %s WHERE user_id = %s"
                cursor.execute(update_user_query, (username, id))
                return redirect(url_for('manager.view_customer', id=id))
        return render_template('update_customer.html', account=account, customer_info=customer_info, msg=msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))

@manager.route("/changecustomerpassword/<id>", methods=["POST"])
def change_customer_password(id):
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))

    cursor, connection = get_cursor()
    new_password = request.form['newPassword']
    confirm_password = request.form['confirmPassword']

    if new_password != confirm_password:
        flash('New password and confirm password do not match.')
        return redirect(url_for('manager.view_customer', id=id))

    if not new_password or (len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password)):
        flash('Password must be at least 8 characters long and contain both letters and numbers.')
        return redirect(url_for('manager.view_customer', id=id))

    hashed = hashing.hash_value(new_password, salt='abcd')

    update_account_query = '''
        UPDATE User
        SET password = %s
        WHERE user_id = %s
    '''
    cursor.execute(update_account_query, (hashed, id))
    connection.commit()

    flash('Your password has been successfully updated.')
    return redirect(url_for('manager.view_customer', id=id))


@manager.route("/changecustomer/<id>", methods=['GET', 'POST'])
def change_customer_status(id):
    if 'loggedin' in session:
        cursor, connection = get_cursor()
        sql = """SELECT * FROM User LEFT JOIN Customer ON User.user_id = Customer.customer_id WHERE role = 'Customer';"""
        cursor.execute(sql)
        accountlist = cursor.fetchall()
        if request.method == 'POST':
            # Update the status from customer
            status = request.form.get('status')
            cursor.execute("UPDATE Customer SET status = %s WHERE customer_id=%s;",(status,id))
            connection.commit()
            return redirect(url_for('manager.manage_customer'))
        return render_template('manage_customer.html', accountlist=accountlist)
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))

@manager.route("/addcustomer", methods=['GET', 'POST'])
def add_customer():
    if 'loggedin' in session:
        msg = ''
        cursor, connection = get_cursor()
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            title = request.form.get('title')
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            birthdate = request.form.get('birthdate')
            # points = request.form['points'] if request.form['points'] else 0
            # credit = request.form['credit'] if request.form['credit'] else -1
            remain_credit = request.form['remain_credit'] if request.form['remain_credit'] else -1
            
            
            # Validate the new added password and email, username and phone number in nz format
            
            nz_phone_pattern = re.compile(r"^(\+64|0)([2-9]\d{1}|[27]\d{2})[-\s]?\d{3}[-\s]?\d{4}$")
            if not nz_phone_pattern.match(phone):
                flash('Phone number must be in New Zealand format.', 'error')
                return redirect(request.url)
            
            check_username_query = '''SELECT COUNT(*) FROM User WHERE username = %s'''
            cursor.execute(check_username_query, (username,))
            result = cursor.fetchone()
            if result[0] > 0:
                msg = 'Username is already taken!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif len(password) < 8:
                msg = 'Password must be at least 8 characters long!'
            elif not re.search(r'[A-Z]', password):
                msg = 'Password must contain at least one uppercase letter!'
            elif not re.search(r'[a-z]', password):
                msg = 'Password must contain at least one lowercase letter!'
            elif not re.search(r'\d', password):
                msg = 'Password must contain at least one digit!'
            elif not re.search(r'[^A-Za-z0-9]', password):
                msg = 'Password must contain at least one special character!'    
            else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            # Implement a password hashing and salting techniques to ensure secure storage of user passwords. 
                hashed = hashing.hash_value(password, salt='abcd')
                
                # Insert info to useraccount
                sql1 = """INSERT INTO User (username, password, role) VALUES (%s, %s, %s);"""
                cursor.execute(sql1,(username, hashed, 'Customer'))
                # Then, insert other profile info to customer
                cursor.execute("SELECT LAST_INSERT_ID();")
                customer_id = cursor.fetchone()[0]
                sql2 = """INSERT INTO Customer values(%s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s,NULL,%s);"""
                cursor.execute(sql2,(customer_id,firstname,lastname,title, birthdate,email, phone,address, 0,-1, remain_credit,'Active'))

                return redirect(url_for('manager.manage_customer'))
        return render_template('add_customer.html',msg=msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))

# Manage staff
@manager.route("/managestaff")
def manage_staff():
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor, connection = get_cursor()
        # Select all users info to show the list
        sql = """SELECT * FROM User LEFT JOIN Staff ON User.user_id = Staff.staff_id WHERE role = 'Staff';"""
        cursor.execute(sql)
        accountlist = cursor.fetchall()
        # Show the manage users page with account info
        return render_template('manage_staff.html', accountlist=accountlist)
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))

@manager.route("/searchstaff", methods=["GET","POST"])
def search_staff():
    if 'loggedin' in session:
        if request.method == "POST":
            searchterm = request.form.get('search')
            searchtermupdated = f"%{searchterm}%"
            cursor, connection = get_cursor()
            # Select all searched staff and order them by family name and then first name
            search_query = """SELECT * FROM User LEFT JOIN Staff ON User.user_id = Staff.staff_id 
            WHERE Role = 'Staff' 
            AND (first_name LIKE %s OR last_name LIKE %s) 
            ORDER BY last_name, first_name;"""
            cursor.execute(search_query,(searchtermupdated,searchtermupdated))
            accountlist = cursor.fetchall()
            return render_template("manage_staff.html", accountlist = accountlist)
        return redirect(url_for('manager.manage_staff'))
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page')) 

@manager.route("/viewstaff/<id>")
def view_staff(id):
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor, connection = get_cursor()
        # Select staff info to show the profile
        # Fetch user account info
        cursor.execute('SELECT * FROM User WHERE user_id = %s', (id,))
        account = cursor.fetchone()
        
        # Fetch staff info for the user
        cursor.execute('SELECT * FROM Staff WHERE staff_id = %s', (id,))
        staff_info = cursor.fetchone()
        # Show the manage users page with account info
        return render_template('view_staff.html', account=account, staff_info=staff_info )
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))

@manager.route('/updatestaff/<id>', methods=['GET', 'POST'])
def update_staff(id):
    cursor, connection = get_cursor()
    # Fetch user account info
    cursor.execute('SELECT * FROM User WHERE user_id = %s', (id,))
    account = cursor.fetchone()
    # Fetch stafft info for the user
    cursor.execute('SELECT * FROM Staff WHERE staff_id = %s', (id,))
    staff_info = cursor.fetchone()
    if 'loggedin' in session:
        msg=''
        if request.method == "POST": 
            username = request.form.get('username')
            title = request.form.get('title')
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            joindate = request.form.get('joindate')
            filename = None

            profile_image = request.files.get('profile_image')
            if profile_image and profile_image.filename:
                filename = secure_filename(profile_image.filename)
                filepath = os.path.join('worldwaytravel', 'static', 'uploads', filename)
                profile_image.save(filepath)

                cursor.execute('''
                               UPDATE Staff
                               SET image_url=%s
                               Where staff_id=%s
                               ''',(filename,id)

                )
            cursor.execute("UPDATE Staff SET title = %s, first_name=%s, last_name=%s, email=%s, phone_number=%s, date_join = %s WHERE staff_id = %s;",(title, firstname, lastname, email, phone, joindate, id))
            
            #check phone number in nz format
            nz_phone_pattern = re.compile(r"^(\+64|0)([2-9]\d{1}|[27]\d{2})[-\s]?\d{3}[-\s]?\d{4}$")
            if not nz_phone_pattern.match(phone):
                flash('Phone number must be in New Zealand format.', 'error')
                return redirect(request.url)
            
            # Check if the new username is already taken
            check_username_query = '''SELECT COUNT(*) FROM User WHERE username = %s AND user_id != %s'''
            cursor.execute(check_username_query, (username, id))
            result = cursor.fetchone()
            if result[0] > 0:
                msg = 'Username is already taken!'
            else:
                # Update the database
                update_user_query = "UPDATE User SET username = %s WHERE user_id = %s"
                cursor.execute(update_user_query, (username, id))          
                return redirect(url_for('manager.view_staff', id=id))
        
        return render_template('update_staff.html', account=account, staff_info=staff_info, msg=msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))


@manager.route("/changestaffpassword/<id>", methods=["POST"])
def change_staff_password(id):
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))

    cursor, connection = get_cursor()
    new_password = request.form['newPassword']
    confirm_password = request.form['confirmPassword']

    if new_password != confirm_password:
        flash('New password and confirm password do not match.')
        return redirect(url_for('manager.view_staff', id=id))

    if not new_password or (len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password)):
        flash('Password must be at least 8 characters long and contain both letters and numbers.')
        return redirect(url_for('manager.view_staff', id=id))

    hashed = hashing.hash_value(new_password, salt='abcd')

    update_account_query = '''
        UPDATE User
        SET password = %s
        WHERE user_id = %s
    '''
    cursor.execute(update_account_query, (hashed, id))
    connection.commit()

    flash('Your password has been successfully updated.')
    return redirect(url_for('manager.view_staff', id=id))


@manager.route("/changestaff/<id>", methods=['GET', 'POST'])
def change_staff_status(id):
    if 'loggedin' in session:
        cursor, connection = get_cursor()
        sql = """SELECT * FROM User LEFT JOIN Staff ON User.user_id = Staff.staff_id WHERE role = 'Staff';"""
        cursor.execute(sql)
        accountlist = cursor.fetchall()
        if request.method == 'POST':
            # Update the status from staff
            status = request.form.get('status')
            cursor.execute("UPDATE Staff SET status = %s WHERE staff_id=%s;",(status,id))
            connection.commit()
            return redirect(url_for('manager.manage_staff'))
        return render_template('manage_staff.html', accountlist=accountlist)
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))

@manager.route("/addstaff", methods=['GET', 'POST'])
def add_staff():
    if 'loggedin' in session:
        msg = ''
        cursor, connection = get_cursor()
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            title = request.form.get('title')
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            joindate = request.form.get('joindate')
            
            # Validate the new added password and email, username and phone number in nz format
            
            nz_phone_pattern = re.compile(r"^(\+64|0)([2-9]\d{1}|[27]\d{2})[-\s]?\d{3}[-\s]?\d{4}$")
            if not nz_phone_pattern.match(phone):
                flash('Phone number must be in New Zealand format.', 'error')
                return redirect(request.url)
            

            check_username_query = '''SELECT COUNT(*) FROM User WHERE username = %s'''
            cursor.execute(check_username_query, (username,))
            result = cursor.fetchone()
            if result[0] > 0:
                msg = 'Username is already taken!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif len(password) < 8:
                msg = 'Password must be at least 8 characters long!'
            elif not re.search(r'[A-Z]', password):
                msg = 'Password must contain at least one uppercase letter!'
            elif not re.search(r'[a-z]', password):
                msg = 'Password must contain at least one lowercase letter!'
            elif not re.search(r'\d', password):
                msg = 'Password must contain at least one digit!'
            elif not re.search(r'[^A-Za-z0-9]', password):
                msg = 'Password must contain at least one special character!'    
            else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            # Implement a password hashing and salting techniques to ensure secure storage of user passwords. 
                hashed = hashing.hash_value(password, salt='abcd')
                
                # Insert info to useraccount
                sql1 = """INSERT INTO User (username, password, role) VALUES (%s, %s, %s);"""
                cursor.execute(sql1,(username, hashed, 'Staff'))
                # Then, insert other profile info to membership
                cursor.execute("SELECT LAST_INSERT_ID();")
                staff_id = cursor.fetchone()[0]
                sql2 = """INSERT INTO Staff values(%s, %s, %s, %s, %s, %s, %s, NULL,%s);"""   
                cursor.execute(sql2,(staff_id,firstname,lastname,title, joindate,email, phone,'Active'))
                return redirect(url_for('manager.manage_staff'))
        return render_template('add_staff.html',msg=msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))


@manager.route("/loyalty_setting")
def loyalty_setting():
    # Fetch current loyalty settings
    cursor, connection = get_dict_cursor()
    cursor.execute('SELECT * FROM Loyalty_Settings')
    settings = cursor.fetchall()
    return render_template('loyalty_setting.html', settings=settings)


@app.route('/update_loyalty_setting', methods=['POST'])
def update_loyalty_setting():
    setting = request.form['setting']
    new_value = request.form['value']
    changed_by = "manager_username"  # Retrieve this from session or auth

    cursor, connection = get_dict_cursor()

    # Fetch current value
    cursor.execute('SELECT * FROM Loyalty_Settings WHERE setting = %s', (setting,))
    current_setting = cursor.fetchone()

    if current_setting:
        old_value = current_setting['value']
        cursor.execute('UPDATE Loyalty_Settings SET value = %s WHERE setting = %s', (new_value, setting))

        # Insert into history table
        cursor.execute(
            'INSERT INTO Loyalty_Settings_History (setting, old_value, new_value, changed_by) VALUES (%s, %s, %s, %s)',
            (setting, old_value, new_value, changed_by))

        flash('Loyalty settings updated successfully!', 'success')
    else:
        flash('Setting not found.', 'error')

    return redirect(url_for('manager.loyalty_setting'))

# Manage massage
@manager.route("/managemessage")
def manage_message():
    if 'loggedin' in session:
        cursor, connection = get_cursor()
        recipient_id = request.args.get('recipient_id')
        message_type = request.args.get('type')
        
        sql = "SELECT * FROM Messages"
        params = []
        
        if recipient_id:
            sql += " WHERE recipient_id = %s"
            params.append(recipient_id)
        elif message_type:
            sql += " WHERE message_type = %s"
            params.append(message_type)
        
        cursor.execute(sql, params)
        messagelist = cursor.fetchall()
        return render_template('manage_message.html', messagelist=messagelist)
    return redirect(url_for('login.login_page'))

# Manage credit limit
@manager.route("/managecredit")
def manage_credit():
    if 'loggedin' in session:
        cursor, connection = get_cursor()
        filter_status = request.args.get('filter', 'all')
        if filter_status == 'replied':
            cursor.execute("SELECT * FROM Messages LEFT JOIN Customer ON sender_id = customer_id WHERE message_type = 'apply_credit' AND reply_status = 'replied'")
            creditlist = cursor.fetchall()
        elif filter_status == 'waiting':
            cursor.execute("SELECT * FROM Messages LEFT JOIN Customer ON sender_id = customer_id WHERE message_type = 'apply_credit' AND reply_status = 'waiting for reply'")
            creditlist = cursor.fetchall()
        elif filter_status == 'all':
            cursor.execute("SELECT * FROM Messages LEFT JOIN Customer ON sender_id = customer_id WHERE message_type = 'apply_credit'")
            creditlist = cursor.fetchall()
        
        return render_template('manage_credit.html', creditlist=creditlist, filter_status=filter_status)
    return redirect(url_for('login.login_page'))


@manager.route("/process_reply", methods=["POST"])
def process_reply():
    if 'loggedin' in session:
        cursor, connection = get_cursor()

        request_credit_id = request.form.get('credit_id')
        reply_status = request.form.get('reply_status')
        credit_limit = request.form.get('credit_limit')
        decline_reason = request.form.get('decline_reason')

        cursor.execute("SELECT sender_id FROM Messages WHERE message_id = %s", (request_credit_id,))
        sender_id = cursor.fetchone()[0]

        # Update Customer table with credit limit if approved
        if reply_status == 'approve' and credit_limit is not None:
            today = date.today()
            due_date = today + timedelta(days=30)
            cursor.execute("UPDATE Customer SET credit_limit = %s, remaining_credit = %s WHERE customer_id = %s", (credit_limit, credit_limit, sender_id))
            cursor.execute("INSERT INTO Accounts (customer_id, credit_limit, outstanding_balance, invoice_due_date, invoice_frequency) VALUES(%s,%s,%s,%s,%s)", (sender_id,credit_limit, 0,due_date ,'Monthly'))
            # Insert message into Messages table
            message_content = reply_status + ', ' + credit_limit
            cursor.execute("INSERT INTO Messages (sender_id, recipient_id, message_type, message_content, message_date, reply_status) VALUES (%s, %s, %s, %s, NOW(), %s)",
                               (session['id'], sender_id, 'reply_credit', message_content, 'waiting for reply'))
            cursor.execute("UPDATE Messages SET reply_status = %s WHERE message_id = %s", ('replied', request_credit_id))
        elif reply_status == 'decline' and decline_reason is not None:
           # Insert message into Messages table
           message_content = reply_status + ', ' + decline_reason
           cursor.execute("INSERT INTO Messages (sender_id, recipient_id, message_type, message_content, message_date, reply_status) VALUES (%s, %s, %s, %s, NOW(), %s)",
                               (session['id'], sender_id, 'reply_credit', message_content, 'waiting for reply'))
           cursor.execute("UPDATE Messages SET reply_status = %s WHERE message_id = %s", ('replied', request_credit_id))

        connection.commit()
        connection.close()

    return redirect(url_for('manager.manage_credit'))


@manager.route("/report", methods=['GET', 'POST'])
def customer_report():
    if 'loggedin' in session:
        # Set default start and end dates
        current_year = date.today().year
        default_start_date_1 = f"{current_year}-01-01"
        default_end_date_1 = date.today().strftime('%Y-%m-%d')
        default_start_date_2 = f"{current_year}-01-01"
        default_end_date_2 = date.today().strftime('%Y-%m-%d')

        # Initialize start and end dates with default values
        start_date_1 = default_start_date_1
        end_date_1 = default_end_date_1
        start_date_2 = default_start_date_2
        end_date_2 = default_end_date_2

        if request.method == 'POST':
            # Get user-provided start and end dates for first chart
            start_date_1 = request.form.get('start_date_1', default_start_date_1)
            end_date_1 = request.form.get('end_date_1', default_end_date_1)
            # Get user-provided start and end dates for second chart
            start_date_2 = request.form.get('start_date_2', default_start_date_2)
            end_date_2 = request.form.get('end_date_2', default_end_date_2)

        cursor, connection = get_cursor()
        
        # Generate data for the first chart
        cursor.execute("SELECT * FROM Orders WHERE status = 'Completed' AND order_date BETWEEN %s AND %s;", (start_date_1, end_date_1))
        payments_completed_1 = cursor.fetchall()
        total_completed_1 = sum(item[3] if item[3] is not None else decimal.Decimal(0) for item in payments_completed_1)
        
        cursor.execute("SELECT * FROM Orders WHERE status != 'Completed' AND status != 'Cancelled' AND order_date BETWEEN %s AND %s;", (start_date_1, end_date_1))
        payments_other_1 = cursor.fetchall()
        total_other_1 = sum(item[3] if item[3] is not None else decimal.Decimal(0) for item in payments_other_1)
        
        cursor.execute("SELECT * FROM Orders WHERE status = 'Cancelled' AND order_date BETWEEN %s AND %s;", (start_date_1, end_date_1))
        payments_cancelled_1 = cursor.fetchall()
        total_cancelled_1 = sum(item[3] if item[3] is not None else decimal.Decimal(0) for item in payments_cancelled_1)

        fig1 = go.Figure()
        fig1.add_trace(go.Pie(
            labels=['Completed orders', 'Processing orders', 'Cancelled orders'],
            values=[total_completed_1, total_other_1, total_cancelled_1],
            name='Total Revenue',
            text=[f'${total_completed_1}', f'${total_other_1}', f'${total_cancelled_1}'],
            textposition='inside',
            marker_colors=['lightblue', 'lightcoral', 'lightgreen']
        ))
        fig1.update_layout(
            width=800,
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        plot_div1 = plot(fig1, output_type='div', include_plotlyjs=True)

        # Generate data for the second chart
        query = """SELECT parent_category_id, SUM(quantity) as total_quantity, Categories.name 
                   FROM Orders 
                   LEFT JOIN Order_Details ON Orders.order_id = Order_Details.order_id 
                   LEFT JOIN Products ON Order_Details.product_id = Products.product_id 
                   LEFT JOIN Categories ON Products.category_id = Categories.category_id
                   WHERE Orders.status = 'Completed' AND order_date BETWEEN %s AND %s
                   GROUP BY parent_category_id, Categories.name;"""
        cursor.execute(query, (start_date_2, end_date_2))
        sale_result = cursor.fetchall()

        # Extract category names and total quantities from the query result
        categories = [row[2] for row in sale_result]  # Categories.name is the third column in the query
        total_quantities = [row[1] for row in sale_result]  # total_quantity is the second column in the query

        # Create the second chart
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=categories,
            y=total_quantities,
            name='Total Quantity',
            text=[f'{qty}' for qty in total_quantities],
            textposition='outside',
            marker_color='lightblue',
            marker_line_color='black',
            marker_line_width=1,
            width=0.5
        ))
        fig2.update_layout(
            xaxis_title='Category',
            yaxis_title='Total Quantity',
            width=800,
            height=400,
            bargap=0.2,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        plot_div2 = plot(fig2, output_type='div', include_plotlyjs=True)

        return render_template('report.html', plot_div1=plot_div1, plot_div2=plot_div2, 
                               default_start_date_1=default_start_date_1, default_end_date_1=default_end_date_1, 
                               default_start_date_2=default_start_date_2, default_end_date_2=default_end_date_2)

    # User is not logged in, redirect to login page
    return redirect(url_for('login.login_page'))



# Manage credit limit
@manager.route("/manage_account")
def manage_account():
    if 'loggedin' in session:
        cursor, connection = get_cursor()
        cursor.execute('''
            SELECT customer_id, CONCAT(first_name, ' ', last_name) AS full_name, remaining_credit, credit_limit, status
            FROM Customer
        ''')
        customers_account = cursor.fetchall()

        cursor.close()
        connection.close()
        return render_template('manage_account.html',customers_account=customers_account )
    return redirect(url_for('login.login_page'))

@manager.route("/manage_customer_status/<id>", methods=['GET', 'POST'])
def manage_customer_status(id):
    if 'loggedin' in session:
        new_status = request.form['status']
        cursor, connection = get_cursor()
        
        cursor.execute('''
            UPDATE Customer
            SET status = %s
            WHERE customer_id = %s
        ''', (new_status, id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return redirect(url_for('manager.manage_account'))
    return redirect(url_for('login.login_page'))

@manager.route("/modify_credit_limit/<int:id>", methods=["POST"])
def modify_credit_limit(id):
    if 'loggedin' in session:
        new_credit_limit = request.form['new_credit_limit']
        cursor, connection = get_cursor()
        
        cursor.execute('''
            UPDATE Customer
            SET credit_limit = %s
            WHERE customer_id = %s
        ''', (new_credit_limit, id))

        # Check if the account exists for the customer
        cursor.execute('''
            SELECT account_id FROM Accounts WHERE customer_id = %s
        ''', (id,))
        account = cursor.fetchone()

        if account:
            # Update the credit limit if the account exists
            cursor.execute('''
                UPDATE Accounts
                SET credit_limit = %s
                WHERE customer_id = %s
            ''', (new_credit_limit, id))
        else:
            # Insert a new account if it doesn't exist
            cursor.execute('''
                INSERT INTO Accounts (customer_id, credit_limit, outstanding_balance, invoice_due_date, invoice_frequency)
                VALUES (%s, %s, 0.00, NULL, NULL)
            ''', (id, new_credit_limit))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return redirect(url_for('manager.manage_account'))
    return redirect(url_for('login.login_page'))
