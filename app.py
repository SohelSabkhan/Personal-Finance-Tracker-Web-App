from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Transaction
import psycopg
import csv
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg://postgres:password@localhost:5432/personal_finance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'

# Database connection function (alternative method using psycopg2)
def get_con():
    conn = psycopg.connect(
        dbname='personal_finance',
        user='postgres',
        password='password',
        host='localhost',
        port='5432'
    )
    return conn

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authentication Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('signup'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get filter parameters
    month = request.args.get('month')
    year = request.args.get('year')
    transaction_type = request.args.get('type', 'all')  # all, income, expense
    
    # Base query
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if month and year:
        from datetime import datetime
        start_date = datetime(int(year), int(month), 1)
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1)
        query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
    
    if transaction_type != 'all':
        query = query.filter_by(type=transaction_type)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Calculate totals
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = income - expenses
    
    # Category breakdown
    expense_by_category = {}
    for t in transactions:
        if t.type == 'expense':
            expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount
    
    # Get available months/years for dropdown
    all_transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    available_dates = set()
    for t in all_transactions:
        available_dates.add((t.date.year, t.date.month))
    available_dates = sorted(available_dates, reverse=True)
    
    return render_template('dashboard.html', 
                         transactions=transactions,
                         income=income,
                         expenses=expenses,
                         balance=balance,
                         expense_by_category=expense_by_category,
                         available_dates=available_dates,
                         selected_month=month,
                         selected_year=year,
                         selected_type=transaction_type)
# Add Transaction
@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        # Get date from form or use current datetime
        date_str = request.form.get('date')
        if date_str:
            transaction_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        else:
            transaction_date = datetime.utcnow()
        
        # Handle custom category
        category = request.form.get('category')
        custom_category = request.form.get('custom_category', '').strip()
        
        if (category == 'Other Income' or category == 'Other Expense') and custom_category:
            category = custom_category
        
        transaction = Transaction(
            user_id=current_user.id,
            type=request.form.get('type'),
            category=category,
            amount=float(request.form.get('amount')),
            description=request.form.get('description', ''),
            date=transaction_date
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_transaction.html')

# Edit Transaction
@app.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    if transaction.user_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        transaction.type = request.form.get('type')
        
        # Handle custom category
        category = request.form.get('category')
        custom_category = request.form.get('custom_category', '').strip()
        
        if (category == 'Other Income' or category == 'Other Expense') and custom_category:
            transaction.category = custom_category
        else:
            transaction.category = category
        
        transaction.amount = float(request.form.get('amount'))
        transaction.description = request.form.get('description', '')
        
        # Update date if provided
        date_str = request.form.get('date')
        if date_str:
            transaction.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_transaction.html', transaction=transaction)

# Delete Transaction
@app.route('/delete_transaction/<int:id>')
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    if transaction.user_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

# Export to CSV with filters
@app.route('/export/csv')
@login_required
def export_csv():
    # Get filter parameters from URL
    month = request.args.get('month')
    year = request.args.get('year')
    transaction_type = request.args.get('type', 'all')
    
    # Base query
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if month and year:
        from datetime import datetime
        start_date = datetime(int(year), int(month), 1)
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1)
        query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
    
    if transaction_type != 'all':
        query = query.filter_by(type=transaction_type)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description'])
    
    for t in transactions:
        writer.writerow([
            t.date.strftime('%Y-%m-%d %H:%M:%S'),
            t.type.capitalize(),
            t.category,
            f"{t.amount:.2f}",
            t.description or ''
        ])
    
    output = BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    
    # Generate filename based on filters
    filename = f'transactions_{current_user.username}'
    if month and year:
        month_name = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(month)]
        filename += f'_{month_name}{year}'
    if transaction_type != 'all':
        filename += f'_{transaction_type}'
    filename += f'_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

# Export to PDF with filters
@app.route('/export/pdf')
@login_required
def export_pdf():
    # Get filter parameters from URL
    month = request.args.get('month')
    year = request.args.get('year')
    transaction_type = request.args.get('type', 'all')
    
    # Base query
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if month and year:
        from datetime import datetime
        start_date = datetime(int(year), int(month), 1)
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1)
        query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
    
    if transaction_type != 'all':
        query = query.filter_by(type=transaction_type)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "Personal Finance Tracker")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, f"User: {current_user.username}")
    p.drawString(50, height - 85, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Filter info
    filter_text = "Filter: "
    if month and year:
        month_name = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][int(month)]
        filter_text += f"{month_name} {year}"
    else:
        filter_text += "All Time"
    
    if transaction_type != 'all':
        filter_text += f" - {transaction_type.capitalize()} Only"
    
    p.drawString(50, height - 100, filter_text)
    
    # Calculate totals
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = income - expenses
    
    # Summary Box
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 135, "Summary")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 155, f"Total Income: ${income:.2f}")
    p.drawString(50, height - 170, f"Total Expenses: ${expenses:.2f}")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 190, f"Balance: ${balance:.2f}")
    
    # Table headers
    p.setFont("Helvetica-Bold", 10)
    y = height - 225
    p.drawString(50, y, "Date")
    p.drawString(140, y, "Type")
    p.drawString(210, y, "Category")
    p.drawString(310, y, "Amount")
    p.drawString(400, y, "Description")
    
    # Draw line
    p.line(50, y - 5, width - 50, y - 5)
    
    # Transactions
    p.setFont("Helvetica", 9)
    y -= 20
    
    for t in transactions:
        if y < 50:  # New page if needed
            p.showPage()
            p.setFont("Helvetica", 9)
            y = height - 50
        
        p.drawString(50, y, t.date.strftime('%Y-%m-%d'))
        p.drawString(140, y, t.type.capitalize())
        p.drawString(210, y, t.category[:15])
        
        # Color based on type
        if t.type == 'income':
            p.setFillColorRGB(0, 0.5, 0)
        else:
            p.setFillColorRGB(0.8, 0, 0)
        p.drawString(310, y, f"${t.amount:.2f}")
        p.setFillColorRGB(0, 0, 0)
        
        p.drawString(400, y, (t.description or '')[:25])
        y -= 15
    
    p.save()
    buffer.seek(0)
    
    # Generate filename based on filters
    filename = f'transactions_{current_user.username}'
    if month and year:
        month_name = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(month)]
        filename += f'_{month_name}{year}'
    if transaction_type != 'all':
        filename += f'_{transaction_type}'
    filename += f'_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables in PostgreSQL
    app.run(debug=True)