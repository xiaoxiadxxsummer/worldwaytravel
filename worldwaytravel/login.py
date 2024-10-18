import captcha,string,random
from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_hashing import Hashing
# Import the following modules
from captcha.image import ImageCaptcha
from .database import get_cursor

login = Blueprint("login", __name__, static_folder="static", 
                       template_folder="templates")

hashing = Hashing()

@login.route('/', methods=['GET', 'POST'])
def login_page():
    global captcha_text
    msg = ''
    if request.method == 'GET':
        # generate random text
        captcha_text = ''.join(random.choices(string.ascii_lowercase+string.digits, k=7))
        # Create an image instance of the given size
        image = ImageCaptcha(width=280, height=90)
        # generate the image of the given text
        data = image.generate(captcha_text)
        # write the image on the given file and save it
        image.write(captcha_text, 'worldwaytravel/static/assets/img/CAPTCHA.png')

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        user_password = request.form['password']
        cursor, connection = get_cursor()  
        cursor.execute('SELECT * FROM User LEFT JOIN Customer ON User.user_id = Customer.customer_id and Customer.status = "Active" LEFT JOIN Manager ON User.user_id = Manager.manager_id and Manager.status = "Active" LEFT JOIN Staff ON User.user_id = Staff.staff_id and Staff.status = "Active" LEFT JOIN SystemAdministrator ON SystemAdministrator.admin_id = User.user_id AND SystemAdministrator.status = "Active"  WHERE username = %s and  isnull(Customer.customer_id) + isnull(Manager.manager_id) + isnull(Staff.staff_id) + isnull(SystemAdministrator.admin_id) < 4', (username,))
        account = cursor.fetchone()
        if request.form['captcha'] == captcha_text:
            if account is not None:
                password = account[2]
                if hashing.check_value(password, user_password, salt='abcd'):
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['username'] = account[1]
                    session['role'] = account[3]
                    if session['role'] == 'Customer':
                       return redirect(url_for('visitor.all_products'))
                    elif session['role'] == 'Staff':
                       cursor.execute('SELECT * FROM Staff WHERE staff_id = %s', (session['id'],))
                       staff = cursor.fetchone()
                       if staff[8] == 'Active':
                           return redirect(url_for('staff.staff_dashboard'))
                       else:
                            msg = 'Your account is currently inactive. Please contact our administrator for assistance.'
                    elif session['role'] == 'Manager':
                       return redirect(url_for('manager.manager_dashboard'))
                    elif session['role'] == 'SystemAdministrator':
                       return redirect(url_for('administrator.admin_dashboard'))
                else:
                    msg = 'Incorrect password!'
            else:
                msg = 'Incorrect username or user is disabled!'
        else:
            msg = 'Incorrect CAPTCHA!'
            # generate random text
            captcha_text = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
            # Create an image instance of the given size
            image = ImageCaptcha(width=280, height=90)
            # generate the image of the given text
            data = image.generate(captcha_text)
            # write the image on the given file and save it
            image.write(captcha_text, 'worldwaytravel/static/assets/img/CAPTCHA.png')
        cursor.close()  
        connection.close()  
    return render_template('login.html', msg=msg)

@login.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('visitor_home'))
