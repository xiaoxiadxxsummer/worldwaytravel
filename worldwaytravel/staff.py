from worldwaytravel import app
from worldwaytravel import Blueprint

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify,current_app
from flask_hashing import Hashing
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, date, time
import os
import re
from . import connect
from .database import get_cursor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from decimal import Decimal


staff = Blueprint("staff", __name__, static_folder="static", 
                       template_folder="templates")

hashing = Hashing(app)

app.config['flash_messages'] = {}

if 'status_change_dates' not in app.config:
    app.config['status_change_dates'] = {}

@staff.route('/')
def staff_dashboard():
    if 'loggedin' in session: # Ensuring the user is a logged-in staff
        user_role = session.get('role', None)
        user_id = session.get('id', None)
        cursor, connection = get_cursor() 

        #Fetch staff profile info
        cursor.execute('SELECT * FROM Staff WHERE staff_id = %s', (session['id'],))
        staff_profile = cursor.fetchone()

         
        #Fetch user account info
        cursor.execute('SELECT * FROM User WHERE user_id = %s',(session['id'],))
        staff_info = cursor.fetchone()

        cursor.close()  
        connection.close() 
        

        return render_template('staff_dashboard.html',staff_info = staff_info, staff_profile = staff_profile)
    return redirect(url_for('login.login_page'))


@staff.route('/profile')
def staff_profile():
    if 'loggedin' in session: # Ensuring the user is a logged-in staff
        user_role = session.get('role', None)
        user_id = session.get('id', None)
        cursor, connection = get_cursor() 

        #Fetch staff profile info
        cursor.execute('SELECT * FROM Staff WHERE staff_id = %s', (session['id'],))
        staff_profile = cursor.fetchone()

        

        #Fetch user account info
        cursor.execute('SELECT * FROM User WHERE user_id = %s',(session['id'],))
        staff_info = cursor.fetchone()

        cursor.close()  
        connection.close() 


        return render_template('staff_profile.html',staff_info = staff_info, staff_profile = staff_profile)
    else:
        return redirect(url_for('login.login_page'))

