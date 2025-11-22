# 💰 FinTech: Personal Finance Tracker

A full-featured web application built with Flask and PostgreSQL to help you manage your personal finances. Track income and expenses, categorize transactions, and export your financial data.

## ✨ Features

- **User Authentication**: Secure signup and login system with password hashing
- **Transaction Management**: Add, edit, and delete income/expense transactions
- **Custom Categories**: Support for custom income and expense categories
- **Smart Filtering**: Filter transactions by month, year, and type
- **Financial Summary**: Real-time calculation of income, expenses, and balance
- **Data Export**: Export transactions to CSV or PDF format with applied filters
- **Responsive Design**: Clean, modern UI built with Bootstrap 5
- **Date & Time Tracking**: Record transactions with specific dates and times

## 📸 Screenshots

### Dashboard
View all your transactions with filtering options and financial summary cards.

### Add Transaction
Easily add new income or expense transactions with custom categories.

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher (tested on Python 3.13)
- PostgreSQL 14 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/personal-finance-tracker.git
   cd personal-finance-tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```sql
   -- Open PostgreSQL command line or pgAdmin
   CREATE DATABASE personal_finance;
   ```

5. **Configure database connection**
   
   Update the database credentials in `app.py` if needed:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/personal_finance'
   ```

6. **Generate a secret key**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```
   
   Update `SECRET_KEY` in `app.py` with the generated key:
   ```python
   app.config['SECRET_KEY'] = 'your-generated-secret-key-here'
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   
   Open your browser and navigate to: `http://127.0.0.1:5000`

## 📁 Project Structure

```
personal-finance-tracker/
├── app.py                 # Main application file with routes
├── models.py              # Database models (User, Transaction)
├── requirements.txt       # Python dependencies
├── templates/            
│   ├── login.html        # Login page
│   ├── signup.html       # Signup page
│   ├── dashboard.html    # Main dashboard
│   ├── add_transaction.html
│   └── edit_transaction.html
├── static/
│   └── style.css         # Custom CSS styles
└── README.md
```

## 🛠️ Technologies Used

- **Backend**: Flask 3.0.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Database Driver**: psycopg3
- **Authentication**: Flask-Login
- **Password Security**: Werkzeug password hashing
- **PDF Generation**: ReportLab
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript

## 📦 Dependencies

```
Flask==3.0.0
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
psycopg[binary]>=3.2.3
reportlab==4.0.7
Werkzeug==3.0.1
SQLAlchemy>=2.0.35
```

## 💡 Usage

### Creating an Account
1. Navigate to the signup page
2. Enter username, email, and password
3. Click "Sign Up"

### Adding Transactions
1. Log in to your account
2. Click "Add Transaction" in the navigation bar
3. Select transaction type (Income/Expense)
4. Choose or create a custom category
5. Enter amount, date, and optional description
6. Click "Add Transaction"

### Filtering Transactions
1. Use the filter section on the dashboard
2. Select month, year, and/or transaction type
3. Click "Apply Filter"
4. Clear filters anytime with the "Clear" button

### Exporting Data
1. Apply desired filters (optional)
2. Click "Export" dropdown in navigation
3. Choose CSV or PDF format
4. File will download with filters applied

## 🔒 Security Features

- Password hashing using Werkzeug's security utilities
- Session management with Flask-Login
- SQL injection prevention through SQLAlchemy ORM
- CSRF protection with Flask's secret key
- User-specific data isolation

## 📈 Future Enhancements

- [ ] Data visualization with charts and graphs
- [ ] Budget setting and tracking
- [ ] Recurring transactions
- [ ] Multi-currency support
- [ ] Mobile application
- [ ] Email notifications
- [ ] Category-wise spending analysis
- [ ] Financial goals tracking
