from flask import Flask, render_template, request, redirect, session
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret-key'

# Database connection
def get_con():
    conn = psycopg2.connect(
        database='personal_finance',
        user='postgres',
        password='password',
        host='localhost',
        port='5432'
    )
    return conn

# Home
@app.route('/')
def home():
    return redirect('/login')

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        con = get_con()
        cur = con.cursor()

        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            con.close()
            return 'User already exists'

        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        con.commit()
        cur.close()
        con.close()
        return redirect('/login')

    return render_template('signup.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        con = get_con()
        cur = con.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        con.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect('/dashboard')
        return 'Invalid credentials'

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    con = get_con()
    cur = con.cursor()
    cur.execute("SELECT type, category, amount, date, id FROM transactions WHERE user_id = %s", (session['user_id'],))
    transactions = cur.fetchall()
    cur.close()
    con.close()

    income = sum(t[2] for t in transactions if t[0] == 'income')
    expense = sum(t[2] for t in transactions if t[0] == 'expense')
    balance = income - expense

    return render_template('dashboard.html', transactions=transactions, income=income, expense=expense, balance=balance)

# Add Transaction
@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        txn_type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        date = request.form['date']

        con = get_con()
        cur = con.cursor()
        cur.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (%s, %s, %s, %s, %s)",
                    (session['user_id'], txn_type, category, amount, date))
        con.commit()
        cur.close()
        con.close()
        return redirect('/dashboard')

    return render_template('add_transaction.html')

# Edit Transaction
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    if 'user_id' not in session:
        return redirect('/login')

    con = get_con()
    cur = con.cursor()

    if request.method == 'POST':
        txn_type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        date = request.form['date']
        cur.execute("UPDATE transactions SET type=%s, category=%s, amount=%s, date=%s WHERE id=%s AND user_id=%s",
                    (txn_type, category, amount, date, id, session['user_id']))
        con.commit()
        cur.close()
        con.close()
        return redirect('/dashboard')

    cur.execute("SELECT type, category, amount, date FROM transactions WHERE id = %s AND user_id = %s", (id, session['user_id']))
    txn = cur.fetchone()
    cur.close()
    con.close()

    if not txn:
        return 'Transaction not found'

    return render_template('edit_transaction.html', txn=txn, id=id)

# Delete Transaction
@app.route('/delete/<int:id>')
def delete_transaction(id):
    if 'user_id' not in session:
        return redirect('/login')

    con = get_con()
    cur = con.cursor()
    cur.execute("DELETE FROM transactions WHERE id = %s AND user_id = %s", (id, session['user_id']))
    con.commit()
    cur.close()
    con.close()
    return redirect('/dashboard')


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Create tables (only for first run)
def init_db():
    con = get_con()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(200) NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            type VARCHAR(10) NOT NULL,
            category VARCHAR(100) NOT NULL,
            amount FLOAT NOT NULL,
            date VARCHAR(20) NOT NULL
        );
    """)
    con.commit()
    cur.close()
    con.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
