from worldwaytravel import app
import re
from worldwaytravel import Blueprint
from .database import get_cursor
from flask import Blueprint, session, url_for, render_template, redirect, request, flash, current_app
from flask_hashing import Hashing
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from decimal import Decimal
from datetime import datetime, timedelta, date

customer = Blueprint("customer", __name__, static_folder="static", 
                       template_folder="templates")

hashing = Hashing(app)

@customer.route("/")
def customer_profile():
    # Check if user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor, connection = get_cursor() 

        customer_id = session['id']
        if customer_id in app.config['flash_messages']:
            for msg in app.config['flash_messages'][customer_id]:
                flash(msg, 'success')
            del app.config['flash_messages'][customer_id]
        
        # Fetch user account info
        cursor.execute('SELECT * FROM User WHERE user_id = %s', (session['id'],))
        account = cursor.fetchone()

        cursor.execute('''
            SELECT o.order_id, o.order_date, o.total_cost, o.status
            FROM Orders o
            WHERE o.customer_id = %s AND o.status != 'Pending' order by o.order_id desc
        ''', (session['id'],))
        order_history = cursor.fetchall()

        # Execute the query to select the setting
        # cursor.execute("SELECT value FROM Loyalty_Settings WHERE setting = 'redemption'")
        # setting = cursor.fetchone()[0]
        #cursor.fetchall()
        
        # Fetch membership info for the user
        cursor.execute('SELECT * FROM Customer WHERE customer_id = %s', (session['id'],))
        customer_info = cursor.fetchone()

        # remaining_credit_percent = (customer_info[10] / customer_info[9]) * 100
        # remaining_point_percent = (customer_info[8] / setting) * 100

        image_name = customer_info[11] if customer_info[11] else None
        image_path = url_for('static', filename='uploads/' + image_name) if image_name else None

         # Check if account exists
        cursor.execute('''
            SELECT account_id
            FROM Accounts
            WHERE customer_id = %s
        ''', (session['id'],))
        account_info = cursor.fetchone()

        account_status = bool(account_info)  # Convert account_info to a boolean value

        # Check if there is already an apply_credit message
        cursor.execute('''
            SELECT COUNT(*) FROM Messages
            WHERE sender_id = %s AND message_type = 'apply_credit'
        ''', (session['id'],))
        apply_credit_exists = cursor.fetchone()[0] > 0

        # Check if the apply is replied
        cursor.execute('''
            SELECT COUNT(*) FROM Messages
            WHERE recipient_id = %s AND message_type = 'reply_credit'
        ''', (session['id'],))
        reply_credit_exists = cursor.fetchone()[0] > 0
        
        reply_status = None  # initialise reply_status variable
        # Get the reply content
        if reply_credit_exists:
            cursor.execute('''
            SELECT message_content FROM Messages
            WHERE recipient_id = %s AND message_type = 'reply_credit'
            ORDER BY message_date DESC
        ''', (session['id'],))
            replylist = cursor.fetchall()
            reply = replylist[0][0]
            reply = reply.split(',', 1)
            reply_status = reply[0]
            


        previous_statuses = {
            1: 'Pending',
            2: 'Progressing',
            # 3: 'Shipped',
            # 4: 'Delivered',
            3: 'Confirmed',
            4: 'Completed'
        }

        order_changed = {}
        for order in order_history:
            order_id = order[0]
            current_status = order[3]
            previous_status = previous_statuses.get(order_id, 'Progressing')
            order_changed[order_id] = (current_status != previous_status)


        cursor.execute('''
            SELECT message_content, message_date, 'sent' as direction
            FROM Messages
            WHERE sender_id = %s
        ''', (session['id'],))

        sent_messages = cursor.fetchall()

        cursor.execute('''
            SELECT message_content, message_date, 'received' as direction
            FROM Messages
            WHERE recipient_id = %s
        ''', (session['id'],))
        received_messages = cursor.fetchall()


        # Combine and sort messages
        messages = sent_messages + received_messages
        messages.sort(key=lambda x: x[1], reverse=True)

        cursor.close()  
        connection.close() 
        
        # Show the profile page with account info and membership info
        return render_template('customer_profile.html', account=account, customer_info=customer_info,  image_path=image_path, order_history=order_history, account_status=account_status,apply_credit_exists=apply_credit_exists, order_changed=order_changed, reply_credit_exists=reply_credit_exists,reply_status=reply_status, messages=messages)
    # User is not logged in redirect to login page
    return redirect(url_for('login.login_page'))


