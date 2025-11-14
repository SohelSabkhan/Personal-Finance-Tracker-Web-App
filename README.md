# FinTrack 💰

**Track your spending, grow your savings.**

A simple and intuitive web-based personal finance tracker built with Flask and PostgreSQL. Manage your income and expenses, monitor your balance, and gain better control over your finances.

## ✨ Features

- **User Authentication**: Secure signup and login system with password hashing
- **Transaction Management**: Add, edit, and delete income and expense transactions
- **Financial Overview**: Real-time dashboard showing:
  - Total Income
  - Total Expenses
  - Current Balance
- **Transaction History**: View all your transactions in an organized table with color-coded badges
- **Category Tracking**: Organize transactions by custom categories
- **Date Tracking**: Record and view transactions by date
- **Export Functionality**: 
  - **CSV Export**: Download transaction history as CSV for spreadsheet analysis
  - **PDF Export**: Generate professional PDF reports with summaries and detailed transaction tables

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, HTML, Jinja2 Templates, Font Awesome Icons
- **Security**: Werkzeug password hashing
- **Session Management**: Flask sessions
- **Report Generation**: ReportLab (PDF), CSV module

## 📋 Prerequisites

Before running this application, ensure you have the following installed:

- Python 3.7 or higher
- PostgreSQL
- pip (Python package installer)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Personal_Finance_Tracker
   ```

2. **Set up a virtual environment** (recommended)
   ```bash
   python -m venv pft_env
   
   # On Windows
   pft_env\Scripts\activate
   
   # On macOS/Linux
   source pft_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   - Create a new PostgreSQL database named `personal_finance`
   - Update the database credentials in `app.py` if needed:
     ```python
     database='personal_finance',
     user='postgres',
     password='password',
     host='localhost',
     port='5432'
     ```

5. **Initialize the database**
   The application will automatically create the necessary tables on first run.

## 🎯 Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Access the application**
   - Open your web browser and navigate to `http://127.0.0.1:5000`
   - The application will redirect you to the login page

3. **Create an account**
   - Click on "Sign up" to create a new account
   - Enter a username and password
   - Click "Create Account"

4. **Start tracking your finances**
   - Log in with your credentials
   - Click "Add Transaction" to record income or expenses
   - View your financial summary on the dashboard
   - Edit or delete transactions as needed

5. **Export your data**
   - Click **"Export CSV"** to download transactions as a CSV file for Excel/Google Sheets
   - Click **"Export PDF"** to generate a professional PDF report with summaries
   - Exported files are automatically named with the current date (e.g., `fintrack_transactions_20250415.pdf`)

## 📁 Project Structure

```
Personal_Finance_Tracker/
│
├── app.py                      # Main application file
├── requirements.txt            # Python dependencies
│
├── templates/                  # HTML templates
│   ├── login.html             # Login page
│   ├── signup.html            # Signup page
│   ├── dashboard.html         # Main dashboard with export buttons
│   ├── add_transaction.html   # Add transaction form
│   └── edit_transaction.html  # Edit transaction form
│
└── static/                     # Static files (CSS, images, etc.)
    └── style.css              # Custom styles
```

## 🔒 Security Features

- Password hashing using Werkzeug's security utilities
- Session-based authentication
- User-specific data access (users can only view/edit their own transactions)
- SQL injection prevention through parameterized queries
- Delete confirmation prompts to prevent accidental data loss

## 🎨 User Interface

The application features a clean, modern interface with:
- Responsive Bootstrap design
- Color-coded financial cards (Green for income, Red for expenses, Blue for balance)
- Easy-to-use forms for data entry
- Organized transaction table with action buttons
- Font Awesome icons for better visual guidance
- Badge indicators for transaction types

## 📊 Export Features

### CSV Export
- Includes complete transaction history
- Summary section with totals (Income, Expense, Balance)
- Compatible with Excel, Google Sheets, and other spreadsheet software
- Perfect for further data analysis and record-keeping

### PDF Export
- Professional report layout with styled headers
- Color-coded summary table
- Detailed transaction table with alternating row colors
- Includes generation timestamp
- Ideal for printing, archiving, or sharing with financial advisors

## 🤝 Contributing

Contributions are welcome! Here are some ways you can contribute:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 Future Enhancements

Potential features for future versions:
- Data visualization (charts and graphs)
- Budget planning and alerts
- Multiple currency support
- Monthly/yearly financial reports
- Receipt upload functionality
- Mobile app version
- Recurring transaction support
- Category-wise expense breakdown
- Custom date range filtering for exports

## 📦 Dependencies

Key Python packages used:
- **Flask**: Web framework
- **psycopg2**: PostgreSQL adapter
- **Werkzeug**: Security utilities
- **ReportLab**: PDF generation
- **Bootstrap 5**: Frontend framework
- **Font Awesome**: Icon library

## 📄 License

This project is open source and available for personal and educational use.

## 💡 Tips

- Regularly export your data to keep backup copies
- Use descriptive categories for better financial insights
- Review your balance regularly to stay on track with your budget
- The PDF export is great for monthly financial reviews

---

**Happy Tracking! 📊💵**
