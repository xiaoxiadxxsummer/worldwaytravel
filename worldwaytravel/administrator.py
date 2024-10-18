from worldwaytravel import app
from worldwaytravel import Blueprint
from flask import Blueprint, session, render_template, redirect, url_for, request, flash
from .database import get_cursor
import re
from flask_hashing import Hashing
from werkzeug.utils import secure_filename
import os

administrator = Blueprint("administrator", __name__, static_folder="static", 
                       template_folder="templates")

hashing = Hashing(app)

# Administrator dashbord
@administrator.route("/")
def admin_dashboard():
    # Check if user is logged in
    if 'loggedin' in session:
        user_role = session.get('role', None)
        user_id = session.get('id', None)  
        return render_template('admin_dashboard.html')
    return redirect(url_for('login.login_page'))

@administrator.route("/profile")
def admin_profile():
    # Check if user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        user_role = session.get('role', None)
        user_id = session.get('id', None)
        cursor, connection = get_cursor() 
        
        # Fetch user account info
        cursor.execute('SELECT * FROM User WHERE user_id = %s', (session['id'],))
        account = cursor.fetchone()
        
        # Fetch administrator info for the user
        cursor.execute('SELECT * FROM SystemAdministrator WHERE admin_id = %s', (session['id'],))
        admin_info = cursor.fetchone()  
        return render_template('admin_profile.html', account = account, admin_info = admin_info)
    return redirect(url_for('login.login_page'))