@customer.route("/apply_credit", methods=['GET', 'POST'])
def apply_credit():
    if 'loggedin' in session:
        if request.method == 'POST':
            cursor, connection = get_cursor()
            
            sender_id = session['id']
            recipient_id = 26  # Fixed recipient_id
            message_content = request.form.get('message', "Request to activate credit.")
            message_type = request.form.get('message_type', 'standard')
            message_date = datetime.now()
            
            # Get company information
            company_name = request.form.get('company_name')
            company_address = request.form.get('company_address')
            company_registration_number = request.form.get('company_registration_number')

            # Append company information to the message content
            message_content += f"\n\nCompany Name: {company_name}\n"
            message_content += f"Company Address: {company_address}\n"
            message_content += f"Company Registration Number: {company_registration_number}"

            cursor.execute('''
                INSERT INTO Messages (sender_id, recipient_id, message_content, message_date, message_type)
                VALUES (%s, %s, %s, %s, %s)
            ''', (sender_id, recipient_id, message_content, message_date, message_type))

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('customer.customer_profile'))
        
        # If it's a GET request, render the form
        return render_template('customer_credit.html')
    
    return redirect(url_for('login.login_page'))


@customer.route("/send_message", methods=['GET', 'POST'])
def send_message():
    if 'loggedin' in session:
        if request.method == 'POST':
            cursor, connection = get_cursor()
            
            sender_id = session['id']
            recipient_id = 16  # Fixed recipient_id
            message_content = request.form.get('message')
            message_type = request.form.get('message_type', 'standard')
            message_date = datetime.now()
            
            cursor.execute('''
                INSERT INTO Messages (sender_id, recipient_id, message_content, message_date, message_type)
                VALUES (%s, %s, %s, %s, %s)
            ''', (sender_id, recipient_id, message_content, message_date, message_type))

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('customer.customer_profile'))
        
        # If it's a GET request, render the form
        return render_template('customer_message.html')
    
    return redirect(url_for('login.login_page'))



@customer.route("/profile_edit", methods=['GET', 'POST'])
def profile_edit():
    cursor, connection = get_cursor()
    
    cursor.execute('SELECT * FROM User WHERE user_id = %s', (session['id'],))
    account = cursor.fetchone()
        
        # Fetch customer info for the user
    cursor.execute('SELECT * FROM Customer WHERE customer_id = %s', (session['id'],))
    customer_info = cursor.fetchone()
    if 'loggedin' in session:
        msg = ''
        if request.method == "POST":
            username = request.form.get('username')
            title = request.form.get('customer_title')
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            date_birth = request.form.get('date_birth')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')

            # Check if the new username is already taken
            check_username_query = '''SELECT COUNT(*) FROM User WHERE username = %s AND user_id != %s'''
            cursor.execute(check_username_query, (username, session['id']))
            result = cursor.fetchone()
            if result[0] > 0:
                msg = 'Username is already taken!'

            # Update the database
            update_user_query = "UPDATE User SET username = %s WHERE user_id = %s"
            cursor.execute(update_user_query, (username, session['id']))
                
            update_customer_query = '''
                UPDATE Customer 
                SET title = %s, first_name = %s, last_name = %s, date_birth = %s, email = %s, phone_number = %s, address = %s
                WHERE customer_id = %s
                '''
            cursor.execute(update_customer_query, (title, firstname, lastname, date_birth, email, phone, address, session['id']))


            image_url = request.files.get('image_url')
            if image_url.filename != '':
                image_path = upload(image_url)
                update_customer_query = '''
                                UPDATE Customer 
                                SET image_url=%s
                                WHERE customer_id = %s
                                '''
                cursor.execute(update_customer_query, (image_path, session['id']))

            connection.commit()
            return redirect(url_for('customer.customer_profile'))
        return render_template('customer_profile_edit.html', account=account, customer_info=customer_info, msg = msg)
    # User is not loggedin redirect to login page
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


