from worldwaytravel import app
from .database import get_cursor
from worldwaytravel import Blueprint
from flask import Blueprint, render_template, request
from math import ceil

visitor = Blueprint("visitor", __name__, static_folder="static", 
                       template_folder="templates")

@app.context_processor
def inject_lay_categories():
    cursor, connection = get_cursor()
    cursor.execute("SELECT * FROM Categories WHERE parent_category_id IS NULL")

    lay_categories = cursor.fetchall()

    connection. close()
    return dict(lay_categories=lay_categories)


@app.route('/')
def visitor_home():
    cursor, connection = get_cursor() 

    cursor.execute('SELECT * FROM Products LIMIT 5')
    products = cursor.fetchall()


    cursor.execute('SELECT * FROM Products WHERE category_id in (1,5,6,7,8,9,10) ORDER BY stock_level asc LIMIT 8')
    china_products = cursor.fetchall()
    cursor.execute('SELECT * FROM Products WHERE category_id in (11,12,13) ORDER BY stock_level asc LIMIT 8')
    nz_products = cursor.fetchall()
    cursor.execute('SELECT * FROM Products WHERE category_id in (14,15,16,17) ORDER BY stock_level asc LIMIT 8')
    weekend_products = cursor.fetchall()
    cursor.execute('SELECT * FROM Products WHERE category_id in (18,19) ORDER BY stock_level asc LIMIT 8')
    oversea_products = cursor.fetchall()

    connection.close()
    return render_template('index.html', products=products, china_products=china_products,nz_products=nz_products,weekend_products=weekend_products,oversea_products=oversea_products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tips/<int:tip_id>')
def tips(tip_id):
    return render_template('tips.html', tip_id=str(tip_id))

@visitor.route("/product/<int:product_id>")
def view_product(product_id):
    cursor, connection = get_cursor()

    cursor.execute('''SELECT 
        Products.product_id,
        Products.name,
        Products.price,
        Products.description,
        
        Products.image_url,
        Products.stock_level,      
        Categories.category_id,
        Categories.name,
        Products.discount_details
    FROM 
        Products
    JOIN
        Categories ON Products.category_id = Categories.category_id
    
    WHERE 
        Products.product_id = %s''', (product_id,))
    product_detail = cursor.fetchone()

    connection.close()
    
    return render_template('product_details.html', product_detail=product_detail)

@visitor.route('/all_products')
def all_products():
    cursor, connection = get_cursor()

    # Get the current page number parameter
    page = request.args.get('page', 1, type=int)
    per_page = 25  # show 25 products every page

    # Get the price range from the request args
    price_range = request.args.get('price_range')

    # Get category id from request args
    category_clause = ''
    category_id = request.args.get('category_id')
    if category_id is not None: category_clause = "WHERE parent_category_id = " + category_id

    # Build the SQL query to filter products by price range
    # sql = "SELECT * FROM Products"
    sql = f"SELECT Products.*, Categories.category_id AS cat_id FROM Products LEFT JOIN Categories ON Products.category_id = Categories.category_id and Products.status = 'Available'" + category_clause

    if price_range == '0-50':
        sql += " WHERE price <= 50"
    elif price_range == '50-100':
        sql += " WHERE price > 50 AND price <= 100"        
    elif price_range == '100-200':
        sql += " WHERE price > 100 AND price <= 200"        
    elif price_range == '200-500':
        sql += " WHERE price > 200 AND price <= 500"       
    elif price_range == '500-':
        sql += " WHERE price > 500"
    
    # Get the total number of products to calculate the total number of pages
    cursor.execute(f"SELECT COUNT(*) FROM ({sql}) AS total_query")
    total_count = cursor.fetchone()[0]
    total_pages = ceil(total_count / per_page)

    # Add LIMIT and OFFSET for paging
    offset = (page - 1) * per_page
    sql += f" LIMIT {per_page} OFFSET {offset}"
    cursor.execute(sql)
    products = cursor.fetchall()

    cursor.execute("SELECT * FROM Categories WHERE parent_category_id IS NULL")
    categories = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('all_products.html', products=products, categories=categories, page=page, total_pages=total_pages, price_range=price_range)
#
# @visitor.route("/products/category/<category_id>")
# def products_by_category(category_id):
#     cursor, connection = get_cursor()
#
#     # Get the current page number parameter
#     page = request.args.get('page', 1, type=int)
#     per_page = 25  # show 25 products every page
#
#     # Get the price range from the request args
#     price_range = request.args.get('price_range')
#
#     # Build the SQL query to filter products by category and price range
#     sql = f"SELECT Products.*, Categories.category_id AS cat_id FROM Products LEFT JOIN Categories ON Products.category_id = Categories.category_id WHERE parent_category_id = {category_id}"
#
#     if price_range == '0-50':
#         sql += " AND price <= 50"
#     elif price_range == '50-100':
#         sql += " AND price > 50 AND price <= 100"
#     elif price_range == '100-200':
#         sql += " AND price > 100 AND price <= 200"
#     elif price_range == '200-500':
#         sql += " AND price > 200 AND price <= 500"
#     elif price_range == '500-':
#         sql += " AND price > 500"
#
#     # Get the total number of products to calculate the total number of pages
#     cursor.execute(f"SELECT COUNT(*) FROM ({sql}) AS total_query")
#     total_count = cursor.fetchone()[0]
#     total_pages = ceil(total_count / per_page)
#
#     # Add LIMIT and OFFSET for paging
#     offset = (page - 1) * per_page
#     sql += f" LIMIT {per_page} OFFSET {offset}"
#     cursor.execute(sql)
#     products = cursor.fetchall()
#
#     cursor.execute("SELECT * FROM Categories WHERE parent_category_id IS NULL")
#     categories = cursor.fetchall()
#
#     cursor.close()
#     connection.close()
#
#     return render_template('all_products.html', products=products, categories=categories, page=page, total_pages=total_pages, price_range=price_range)

@visitor.route('/search_products')
def search_products():
    searchterm = request.args.get('search', '')    
    searchtermupdated = f"%{searchterm}%"
    cursor, connection = get_cursor()
    
    # Get the current page number parameter
    page = request.args.get('page', 1, type=int)
    per_page = 25  # show 25 products every page

    # Select all searched products
    search_query = """SELECT * FROM Products WHERE name LIKE %s"""

    # Get the total number of products to calculate the total number of pages
    cursor.execute(f"SELECT COUNT(*) FROM ({search_query}) AS total_query", (searchtermupdated,))
    total_count = cursor.fetchone()[0]
    total_pages = ceil(total_count / per_page)

    # Add LIMIT and OFFSET for paging
    offset = (page - 1) * per_page
    search_query += f" LIMIT {per_page} OFFSET {offset}"
    cursor.execute(search_query, (searchtermupdated,))
    products = cursor.fetchall()

    return render_template('all_products.html', products=products, page=page, total_pages=total_pages, search=searchterm)


# @app.route('/products_category/<int:category_id>')
# def products_category(category_id):
#     cursor, connection = get_cursor()
#
#     cursor.execute("SELECT * FROM Products WHERE category_id IN (SELECT category_id FROM Categories WHERE parent_category_id = %s)", (category_id,))
#     products_ca = cursor.fetchall()
#
#     cursor.close()
#     connection.close()
#
#     return render_template('products_category.html', products_ca=products_ca)


@app.route('/products_onsale')
def products_onsale():
    cursor, connection = get_cursor()
    cursor.execute('SELECT * FROM Products WHERE discount_details is not null and status = "Available"')
    products_onsale = cursor.fetchall()

    cursor.execute("SELECT * FROM Categories WHERE parent_category_id IS NULL")
    lay_categories = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('products_onsale.html', products_onsale=products_onsale, lay_categories=lay_categories)