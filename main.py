from datetime import datetime, date
from db import db_connection
class User:
    def __init__(self, user_id: int, username: str, password: str, email: str, total_amount: float ):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.total_amount = total_amount



class Expense:
    def __init__(self, expense_id : int, amount : float, category : str, expense_date : date, description : str):
        self.expense_id = expense_id
        self.amount = amount
        self.category = category
        self.expense_date = expense_date
        self.description = description


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