@customer.route("/change_password", methods=["POST"])
def change_password():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))

    cursor, connection = get_cursor()
    new_password = request.form['newPassword']
    confirm_password = request.form['confirmPassword']

    if new_password != confirm_password:
        flash('New password and confirm password do not match.')
        return redirect(request.url)

    if not new_password or (len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password)):
        flash('Password must be at least 8 characters long and contain both letters and numbers.')
        return redirect(request.url)

    hashed = hashing.hash_value(new_password, salt='abcd')

    update_account_query = '''
        UPDATE User
        SET password = %s
        WHERE user_id = %s
    '''
    cursor.execute(update_account_query, (hashed, session['id']))
    connection.commit()

    flash('Your password has been successfully updated.')
    return redirect(url_for('customer.customer_profile'))

def create_or_get_order():
    cursor, connection = get_cursor()
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Check if there is a 'Pending' status order
    cursor.execute('SELECT order_id FROM Orders WHERE customer_id = %s AND status = %s', (session['id'], 'Pending'))
    pending_order = cursor.fetchone()

    if pending_order:
        # If a 'Pending' status order is found, use its order ID
        order_id = pending_order[0]
    else:
        # If no 'Pending' status order is found, create a new one
        cursor.execute('INSERT INTO Orders (customer_id, order_date, status) VALUES (%s, %s, %s)', (session['id'], current_date, 'Pending'))
        # cursor.execute('INSERT INTO Orders (customer_id, order_date, status, shipping_id) VALUES (%s, %s, %s, %s)', (session['id'], current_date, 'Pending', '1'))
        connection.commit()
        order_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return order_id


@customer.route("/view_cart", methods=["GET", "POST"])
def view_cart():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    
    cursor, connection = get_cursor()

    order_id = create_or_get_order()


    if order_id is None:
        return render_template('empty_shopping_cart.html')
    
        # Fetch user account info
    cursor.execute('SELECT status FROM Customer WHERE customer_id = %s', (session['id'],))
    account_status = cursor.fetchone()

    if account_status is None or account_status[0] == 'Inactive':
        cursor.close()
        connection.close()
        return render_template('inactive_shopping_cart.html')

    
    cursor.execute('''
        SELECT od.product_id, p.name, od.quantity, p.price as current_price, p.discount_details, p.image_url
        FROM Order_Details od 
        INNER JOIN Products p ON od.product_id = p.product_id 
        WHERE od.order_id = %s
    ''', (order_id,))
    order_details = cursor.fetchall()
    
    # update cart product price
    for detail in order_details:
        original_price = detail[3]
        discount = detail[4]
        if discount and discount != 'None' and '%' in discount:
            discount_percentage =  Decimal(discount.replace('%', ''))
            new_price = original_price * (1 - discount_percentage / Decimal('100'))
        else:
            new_price = original_price
        cursor.execute('UPDATE Order_Details SET price = %s WHERE order_id = %s AND product_id = %s', (new_price, order_id, detail[0]))

    connection.commit()

    cursor.execute('''
        SELECT od.product_id, p.name, od.quantity, od.price, p.image_url
        FROM Order_Details od 
        INNER JOIN Products p ON od.product_id = p.product_id 
        WHERE od.order_id = %s
    ''', (order_id,))
    updated_order_details = cursor.fetchall()
    connection.close()

    product_cost = sum(detail[3] * detail[2] for detail in updated_order_details)

    return render_template('shopping_cart.html', order_details=updated_order_details, product_cost=product_cost)

    
