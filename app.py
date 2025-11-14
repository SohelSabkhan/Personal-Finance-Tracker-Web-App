from flask import Flask, render_template, request, redirect, session, send_file, make_response
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime

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
    cur.execute("SELECT type, category, amount, date, id FROM transactions WHERE user_id = %s ORDER BY date DESC", (session['user_id'],))
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

# Export to CSV
@app.route('/export/csv')
def export_csv():
    if 'user_id' not in session:
        return redirect('/login')

    con = get_con()
    cur = con.cursor()
    cur.execute("SELECT type, category, amount, date FROM transactions WHERE user_id = %s ORDER BY date DESC", (session['user_id'],))
    transactions = cur.fetchall()
    cur.close()
    con.close()

    # Calculate totals
    income = sum(t[2] for t in transactions if t[0] == 'income')
    expense = sum(t[2] for t in transactions if t[0] == 'expense')
    balance = income - expense

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['FinTrack - Transaction Report'])
    writer.writerow(['Generated on: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    writer.writerow(['Summary'])
    writer.writerow(['Total Income', f'₹{income:.2f}'])
    writer.writerow(['Total Expense', f'₹{expense:.2f}'])
    writer.writerow(['Balance', f'₹{balance:.2f}'])
    writer.writerow([])
    writer.writerow(['Date', 'Type', 'Category', 'Amount (₹)'])
    
    # Write transaction data
    for txn in transactions:
        writer.writerow([txn[3], txn[0].capitalize(), txn[1], f'{txn[2]:.2f}'])
    
    # Prepare response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=fintrack_transactions_{datetime.now().strftime("%Y%m%d")}.csv'
    response.headers['Content-Type'] = 'text/csv'
    
    return response

# Export to PDF
@app.route('/export/pdf')
def export_pdf():
    if 'user_id' not in session:
        return redirect('/login')

    con = get_con()
    cur = con.cursor()
    cur.execute("SELECT type, category, amount, date FROM transactions WHERE user_id = %s ORDER BY date DESC", (session['user_id'],))
    transactions = cur.fetchall()
    cur.close()
    con.close()

    # Calculate totals
    income = sum(t[2] for t in transactions if t[0] == 'income')
    expense = sum(t[2] for t in transactions if t[0] == 'expense')
    balance = income - expense

    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Title
    title = Paragraph("FinTrack - Transaction Report", title_style)
    elements.append(title)
    
    # Date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
    elements.append(date_text)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary Table
    summary_data = [
        ['Summary', ''],
        ['Total Income', f'₹{income:.2f}'],
        ['Total Expense', f'₹{expense:.2f}'],
        ['Balance', f'₹{balance:.2f}']
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Transactions Table
    if transactions:
        trans_data = [['Date', 'Type', 'Category', 'Amount (₹)']]
        for txn in transactions:
            trans_data.append([
                txn[3],
                txn[0].capitalize(),
                txn[1],
                f'₹{txn[2]:.2f}'
            ])
        
        trans_table = Table(trans_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1.5*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(trans_table)
    else:
        no_data = Paragraph("No transactions found.", styles['Normal'])
        elements.append(no_data)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'fintrack_transactions_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

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