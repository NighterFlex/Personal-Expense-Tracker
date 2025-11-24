from datetime import date
# from typing import Optional
import os
from db import db_connection

# ---------- Global DB connection ----------
conn = db_connection()
cursor = conn.cursor()

# ---------- User class ----------
class User:
    def __init__(self, user_id: int = 0 , username: str = "", email: str = "", password: str = "", total_amount: float = 0.0):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.total_amount = total_amount

    def register(self):
        cursor.execute("""
        INSERT INTO users (username, password, email, total_amount)
        VALUES (%s, %s, %s, %s)
        """, (self.username, self.password, self.email, self.total_amount))
        conn.commit()
        #gettingg the auto-generated user id
        self.user_id = cursor.lastrowid
        print(f"User {self.username} registered successfully with ID {self.user_id}!")

    def login(self, username: str, password: str):
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        
        if user:
            print(f"Login successful! Welcome {username}!")
            self.user_id, self.username, self.email, self.password, self.total_amount = user
            return True
        else:
            print("Login failed! Check your username and password.")
            return False
    
    def logout(self):
        print(f"User {self.username} logged out successfully!")
        self.user_id, self.username, self.password, self.email, self.total_amount = 0, "", "", "", 0.0


    def updateProfile(self, new_email : str, new_password : str):
        if not self.user_id:
            print("Error: No user logged in!")
            return
        
        self.email = new_email
        self.password = new_password

        cursor.execute("""
        UPDATE users
        SET email=%s, password=%s
        WHERE user_id=%s
        """, (self.email, self.password, self.user_id))
        conn.commit()

        print(f"User {self.username} profile updated successfully!")

    
    def viewProfile(self):
        if not self.user_id:
            print("No user is currently logged in. :(")
            return
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (self.user_id,))
        user = cursor.fetchone()

        if user:
            print("\n------- USER SUMMARY -------")
            print("User ID:", self.user_id)
            print("Username:", self.username)
            print("Email:", self.email)
            print("Total Amount:", self.total_amount)
            print("----------------------------\n")

            
# ---------- Expense class ----------
class Expense:
    def __init__(self, expense_id: int, user_id: int, amount: float, category: str, description: str, expense_date: date | None = None, categories: list | None = None):
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

# ---------- ExpenseManager class ----------
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

# ---------- Main Script ----------
# ---------- Main Script ----------
if __name__ == "__main__":
    import os

    user = User()
    manager = ExpenseManager()

    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    while True:
        clear()

        # ==========================
        #   BEFORE LOGIN MENU
        # ==========================
        if not user.user_id:
            print("\033[1;36m========================================\033[0m")
            print("\033[1;32m       PERSONAL EXPENSE TRACKER\033[0m")
            print("\033[1;36m========================================\033[0m")
            print("1. Register")
            print("2. Login")
            print("0. Exit")
            print("\033[1;36m========================================\033[0m")

            choice = input("Choose an option: ")

            # -------- REGISTER --------
            if choice == "1":
                clear()
                print("--- Register ---")
                username = input("Enter username: ")
                email = input("Enter email: ")
                password = input("Enter password: ")

                new_user = User(username=username, email=email, password=password)
                new_user.register()

                print("\nRegistration successful! You may now login.")
                input("\nPress Enter to return to menu...")

            # -------- LOGIN --------
            elif choice == "2":
                clear()
                print("--- Login ---")
                u = input("Username: ")
                p = input("Password: ")

                if user.login(u, p):
                    print("Login successful!")
                input("\nPress Enter to continue...")

            # -------- EXIT --------
            elif choice == "0":
                clear()
                print("Goodbye!")
                break

            else:
                print("Invalid option.")
                input("Press Enter to continue...")

        # ==========================
        #   AFTER LOGIN MENU
        # ==========================
        else:
            clear()
            print("\033[1;35m========================================\033[0m")
            print(f"   Logged in as: {user.username}")
            print("\033[1;35m========================================\033[0m")
            print("1. Add Expense")
            print("2. View Profile")
            print("3. View All Expenses")
            print("4. Logout")
            print("\033[1;35m========================================\033[0m")

            choice = input("Choose an option: ")

            # -------- ADD EXPENSE --------
            if choice == "1":
                clear()
                print("--- Add Expense ---")
                categories = manager.fetch_categories()
                print("Available Categories:", categories)

                try:
                    expense_id = int(input("Expense ID: "))
                    amount = float(input("Amount: "))
                    category = input("Category: ")
                    description = input("Description: ")

                    expense = Expense(
                        expense_id=expense_id,
                        user_id=user.user_id,
                        amount=amount,
                        category=category,
                        description=description,
                        categories=categories
                    )

                    manager.add_expense(expense)
                except Exception as e:
                    print("Error:", e)

                input("\nPress Enter to continue...")

            # -------- VIEW PROFILE --------
            elif choice == "2":
                clear()
                user.viewProfile()
                input("\nPress Enter to continue...")

            # -------- VIEW ALL EXPENSES --------
            elif choice == "3":
                clear()
                print("--- All Expenses ---")
                for e in manager.fetch_all_expenses():
                    print(e)
                input("\nPress Enter to continue...")

            # -------- LOGOUT --------
            elif choice == "4":
                clear()
                user.logout()
                input("Press Enter to continue...")

            else:
                print("Invalid option.")
                input("Press Enter to continue...")