# Fuction for admin update its own profile
@administrator.route("/updateadmin", methods=['GET', 'POST'])
def update_admin():
    cursor, connection = get_cursor()
    
    cursor.execute('SELECT * FROM User WHERE user_id = %s', (session['id'],))
    account = cursor.fetchone()
        
    # Fetch administrator info for the user
    cursor.execute('SELECT * FROM SystemAdministrator WHERE admin_id = %s', (session['id'],))
    admin_info = cursor.fetchone()
    if 'loggedin' in session:
        msg = ''
        if request.method == "POST":
            username = request.form.get('username')
            title = request.form.get('title')
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            joindate = request.form.get('joindate')
            status = request.form.get('status')

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
                               UPDATE SystemAdministrator
                               SET image_url=%s
                               Where admin_id=%s
                               ''',(filename,session['id'])

                ) 
            # Check if the new username is already taken
            check_username_query = '''SELECT COUNT(*) FROM User WHERE username = %s AND user_id != %s'''
            cursor.execute(check_username_query, (username, session['id']))
            result = cursor.fetchone()
            if result[0] > 0:
                msg = 'Username is already taken!'
            
            # Update the database
            update_user_query = "UPDATE User SET username = %s WHERE user_id = %s"
            cursor.execute(update_user_query, (username, session['id']))
                
            update_admin_query = '''
                UPDATE SystemAdministrator 
                SET title = %s, first_name = %s, last_name = %s, email = %s, phone_number = %s, date_join= %s, status = %s 
                WHERE admin_id = %s
                '''
            cursor.execute(update_admin_query, (title, firstname, lastname, email, phone, joindate, status, session['id']))
                
            connection.commit()
            return redirect(url_for('administrator.admin_profile'))
        return render_template('update_admin.html', account=account, admin_info=admin_info, msg = msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login.login_page'))

# Administrator update its account password
@administrator.route("/changepassword", methods=["POST"])
def change_password():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))

    cursor, connection = get_cursor()
    new_password = request.form['newPassword']
    confirm_password = request.form['confirmPassword']

    if new_password != confirm_password:
        flash('New password and confirm password do not match.')
        return redirect(url_for('administrator.admin_profile'))

    if not new_password or (len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password)):
        flash('Password must be at least 8 characters long and contain both letters and numbers.')
        return redirect(url_for('administrator.admin_profile'))

    hashed = hashing.hash_value(new_password, salt='abcd')

    update_account_query = '''
        UPDATE User
        SET password = %s
        WHERE user_id = %s
    '''
    cursor.execute(update_account_query, (hashed, session['id']))
    connection.commit()

    flash('Your password has been successfully updated.')
    return redirect(url_for('administrator.admin_profile'))


# Administrator manage category
@administrator.route("/managecategory", methods=['GET', 'POST'])
def manage_category():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))

    cursor, connection = get_cursor()
    cursor.execute("SELECT * FROM Categories WHERE parent_category_id IS NULL")
    main_categories = cursor.fetchall()
    cursor.execute("SELECT * FROM Categories WHERE parent_category_id IS NOT NULL")
    sub_categories = cursor.fetchall()
    
    return render_template('manage_category.html', main_categories=main_categories, sub_categories=sub_categories)   

@administrator.route('/add_main_category', methods=['GET', 'POST'])
def add_main_category():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        main_category_name = request.form['main_category_name']
        cursor, connection = get_cursor()
        cursor.execute("INSERT INTO Categories (name, parent_category_id) VALUES (%s, NULL)",(main_category_name,))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Main category added successfully!', 'success')
        return redirect(url_for('administrator.manage_category'))
    return redirect(url_for('administrator.manage_category'))
    
@administrator.route('/add_sub_category', methods=['GET', 'POST'])
def add_sub_category():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        sub_category_name = request.form['sub_category_name']
        parent_category_id = request.form['parent_category_id']
        cursor, connection = get_cursor()
        cursor.execute("INSERT INTO Categories (name, parent_category_id) VALUES (%s, %s)",(sub_category_name,parent_category_id))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Sub-Category added successfully!', 'success')
        return redirect(url_for('administrator.manage_category'))
    return redirect(url_for('administrator.manage_category'))

@administrator.route('/update_main_category', methods=['GET', 'POST'])
def update_main_category():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        main_category_id = request.form['id']
        main_category_name = request.form['new_name']
        cursor, connection = get_cursor()
        cursor.execute("UPDATE Categories SET name = %s WHERE category_id = %s",(main_category_name, main_category_id))
        
        connection.commit()
        cursor.close()
        connection.close()

        flash('Main category updated successfully!', 'success')
        return redirect(url_for('administrator.manage_category'))
    return redirect(url_for('administrator.manage_category'))
    
@administrator.route('/update_sub_category', methods=['GET', 'POST'])
def update_sub_category():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        sub_category_id = request.form['id']
        sub_category_name = request.form['new_name']
        parent_category_id = request.form['parent_category_id']
        cursor, connection = get_cursor()
        cursor.execute("UPDATE Categories SET name = %s, parent_category_id = %s WHERE category_id = %s",(sub_category_name,parent_category_id, sub_category_id))
        
        connection.commit()
        cursor.close()
        connection.close()

        flash('Sub_category updated successfully!', 'success')
        return redirect(url_for('administrator.manage_category'))
    return redirect(url_for('administrator.manage_category'))   

@administrator.route('/delete_main_category/<id>', methods=['GET', 'POST'])
def delete_main_category(id):
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        cursor, connection = get_cursor()
        cursor.execute("SELECT COUNT(*) FROM Categories WHERE parent_category_id = %s", (id,))
        count = cursor.fetchone()[0]
        if count > 0:
            flash('Main category cannot be deleted as it has associated sub_categories.', 'error')
        else:
            cursor.execute("DELETE FROM Categories WHERE category_id = %s", (id,))
            connection.commit()
            flash('Main category deleted successfully!', 'success')
        cursor.close()
        connection.close()
        return redirect(url_for('administrator.manage_category'))
    return redirect(url_for('administrator.manage_category'))
    
@administrator.route('/delete_sub_category/<id>', methods=['GET', 'POST'])
def delete_sub_category(id):
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        cursor, connection = get_cursor()
        cursor.execute("SELECT COUNT(*) FROM Products WHERE category_id = %s", (id,))
        count = cursor.fetchone()[0]
        if count > 0:
            flash('Sub-category cannot be deleted as it has associated products.', 'error')
        else:
            cursor.execute("DELETE FROM Categories WHERE category_id = %s", (id,))
            connection.commit()
            flash('Sub-category deleted successfully!', 'success')
        cursor.close()
        connection.close()
        return redirect(url_for('administrator.manage_category'))
    return redirect(url_for('administrator.manage_category'))

# Administrator manage shipping options
@administrator.route("/manageshipping", methods=['GET', 'POST'])
def manage_shipping():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))

    cursor, connection = get_cursor()
    cursor.execute("SELECT * FROM Shipping_Options")
    shipping_options = cursor.fetchall()
    
    return render_template('manage_shipping.html', shipping_options=shipping_options)   

@administrator.route('/add_shipping_option', methods=['GET', 'POST'])
def add_shipping_option():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        type = request.form['type']
        cost = request.form['cost']
        description = request.form['description']
        cursor, connection = get_cursor()
        cursor.execute("INSERT INTO Shipping_Options (type, cost, description) VALUES (%s, %s,%s)",(type,cost,description))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Shipping option added successfully!', 'success')
        return redirect(url_for('administrator.manage_shipping'))
    return redirect(url_for('administrator.manage_shipping'))
    


@administrator.route('/update_shipping_option', methods=['GET', 'POST'])
def update_shipping_option():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        shipping_options_id = request.form['id']
        type = request.form['new_type']
        cost = request.form['new_cost']
        description = request.form['new_description']
        cursor, connection = get_cursor()
        cursor.execute("UPDATE Shipping_Options SET type = %s, cost=%s, description=%s WHERE shipping_options_id = %s",(type,cost,description,shipping_options_id))
        
        connection.commit()
        cursor.close()
        connection.close()

        flash('Shipping option updated successfully!', 'success')
        return redirect(url_for('administrator.manage_shipping'))
    return redirect(url_for('administrator.manage_shipping'))
    
    
@administrator.route('/delete_shipping_option/<id>', methods=['GET', 'POST'])
def delete_shipping_option(id):
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        cursor, connection = get_cursor()
        cursor.execute("SELECT COUNT(*) FROM Products WHERE shipping_option = %s", (id,))
        count = cursor.fetchone()[0]
        if count > 0:
            flash('Shipping option cannot be deleted as it has associated products.', 'error')
        else:
            cursor.execute("DELETE FROM Shipping_Options WHERE shipping_options_id = %s", (id,))
            connection.commit()
            flash('Shipping option deleted successfully!', 'success')
        cursor.close()
        connection.close()
        return redirect(url_for('administrator.manage_shipping'))
    return redirect(url_for('administrator.manage_shipping'))