@staff.route('/staff/staff_profile_edit', methods=['GET', 'POST'])
def staff_profile_edit():
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
                               UPDATE Staff
                               SET title=%s, first_name=%s, last_name=%s, phone_number=%s, email=%s, image_url=%s
                            WHERE staff_id=%s
                           ''', (title, first_name, last_name, phone_number, email, image_path, user_id))

            else:

                #update staff info
                cursor.execute('''
                                UPDATE Staff
                                SET title=%s, first_name=%s, last_name=%s, phone_number=%s, email=%s
                                WHERE staff_id=%s
                           ''', (title, first_name, last_name, phone_number, email, user_id))
            flash('Profile updated successfully', 'success')
            return redirect(url_for('staff.staff_profile', image_path=image_path))
        else:
            cursor.execute('SELECT * FROM User WHERE user_id = %s',(session['id'],))
            staff_info = cursor.fetchone()
            #fetch current staff profile for edit
            cursor.execute('SELECT * FROM Staff WHERE staff_id = %s', (session['id'],))
            staff_profile = cursor.fetchone()


            cursor.close()  
            connection.close() 

            return render_template('staff_profile_edit.html', staff_profile=staff_profile, staff_info=staff_info)
    else:
        return redirect(url_for('login.login_page'))
    
def upload(file):
    if file and file.filename:
                filename = secure_filename(file.filename)
                uploads_dir =os.path.join(current_app.root_path,'static','uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                filepath = os.path.join(uploads_dir, filename)
                file.save(filepath.replace("\\", "/"))
                return filename
    




@staff.route("/change_password", methods=["POST"])
def change_password():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))

    cursor, connection = get_cursor()
    new_password = request.form['newPassword']
    confirm_password = request.form['confirmPassword']

    if new_password != confirm_password:
        flash('New password and confirm password do not match.')
        return redirect(url_for('staff.staff_profile'))

    if not new_password or (len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password)):
        flash('Password must be at least 8 characters long and contain both letters and numbers.')
        return redirect(url_for('staff.staff_profile'))

    hashed = hashing.hash_value(new_password, salt='abcd')

    update_account_query = '''
        UPDATE User
        SET password = %s
        WHERE user_id = %s
    '''
    cursor.execute(update_account_query, (hashed, session['id']))
    connection.commit()

    flash('Your password has been successfully updated.')
    return redirect(url_for('staff.staff_profile'))


@staff.route('/staff_products')
def staff_products():
     if 'loggedin' in session: # Ensuring the user is a logged-in staff
        user_role = session.get('role', None)
        user_id = session.get('id', None)
        cursor, connection = get_cursor() 
        
        cursor.execute("SELECT * FROM Categories WHERE parent_category_id IS NULL")
        main_categories = cursor.fetchall()
        cursor.execute("SELECT * FROM Categories WHERE parent_category_id IS NOT NULL")
        sub_categories = cursor.fetchall()
        
        cursor.execute("SELECT * FROM Products ")
        products = cursor.fetchall()
        print(products)
        # cursor.execute("SELECT * FROM Shipping_Options")
        # shipping_options = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('staff_products.html', main_categories=main_categories, sub_categories=sub_categories, products=products)
     return redirect(url_for('login.login_page'))

@staff.route('/subcategories/<int:parent_category_id>')
def get_subcategories(parent_category_id):
    cursor, connection = get_cursor()
    cursor.execute("SELECT * FROM Categories WHERE parent_category_id = %s", (parent_category_id,))
    subcategories = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(subcategories)

@staff.route('/products/<int:category_id>')
def get_products(category_id):
    cursor, connection = get_cursor()
    cursor.execute("SELECT category_id FROM Categories WHERE parent_category_id = %s", (category_id,))
    sub_category_ids = cursor.fetchall()
    if sub_category_ids:
        sub_category_ids = [str(sub[0]) for sub in sub_category_ids]
        placeholder = ', '.join(['%s']*len(sub_category_ids))

        query = """
                SELECT Products.*
                FROM Products
                WHERE category_id IN ({})""".format(placeholder)
        cursor.execute(query, sub_category_ids)
    else:
        cursor.execute("""
                SELECT Products.*
                FROM Products
                WHERE category_id = %s
                """,(category_id,))
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(products)

@staff.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    if request.method == 'POST':
        name = request.form['name']
        category_id = request.form['category_id']
        description = request.form['description']
        price = request.form['price']
        stock_level = request.form['stock_level']
        discount_details = request.form['discount_details']
        # shipping_option = request.form['shipping_option']
        status = request.form['status']
        image_file = request.files.get('image_url')
        if image_file and image_file.filename:
            image_path = upload_file(image_file)
        else:
            image_path = None


        cursor, connection = get_cursor()
        cursor.execute("INSERT INTO Products (name, category_id, description, price, stock_level, image_url, discount_details, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (name, category_id, description, price, stock_level, image_path, discount_details, status))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Product added successfully!', 'success')
        return redirect(url_for('staff.staff_products'))
    
def upload_file(file):
    if file and file.filename:
                filename = secure_filename(file.filename)
                uploads_dir =os.path.join(current_app.root_path,'static','producting')
                os.makedirs(uploads_dir, exist_ok=True)
                filepath = os.path.join(uploads_dir, filename)
                file.save(filepath.replace("\\", "/"))
                return filename
    
@staff.route('/edit_product', methods=['POST'])
def edit_product():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    product_id = request.form['product_id']
    name = request.form['name']
    category_id = request.form['category_id']
    description = request.form['description']
    price = request.form['price']
    stock_level = request.form['stock_level']
    discount_details = request.form['discount_details']
    # shipping_option = request.form['shipping_option']
    status = request.form['status']
    image_file = request.files.get('image_url')

    cursor, connection = get_cursor()
    if image_file and image_file.filename:
        image_path = upload_file(image_file)
    else:
        cursor.execute("SELECT image_url FROM Products WHERE product_id = %s", (product_id,))
        image_path = cursor.fetchone()[0]

    
    cursor.execute("UPDATE Products set name=%s, category_id=%s, description=%s, price=%s, stock_level=%s, image_url=%s, discount_details=%s, status=%s WHERE product_id=%s",
                   (name, category_id, description, price, stock_level, image_path, discount_details, status, product_id))
    connection.commit()
    cursor.close()
    connection.close()

    flash('Product edited successfully!', 'success')
    return redirect(url_for('staff.staff_products'))



@staff.route('/soldout_product', methods=['POST'])
def soldout_product():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    
    product_id = request.form['product_id']
    cursor,connection = get_cursor()
    cursor.execute('''
                   UPDATE Products SET Status=%s WHERE product_id=%s
                   ''',('Unavailable', product_id)
                   )
    connection.commit()
    cursor.close()
    connection.close()

    flash('Product edited successfully!', 'success')
    return redirect(url_for('staff.staff_products'))

@staff.route('/delete_product', methods=['POST'])
def delete_product():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    
    product_id = request.form['product_id']
    cursor,connection = get_cursor()
    cursor.execute('''
                   DELETE FROM Products WHERE product_id=%s
                   ''',(product_id,)
                   )
    connection.commit()
    cursor.close()
    connection.close()

    flash('Product deleted successfully!', 'success')
    return redirect(url_for('staff.staff_products'))

def update_discount_for_main_category(main_category_id, discount):
    cursor, connection = get_cursor()
    try:
        cursor.execute('SELECT category_id FROM Categories WHERE parent_category_id = %s', (main_category_id,))
        sub_category_ids = [row[0] for row in cursor.fetchall()]

        if sub_category_ids:
            placeholders = ','.join(['%s'] * len(sub_category_ids))
            cursor.execute(f'UPDATE Products SET discount_details = %s WHERE category_id IN ({placeholders})', [discount] + sub_category_ids)
            connection.commit()
    finally:
        cursor.close()
        connection.close()

@staff.route('/update_category_discount', methods=['POST'])
def update_category_discount():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    try:
        main_category_id = request.form['main_category_id']
        discount = request.form['discount']
        update_discount_for_main_category(main_category_id, discount)
        flash('Discount updated successfully!', 'success')
    except Exception as e:
        flash(f'An error occured: {str(e)}', 'error')
    return redirect(url_for('staff.staff_products'))



@staff.route('/staff_inventory')
def staff_inventory():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))

    search_query = request.args.get('search', '')
    if search_query=='':
        search_query = '%'

    cursor, connection = get_cursor()
    base_query = """
                    SELECT p.product_id, p.name, p.stock_level, p.status,
                            COALESCE(SUM(CASE WHEN o.status = 'Progressing' THEN d.quantity ELSE 0 END), 0) AS progressing,
                            (p.stock_level + COALESCE(SUM(CASE WHEN o.status = 'Progressing' THEN d.quantity ELSE 0 END),0)) AS total_stock
                    FROM Products p
                    LEFT JOIN Order_Details d ON p.product_id = d.product_id
                    LEFT JOIN Orders o ON d.order_id = o.order_id
                """

    if search_query:
        sql_query = base_query + " WHERE p.product_id LIKE %s OR p.name LIKE %s GROUP BY p.product_id, p.name, p.stock_level, p.status"
        search_like = f"%{search_query}%"
        cursor.execute(sql_query, (search_like, search_like))
    else:
        sql_query = base_query + " GROUP BY p.product_id, p.name, p.stock_level, p.status"
        cursor.execute(sql_query)
    products = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    return render_template('staff_inventory.html', products=products)


@staff.route('/update_stock', methods=['POST'])
def update_stock():
    product_id = request.form.get('product_id')
    stock_level = request.form.get('stock_level', 0)

    try:
        stock_level = int(stock_level)
    except ValueError:
        flash('Invalid input for Seating Number', 'error')
        return redirect(url_for('staff.staff_inventory'))

    cursor, connection = get_cursor()
    cursor.execute("UPDATE Products SET stock_level = %s WHERE product_id = %s", (stock_level, product_id))
    connection.commit()
    flash('Seating Number updated successfully!', 'success')
    cursor.close()
    connection.close()

    return redirect(url_for('staff.staff_inventory'))

@staff.route('/add_stock', methods=['POST'])
def add_stock():
    product_id = request.form.get('product_id')
    additional_stock = request.form.get('additional_stock', type=int, default=0)

    cursor, connection = get_cursor()
    cursor.execute("SELECT stock_level FROM Products WHERE product_id = %s", (product_id,))
    current_stock = cursor.fetchone()[0]
    new_stock = current_stock + additional_stock
    cursor.execute("UPDATE Products SET stock_level = %s WHERE product_id = %s", (new_stock, product_id))
    connection.commit()
    flash('Seating Number updated successfully!', 'success')
    cursor.close()
    connection.close()

    return redirect(url_for('staff.staff_inventory'))

@staff.route('/orders')
def orders():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    search_query = request.args.get('search', '')
    status = request.args.get('status', 'All')
    cursor, connection = get_cursor()
    order_query = """SELECT Orders.order_id, 
                        CONCAT(Customer.first_name, ' ', Customer.last_name, ' ',Customer.email) AS customer_name, 
                        Orders.order_date, 
                        Orders.total_cost, 
                        Orders.status,
                        GROUP_CONCAT(CONCAT(Products.name, ': ', Order_Details.quantity,'|', Products.image_url) SEPARATOR '; ') AS product_details
                        
                    FROM Orders
                    JOIN Customer ON Orders.customer_id = Customer.customer_id
                    LEFT JOIN Order_Details ON Orders.order_id = Order_Details.order_id
                    LEFT JOIN Products ON Order_Details.product_id = Products.product_id

                       """

    where_clauses = []
    params = []

    if status != 'All':
        where_clauses.append("Orders.status = %s")
        params.append(status)

    if search_query:
        where_clauses.append("(Orders.order_id LIKE %s OR CONCAT(Customer.first_name, ' ', Customer.last_name) LIKE %s)")
        search_like = '%' + search_query + '%'
        params.extend([search_like,search_like])
    
    if where_clauses:
        order_query += " WHERE " + " AND ".join(where_clauses)
    order_query += """ GROUP BY Orders.order_id, Customer.first_name, Customer.last_name, Orders.order_date, Orders.total_cost, Orders.status"""
    order_query += " ORDER BY Orders.order_id DESC"

    cursor.execute(order_query, params)
    orders = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('staff_orders.html', orders=orders, current_status=status)


@staff.route('/update_order_status/<int:order_id>/<new_status>', methods=['POST'])
def update_order_status(order_id, new_status):
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    cursor, connection = get_cursor()


    status_change_date = datetime.now()
    

    cursor.execute('SELECT customer_id FROM Orders WHERE order_id = %s', (order_id,))
    customer = cursor.fetchone()
    customer_id = customer[0]

    update_query = "UPDATE Orders SET status = %s, status_change_date = NOW() WHERE order_id = %s"
    cursor.execute(update_query, (new_status, order_id))

    flash_message = f"Order {order_id} is {new_status}."
    if customer_id not in app.config['flash_messages']:
        app.config['flash_messages'][customer_id] = []
    app.config['flash_messages'][customer_id].append(flash_message)

    connection.commit()
    cursor.close()
    connection.close()

    if order_id not in current_app.config['status_change_dates']:
        current_app.config['status_change_dates'][order_id] = {}
    if new_status not in current_app.config['status_change_dates'][order_id]:
        current_app.config['status_change_dates'][order_id][new_status] = status_change_date

    flash(f"Order {order_id} status updated to {new_status}.", 'success')
    return redirect(url_for('staff.orders'))


@staff.route('/view_messages', methods=['GET', 'POST'])
def view_messages():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    
    user_id = session.get('id')
    

    cursor, connection = get_cursor()

    cursor.execute('''
                SELECT c.first_name, c.last_name, m.sender_id, m.message_content, m.message_date, m.message_type, m.reply_status, r.sender_id AS reply_sender, r.message_content AS reply_content, r.message_date AS reply_date
                FROM Messages m
                JOIN Customer c ON m.sender_id = c.customer_id
                JOIN User u ON m.sender_id = u.user_id
                LEFT JOIN Messages r ON m.sender_id = r.recipient_id AND r.message_type = 'reply'
                WHERE u.role = 'customer' AND m.message_type = 'standard'
                ORDER BY 
                   CASE WHEN m.reply_status = 'waiting for reply' THEN 1 ELSE 2 END,
                   r.message_date DESC,
                   m.message_date DESC;
                ''')
    cus_messages = cursor.fetchall()

    if user_id in [16, 17, 26, 27] and request.method == 'POST':
        sender_id = request.form.get('sender_id')
        reply_content = request.form.get('reply')
        message_date = datetime.now()
        cursor.execute('''
                    SELECT message_id FROM Messages 
                    WHERE sender_id = %s AND message_type = 'standard'
                    ORDER BY message_date DESC LIMIT 1
                ''', (sender_id,))
        message_result = cursor.fetchone()
        if message_result:
            message_id = message_result[0]

            cursor.execute('''
                        INSERT INTO Messages (sender_id, recipient_id, message_content, message_date, message_type, reply_status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (user_id, sender_id, reply_content, message_date, 'reply', 'waiting for reply'))
            cursor.execute('''
                    UPDATE Messages SET reply_status = 'replied'
                    WHERE message_id = %s
                ''', (message_id,))
            connection.commit()

            flash('Reply customer successfully!', 'success')
        return redirect(url_for('staff.view_messages'))
    
    

    cursor.close()
    connection.close()

    return render_template('staff_message.html', cus_messages=cus_messages, user_id=user_id)




