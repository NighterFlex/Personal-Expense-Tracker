from datetime import datetime, date
from db import db_connection

conn = db_connection()
cursor = conn.cursor()

class User:
    def __init__(self, user_id: int, username: str, password: str, email: str, total_amount: float ):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.total_amount = total_amount


class Expense:
    def __init__(self, expense_id: int, user_id: int, amount: float, category: str, description: str, expense_date: date = None, categories=None):
        self.expense_id = expense_id
        self.user_id = user_id
        self.amount = amount
        self.description = description
        self.expense_date = expense_date if expense_date else date.today()
        
        # categories are passed from ExpenseManager
        self.categories = categories if categories else []

        # validate category if categories are available
        if self.categories and category not in self.categories:
            raise ValueError(f"Category must be one of: {self.categories}")
        self.category = category


from db import db_connection

# Global connection
conn = db_connection()
cursor = conn.cursor()

class ExpenseManager:
    def __init__(self):
        self.expense_list: list[Expense] = []
        self.total_expense = 0.0

    # Fetch categories from SQL
    def fetch_categories(self):
        cursor.execute("SELECT category_name FROM categories")
        categories = [row[0] for row in cursor.fetchall()]
        return categories

    # Add an expense to in-memory list and SQL
    def add_expense(self, expense: Expense):
        # Validate category against DB categories
        valid_categories = self.fetch_categories()
        if expense.category not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")

        self.expense_list.append(expense)
        self.total_expense += expense.amount

        # Insert into expenses table
        cursor.execute("""
        INSERT INTO expenses (expense_id, user_id, amount, expense_date, category, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (expense.expense_id, expense.user_id, expense.amount, expense.expense_date, expense.category, expense.description))
        conn.commit()
        print(f"Expense added successfully!")

    # Fetch all expenses
    def fetch_all_expenses(self):
        cursor.execute("SELECT * FROM expenses ORDER BY expense_date")
        return cursor.fetchall()

    # Fetch expenses by category
    def fetch_expenses_by_category(self, category: str):
        cursor.execute("SELECT * FROM expenses WHERE category=%s ORDER BY expense_date", (category,))
        return cursor.fetchall()


class Budgeting:
    # def __init__ (self):             #monthly_budget: float , remaining_budget : float)
        # self.monthly_budget = 0.0
        # self.remaining_budget = 0.0
        # self.monthly_budget = monthly_budget
        # self.remaining_budget = remaining_budget



    def __init__(self, rule_type: str = "50-30-20"):
        self.rule_type = rule_type
        self.essential_limit = 0.0
        self.lifestyle_limit = 0.0
        self.savings_limit = 0.0
        
        self.yearly_spending = 0.0
        self.monthly_spending = 0.0
        self.weekly_spending = 0.0
        self.daily_spending = 0.0