@customer.route("/add_to_cart", methods=["GET", "POST"])
def add_to_cart():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')

    quantity = float(quantity)
    
    order_id = create_or_get_order()

    cursor, connection = get_cursor()

   # check if product has discount
    cursor.execute('SELECT price, discount_details FROM Products WHERE product_id = %s', (product_id,))
    product_info = cursor.fetchone()
    original_price = product_info[0]
    discount = product_info[1]
    if discount and discount != 'None' and '%' in discount:
        discount_percentage =  Decimal(discount.replace('%', ''))
        price = original_price * (1 - discount_percentage / Decimal('100'))
    else:
        price = original_price


    # Check if the product already exists in the order details
    cursor.execute('SELECT * FROM Order_Details WHERE order_id = %s AND product_id = %s', (order_id, product_id))
    existing_product = cursor.fetchone()

    if existing_product:
        # If the product already exists, update its quantity
        new_quantity = existing_product[3] + quantity
        cursor.execute('UPDATE Order_Details SET quantity = %s, price = %s WHERE order_id = %s AND product_id = %s', (new_quantity, price, order_id, product_id))
    else:
        # If the product does not exist, insert a new order detail
        cursor.execute('INSERT INTO Order_Details (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)', (order_id, product_id, quantity, price))

    # Update total cost in the order
    cursor.execute('UPDATE Orders SET total_cost = total_cost + %s * %s WHERE order_id = %s', (price, quantity, order_id))
    
    connection.commit()
    connection.close()

    return redirect(url_for('customer.view_cart'))

@app.route("/update_quantity", methods=["POST"])
def update_quantity():
    data = request.json
    quantity = data.get("quantity")
    product_id = data.get("detailId")

    cursor, connection = get_cursor()

    cursor.execute('UPDATE Order_Details SET quantity = %s WHERE product_id = %s', (quantity, product_id))

    connection.commit()
    connection.close()

    return redirect(url_for('customer.view_cart'))

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    data = request.json
    product_id = data.get("detailId")

    cursor, connection = get_cursor()

    cursor.execute('DELETE FROM Order_Details WHERE product_id = %s', (product_id,))

    connection.commit()
    connection.close()

    return redirect(url_for('customer.view_cart'))

@customer.route("/check_out")
def check_out():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    
    cursor, connection = get_cursor()

    cursor.execute('SELECT * FROM Customer WHERE customer_id = %s', (session['id'],))
    cus_info = cursor.fetchone()
    full_name = f"{cus_info[3]} {cus_info[1]} {cus_info[2]}"

    order_id = create_or_get_order()
    
    cursor.execute('''
        SELECT od.product_id, p.name, od.quantity, od.price, p.image_url, (od.quantity * od.price) AS total_pro_price
        FROM Order_Details od 
        INNER JOIN Products p ON od.product_id = p.product_id 
        WHERE od.order_id = %s
    ''', (order_id,))
    order_checkout = cursor.fetchall()

    # cursor.execute('SELECT * FROM GiftCard WHERE customer_id = %s AND status = "Active"', (session['id'],))
    # giftcard_info = cursor.fetchall()

    cursor.execute("""
SELECT COALESCE(
(SELECT remaining_credit
FROM Customer
WHERE customer_id = %s
AND status = 'Active'
AND remaining_credit >= 0), 0) AS remaining_credit;
    """, (session['id'],))
    credit = cursor.fetchone()[0]

    connection.close()

    # Initialize total shipping cost and flag variables
    total_shipping_cost = 0  # Initialize total shipping cost to 0
    oversized_item_flag = False  # Initialize flag for oversized items to False
    standard_shipping_only = True  # Initialize flag for only standard size items to True

    # Iterate through order details
    for detail in order_checkout:
        shipping_option = detail[5]

        # If any item in the order is "Pick up only", set shipping cost to 0 as these items require customer pickup
        if shipping_option == 3:
            total_shipping_cost = 0
            break

        # If there are oversized items ("Oversized item, shipping $100"), each item incurs a $100 shipping cost
        if shipping_option == 2:
            oversized_item_flag = True

        # If there are only standard size items ("Standard shipping $10"), total shipping cost remains $10 regardless of quantity
        if shipping_option != 1:
            standard_shipping_only = False

        # If there are oversized items and not only oversized items
        if oversized_item_flag and not standard_shipping_only:
            # Calculate total shipping cost for oversized items, each oversized item incurs a $100 shipping cost
            total_oversized_shipping_cost = sum(100 * detail[2] for detail in order_checkout if detail[5] == 2)
            # Add $50 shipping cost for the first oversized item
            total_shipping_cost = total_oversized_shipping_cost + 50

    # If there are only standard size items and no oversized items, total shipping cost is $10
    if standard_shipping_only and not oversized_item_flag:
        total_shipping_cost = 10

    sub_cost = sum(detail[3] * detail[2] for detail in order_checkout)

    # total_price = round((float(sub_cost) + float(total_shipping_cost)) * 1.15, 2)
    total_price = round(float(sub_cost) * 1.15, 2)

    return render_template('products_checkout.html',order_checkout=order_checkout, cus_info=cus_info, full_name=full_name, sub_cost=sub_cost, total_shipping_cost=total_shipping_cost, total_price=total_price, credit=credit)


