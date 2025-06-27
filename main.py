from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT)
                    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        price REAL)
                    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cart (
                        user_id INTEGER,
                        product_id INTEGER)
                    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('store.db')

def add_product(name, price):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
    except Exception as e:
        print("Error:", e)
    conn.close()

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('home.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            return "Username already exists"
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    user_id = int(request.form['user_id'])
    product_id = int(request.form['product_id'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cart (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
    conn.commit()
    conn.close()
    return redirect(url_for('view_cart', user_id=user_id))

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    user_id = int(request.form['user_id'])
    product_id = int(request.form['product_id'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM cart 
        WHERE rowid IN (
            SELECT rowid FROM cart 
            WHERE user_id = ? AND product_id = ? 
            LIMIT 1
        )
    ''', (user_id, product_id))
    conn.commit()
    conn.close()
    return redirect(url_for('view_cart', user_id=user_id))


@app.route('/cart/<int:user_id>')
def view_cart(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT p.id, p.name, p.price FROM products p 
                      JOIN cart c ON p.id = c.product_id WHERE c.user_id = ?''', (user_id,))
    items = cursor.fetchall()
    conn.close()
    total = sum([item[2] for item in items])
    return render_template('cart.html', cart=items, total=total, user_id=user_id)



def seed_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    if count == 0:
        products = [
            ("Apples", 30.5),
            ("Milk", 20.0),
            ("Bread", 25.0),
            ("Eggs (12 pack)", 60.0),
            ("Rice (1 kg)", 45.0),
            ("Wheat Flour (1 kg)", 38.0),
            ("Sugar (1 kg)", 34.0),
            ("Salt (1 kg)", 18.0),
            ("Potatoes (1 kg)", 22.0),
            ("Onions (1 kg)", 30.0),
            ("Bananas (6 pcs)", 35.0),
            ("Orange Juice", 55.0),
            ("Tea (250g)", 80.0),
            ("Coffee (200g)", 120.0),
            ("Butter (100g)", 50.0),
            ("Cheese (200g)", 90.0),
            ("Tomatoes (1 kg)", 28.0),
            ("Cooking Oil (1L)", 110.0),
            ("Detergent (1kg)", 95.0),
            ("Toothpaste", 40.0)
        ]
        for name, price in products:
            cursor.execute('''SELECT p.id, p.name, p.price
                              FROM products p
                                       JOIN cart c ON p.id = c.product_id
                              WHERE c.user_id = ?''', (user_id,))
        conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    seed_data()
    app.run(debug=True)
