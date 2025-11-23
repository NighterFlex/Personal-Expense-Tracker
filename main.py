from datetime import datetime, date
from db import db_connection

class User:
    def __init__(self, user_id: int, username: str, password: str, email: str, total_amount: float ):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.total_amount = total_amount



from datetime import date
from db import get_connection

class Expense:
    def __init__(self, expense_id: int, user_id: int, amount: float, category: str, description: str, expense_date: date = None):
        self.expense_id = expense_id
        self.user_id = user_id  # link to a user by ID
        self.amount = amount
        self.description = description
        self.expense_date = expense_date if expense_date else date.today()
        
        # Fetch categories from DB
        self.categories = self.fetch_categories()
        
        # Validate category
        if category not in self.categories:
            raise ValueError(f"Category must be one of: {self.categories}")
        self.category = category

    def fetch_categories(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category_name FROM categories")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories


class ExpenseManager:
    def __init__(self):
        self.expense_list: list[Expense] = []
        self.total_expense = 0.00


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