@customer.route("/make_payment", methods=["POST"])
def make_payment():
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    
    total_price = Decimal(request.form.get('total_price'))
    # shipping_method = request.form.get('shipping_method')
    # gift_card_id = int(request.form.get('giftCardSelect'))
    expiration_date = datetime.now() + timedelta(days=2*365)
    use_credit = int(request.form.get('useCreditSelect'))
    original_total_price = Decimal(request.form.get('original_total_price'))
    print("original_total_price: ", original_total_price)

    cursor, connection = get_cursor()
    # if gift_card_id > 0:
    #     cursor.execute('SELECT balance FROM GiftCard WHERE giftcard_id = %s', (gift_card_id,))
    #     cardBalance = cursor.fetchone()[0]
    #     if cardBalance > original_total_price:
    #         new_balance = cardBalance - original_total_price
    #         cursor.execute('''
    #             UPDATE GiftCard
    #             SET balance = %s
    #             WHERE giftcard_id = %s
    #         ''', (new_balance, gift_card_id))
    #         original_total_price = 0
    #     else:
    #         cursor.execute('''
    #             UPDATE GiftCard
    #             SET status = 'Redeemed'
    #             WHERE giftcard_id = %s
    #         ''', (gift_card_id,))
    #         original_total_price = original_total_price - cardBalance

    if use_credit == 1:
        if original_total_price > 0:
            cursor.execute("""
            SELECT remaining_credit
            FROM Customer
            WHERE customer_id = %s
                """, (session['id'],))
            credit = cursor.fetchone()[0]
            if credit > 0:
                if credit > original_total_price:
                    new_balance = credit - original_total_price
                    cursor.execute('''
                        UPDATE Customer
                        SET remaining_credit = %s
                        WHERE customer_id = %s
                    ''', (new_balance, session['id']))
                    original_total_price = 0
                else:
                    cursor.execute('''
                        UPDATE Customer
                        SET remaining_credit = 0
                        WHERE customer_id = %s
                    ''', (session['id'], ))
                    original_total_price = original_total_price - credit

    # Insert new shipping record and get the new shipping_id
    # if shipping_method == 'freight_by_request':
    #     cursor.execute('''
    #         INSERT INTO Shipping (type, cost, region, extra_fee)
    #         VALUES (%s, %s, %s, %s)
    #     ''', ('freight_by_request', 0, 'UN', 0))
    # elif shipping_method == 'pick_up':
    #     cursor.execute('''
    #         INSERT INTO Shipping (type, cost, region, extra_fee)
    #         VALUES (%s, %s, %s, %s)
    #     ''', ('pick_up', 0, 'NZ', 0))
    # else:
    #     cursor.execute('''
    #         INSERT INTO Shipping (type, cost, region, extra_fee)
    #         VALUES (%s, %s, %s, %s)
    #     ''', ('standard', shipping_method, 'NZ', 0))

    # Get the new inserted shipping_id
    # shipping_id = cursor.lastrowid
    shipping_id = 1#cursor.lastrowid

    order_id = create_or_get_order()
    cursor.execute('SELECT product_id, quantity FROM Order_Details WHERE order_id = %s', (order_id,))
    products_in_order = cursor.fetchall()

    for product in products_in_order:
        product_id, quantity_ordered = product
        cursor.execute('UPDATE Products SET stock_level = stock_level - %s WHERE product_id = %s', (quantity_ordered, product_id))

    # Update the order's status, total cost, and shipping_id
    cursor.execute('''
        UPDATE Orders 
        SET status = %s, total_cost = %s
        WHERE customer_id = %s AND status = %s
    ''', ('Progressing', total_price, session['id'], 'Pending'))

    # # Update the customer's points_balance
    # cursor.execute('''
    #     UPDATE Customer
    #     SET points_balance = points_balance + %s
    #     WHERE customer_id = %s
    # ''', (total_price, session['id'],))
    #
    # # Retrieve the updated points_balance
    # cursor.execute('''
    #     SELECT points_balance
    #     FROM Customer
    #     WHERE customer_id = %s
    # ''', (session['id'],))
    # points_balance = cursor.fetchone()[0]
    #
    #
    # if points_balance >= 1000:
    #     # Calculate the number of gift cards to be issued
    #     num_giftcards = points_balance // 1000
    #
    #     # Calculate the remaining points after issuing gift cards
    #     remaining_points = points_balance % 1000
    #
    #     # Create gift card records
    #     for _ in range(num_giftcards):
    #         cursor.execute('''
    #             INSERT INTO GiftCard (customer_id, balance, expiration_date, status)
    #             VALUES (%s, %s, %s, %s)
    #         ''', (session['id'], 10, expiration_date, 'Active'))
    #
    #     # Update points_balance with the remaining points
    #     cursor.execute('''
    #         UPDATE Customer
    #         SET points_balance = %s
    #         WHERE customer_id = %s
    #     ''', (remaining_points, session['id'],))



    connection.commit()  
    cursor.close()
    connection.close()

    return redirect(url_for('customer.customer_profile'))


@customer.route('/order_detail/<int:order_id>')
def view_order_detail(order_id):
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    
    cursor, connection = get_cursor()

    cursor.execute('''
        SELECT od.product_id, p.name, od.quantity, od.price, p.image_url, 
                (od.quantity * od.price) AS total_pro_price
        FROM Order_Details od 
        INNER JOIN Products p ON od.product_id = p.product_id 
        WHERE od.order_id = %s
    ''', (order_id,))
    order_details = cursor.fetchall()

    cursor.execute('''
        SELECT o.order_id, o.order_date, o.total_cost, o.status, o.status_change_date
        FROM Orders o
        WHERE o.order_id = %s
    ''', (order_id,))
    order_info = cursor.fetchall()

    cursor.close()
    connection.close()

    if isinstance(order_info[0][1], (datetime, date)):
        order_date = datetime.combine(order_info[0][1], datetime.min.time()) if isinstance(order_info[0][1], date) else order_info[0][1]
    else:
        order_date = datetime.strptime(order_info[0][1], '%d-%m-%Y')

    if isinstance(order_info[0][4], (datetime, date)):
        status_change_date = datetime.combine(order_info[0][4], datetime.min.time()) if isinstance(order_info[0][4], date) else order_info[0][4]
    else:
        status_change_date = datetime.now() if order_info[0][4] is None else datetime.strptime(order_info[0][4], '%d-%m-%Y')


    # if order_info[0][4] == 'pick_up':
    #     status_list = ['Pending', 'Progressing', 'Delivered', 'Completed', 'Cancelled']
    # else:
    #     status_list = ['Pending', 'Progressing', 'Shipped', 'Delivered', 'Completed', 'Cancelled']

    status_list = ['Pending', 'Progressing', 'Confirmed', 'Completed', 'Cancelled']
    
    current_date = datetime.now().date()
    current_status = order_info[0][3]
    current_status_index = status_list.index(current_status)
    
    status_dates = {status: None for status in status_list}

    status_dates['Pending'] = order_date
    status_dates['Progressing'] = order_date

    if order_id in current_app.config['status_change_dates']:
        for status, change_date in current_app.config['status_change_dates'][order_id].items():
            if status in status_dates:
                status_dates[status] = change_date

    for index, status in enumerate(status_list):
        if status_dates[status] is None:
            if index <= current_status_index:
                status_dates[status] = status_change_date - timedelta(days=current_status_index - index)
            else:
                status_dates[status] = status_change_date + timedelta(days=index - current_status_index)
    
    

    

    return render_template('customer_order_detail.html', order_info=order_info, order_details=order_details, order_status=current_status, order_date=order_date, status_dates=status_dates, current_date=current_date, timedelta=timedelta, status_change_date=status_change_date, status_list=status_list)


@customer.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if 'loggedin' not in session:
        return redirect(url_for('login.login_page'))
    cursor, connection = get_cursor()
    # fetch total cost
    cursor.execute("SELECT total_cost FROM Orders WHERE order_id = %s", (order_id,))
    total_cost = cursor.fetchone()[0]

    cursor.execute("SELECT order_date FROM Orders WHERE order_id = %s", (order_id,))
    order_date = cursor.fetchone()[0]
    # update inventory
    cursor.execute("SELECT product_id, quantity, price FROM Order_Details WHERE order_id = %s", (order_id,))
    order_details = cursor.fetchall()
    for detail in order_details:
        product_id = detail[0]
        quantity = detail[1]
        cursor.execute("UPDATE Products SET stock_level = stock_level + %s WHERE product_id = %s", (quantity, product_id))
    

    # return points
    # cursor.execute("SELECT points_balance FROM Customer WHERE customer_id = %s", (session['id'],))
    # current_points = cursor.fetchone()[0]
    #
    # new_points = current_points - total_cost
    # while new_points < 0:
    #     new_points += 1000
    #
    # cursor.execute("UPDATE Customer SET points_balance = %s WHERE customer_id = %s", (new_points, session['id']))

    # return as credit

    cursor.execute("UPDATE Customer SET remaining_credit = remaining_credit + %s WHERE customer_id = %s", (total_cost, session['id']))
    

    # delete giftcard if already get from cancelled order
    # giftcard_expiration_date = order_date + timedelta(days=2*365)
    # cursor.execute("SELECT giftcard_id, balance, expiration_date FROM GiftCard WHERE customer_id = %s AND status = 'Active'", (session['id'],))
    # giftcards = cursor.fetchall()
    
    # for giftcard in giftcards:
    #     giftcard_id = giftcard[0]
    #     balance = giftcard[1]
    #     giftcard_issue_date = giftcard[2]
    #     if (giftcard_issue_date - giftcard_expiration_date).days < 1 and balance == 10:
    #         cursor.execute("UPDATE GiftCard SET status = 'Expired' WHERE giftcard_id = %s", (giftcard_id,))
    #
    # # return refunds by giftcard
    # expiration_date = datetime.now() + timedelta(days=3*365)
    # cursor.execute("INSERT INTO GiftCard (customer_id, balance, expiration_date, status) VALUES (%s, %s, %s, 'Active')", (session['id'], total_cost, expiration_date))

    # update status as cancelled
    status_change_date = datetime.now()
    
    update_query = "UPDATE Orders SET status = %s, status_change_date = NOW() WHERE order_id = %s"
    cursor.execute(update_query, ('Cancelled', order_id))


    connection.commit()
    cursor.close()
    connection.close()

    flash(f"Order {order_id} is cancelled! Your refund is returned as a Credit  in your account!", 'success')
    return redirect(url_for('customer.customer_profile', order_id=order_id, status_change_date=status_change_date))


