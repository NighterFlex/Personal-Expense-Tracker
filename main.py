from datetime import date
import os
from db import db_connection
from decimal import Decimal

# ---------- Global DB connection ----------
conn = db_connection()
cursor = conn.cursor()

# ---------- User class ----------
class User:
    def _init_(self, user_id=0, username="", password="", email="", total_amount=0.0):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.total_amount = float(total_amount)

    def register(self):
        cursor.execute("""
        INSERT INTO users (username, password, email, total_amount)
        VALUES (%s, %s, %s, %s)
        """, (self.username, self.password, self.email, self.total_amount))
        conn.commit()
        self.user_id = cursor.lastrowid
        print(f"User {self.username} registered successfully!")

    def login(self, username, password):
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            self.user_id, self.username, self.password, self.email, self.total_amount = user
            self.total_amount = float(self.total_amount)
            return True
        return False

    def logout(self):
        print(f"User {self.username} logged out successfully!")
        self.user_id, self.username, self.password, self.email, self.total_amount = 0, "", "", "", 0.0

    def add_balance(self, amount):
        cursor.execute("UPDATE users SET total_amount = total_amount + %s WHERE user_id=%s", (float(amount), self.user_id))
        conn.commit()
        cursor.execute("SELECT total_amount FROM users WHERE user_id=%s", (self.user_id,))
        self.total_amount = float(cursor.fetchone()[0])
        if self.total_amount == int(self.total_amount):
            amt_display = f"{int(self.total_amount):,}"
        else:
            amt_display = f"{self.total_amount:,.2f}"
        print(f"Balance updated! Total: {amt_display}")

    def view_profile(self):
        if self.total_amount == int(self.total_amount):
            amt_display = f"{int(self.total_amount):,}"
        else:
            amt_display = f"{self.total_amount:,.2f}"
        print("\n------- USER SUMMARY -------")
        print("User ID:", self.user_id)
        print("Username:", self.username)
        print("Email:", self.email)
        print("Total Balance:", amt_display)
        print("----------------------------\n")

# ---------- Expense class ----------
class Expense:
    def _init_(self, user_id, amount, category, description, expense_date=None):
        self.expense_id = None
        self.user_id = user_id
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.expense_date = expense_date if expense_date else date.today()

# ---------- ExpenseManager class ----------
class ExpenseManager:
    def fetch_categories(self):
        cursor.execute("SELECT category_name FROM categories")
        return [row[0] for row in cursor.fetchall()]

    def add_expense(self, expense: Expense):
        cursor.execute("""
            INSERT INTO expenses (user_id, amount, expense_date, category, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (expense.user_id, float(expense.amount), expense.expense_date, expense.category, expense.description))
        conn.commit()
        expense.expense_id = cursor.lastrowid
        print(f"Expense added successfully! (ID: {expense.expense_id})")

    def view_all(self, user_id):
        cursor.execute("SELECT * FROM expenses WHERE user_id=%s ORDER BY expense_date", (user_id,))
        return cursor.fetchall()

    def search_expense(self, expense_id, user_id):
        cursor.execute("SELECT * FROM expenses WHERE expense_id=%s AND user_id=%s", (expense_id, user_id))
        return cursor.fetchone()

    def update_expense(self, expense_id, user_id, amount=None, category=None, description=None):
        if amount is not None:
            cursor.execute("UPDATE expenses SET amount=%s WHERE expense_id=%s AND user_id=%s", (float(amount), expense_id, user_id))
        if category:
            cursor.execute("UPDATE expenses SET category=%s WHERE expense_id=%s AND user_id=%s", (category, expense_id, user_id))
        if description:
            cursor.execute("UPDATE expenses SET description=%s WHERE expense_id=%s AND user_id=%s", (description, expense_id, user_id))
        conn.commit()
        print("Expense updated successfully!")

    def delete_expense(self, expense_id, user_id):
        cursor.execute("DELETE FROM expenses WHERE expense_id=%s AND user_id=%s", (expense_id, user_id))
        conn.commit()
        print("Expense deleted successfully!")

    def filter_by_category(self, user_id, category):
        cursor.execute("SELECT * FROM expenses WHERE user_id=%s AND category=%s ORDER BY expense_date", (user_id, category))
        return cursor.fetchall()

    def filter_by_date_range(self, user_id, start_date, end_date):
        cursor.execute("SELECT * FROM expenses WHERE user_id=%s AND expense_date BETWEEN %s AND %s ORDER BY expense_date", (user_id, start_date, end_date))
        return cursor.fetchall()

    # ---------- Reports ----------
    def daily_report(self, user_id):
        cursor.execute("SELECT expense_date, SUM(amount) FROM expenses WHERE user_id=%s GROUP BY expense_date ORDER BY expense_date DESC", (user_id,))
        return cursor.fetchall()

    def weekly_report(self, user_id):
        cursor.execute("SELECT YEAR(expense_date), WEEK(expense_date,1), SUM(amount) FROM expenses WHERE user_id=%s GROUP BY YEAR(expense_date), WEEK(expense_date,1) ORDER BY YEAR(expense_date), WEEK(expense_date,1)", (user_id,))
        return cursor.fetchall()

    def monthly_report(self, user_id):
        cursor.execute("SELECT YEAR(expense_date), MONTH(expense_date), SUM(amount) FROM expenses WHERE user_id=%s GROUP BY YEAR(expense_date), MONTH(expense_date) ORDER BY YEAR(expense_date), MONTH(expense_date)", (user_id,))
        return cursor.fetchall()

    def yearly_report(self, user_id):
        cursor.execute("SELECT YEAR(expense_date), SUM(amount) FROM expenses WHERE user_id=%s GROUP BY YEAR(expense_date) ORDER BY YEAR(expense_date)", (user_id,))
        return cursor.fetchall()

# ---------- Budget Recommendation class ----------
class Recommendation:
    def _init_(self, total_amount):
        self.total_amount = float(total_amount)
        self.essential = self.total_amount * 0.5
        self.lifestyle = self.total_amount * 0.3
        self.savings = self.total_amount * 0.2

    def show(self):
        if self.essential == int(self.essential):
            e = f"{int(self.essential):,}"
        else:
            e = f"{self.essential:,.2f}"
        if self.lifestyle == int(self.lifestyle):
            l = f"{int(self.lifestyle):,}"
        else:
            l = f"{self.lifestyle:,.2f}"
        if self.savings == int(self.savings):
            s = f"{int(self.savings):,}"
        else:
            s = f"{self.savings:,.2f}"

        print("\n--- BUDGET RECOMMENDATION ---")
        print(f"Essentials (50%): {e}")
        print(f"Lifestyle (30%): {l}")
        print(f"Savings (20%): {s}")
        print("-------------------------------\n")

# ---------- Main ----------
if _name_ == "_main_":
    user = User()
    manager = ExpenseManager()

    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    while True:
        clear()
        if not user.user_id:
            print("="*40)
            print("       PERSONAL EXPENSE TRACKER       ")
            print("="*40)
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            print("="*40)
            choice = input("Choose an option: ")
            if choice == "1":
                clear()
                print("--- Register ---")
                username = input("Username: ")

                # Email validation
                while True:
                    email = input("Email: ")
                    if "@" in email and "." in email:
                        break
                    else:
                        print("Invalid email! Email must contain '@' and '.'")

                password = input("Password: ")
                new_user = User(username=username, email=email, password=password)
                new_user.register()
                input("\nPress Enter to return to menu...")

            elif choice == "2":
                clear()
                print("--- Login ---")
                username = input("Username: ")
                password = input("Password: ")
                if user.login(username, password):
                    print(f"Login successful! Welcome {user.username}!")
                else:
                    print("Login failed! Check username/password.")
                input("\nPress Enter to continue...")
            elif choice == "3":
                clear()
                print("Goodbye!")
                break
            else:
                print("Invalid option!")
                input("Press Enter to continue...")
        else:
            clear()
            print("="*40)
            print(f"       Logged in as: {user.username}       ")
            print("="*40)
            print("1. Add Expense")
            print("2. View All Expenses")
            print("3. Search Expense")
            print("4. Update Expense")
            print("5. Delete Expense")
            print("6. Filter by Category")
            print("7. Filter by Date Range")
            print("8. Reports")
            print("9. Budget Recommendation")
            print("10. Add Balance")
            print("11. View Profile")
            print("12. Logout")
            print("="*40)
            choice = input("Choose an option: ")

            # ---------- Add Expense ----------
            if choice == "1":
                clear()
                print("--- Add Expense ---")
                categories = manager.fetch_categories()
                print("Available Categories:", categories)
                amt = float(input("Amount: "))
                cat = input("Category: ")
                if cat not in categories:
                    print("Invalid category!")
                    input("\nPress Enter to continue...")
                    continue
                desc = input("Description (optional): ") or None
                exp_date_input = input("Expense Date (YYYY-MM-DD, leave blank for today): ")
                if exp_date_input:
                    exp_date = exp_date_input
                else:
                    exp_date = date.today()
                exp = Expense(user.user_id, amt, cat, desc, exp_date)
                manager.add_expense(exp)
                input("\nPress Enter to continue...")

            # ---------- View All Expenses ----------
            elif choice == "2":
                clear()
                print("--- All Expenses ---")
                for expense in manager.view_all(user.user_id):
                    expense_id, user_id, amount, expense_date, category, description = expense
                    if float(amount) == int(amount):
                        amt_display = f"{int(amount):,}"
                    else:
                        amt_display = f"{float(amount):,.2f}"
                    print(f"{expense_id}, {user_id}, {amt_display}, {expense_date}, {category}, {description}")
                input("\nPress Enter to continue...")

            # ---------- Search Expense ----------
            elif choice == "3":
                clear()
                eid = int(input("Expense ID to search: "))
                expense = manager.search_expense(eid, user.user_id)
                if expense:
                    expense_id, user_id, amount, expense_date, category, description = expense
                    if float(amount) == int(amount):
                        amt_display = f"{int(amount):,}"
                    else:
                        amt_display = f"{float(amount):,.2f}"
                    print(f"{expense_id}, {user_id}, {amt_display}, {expense_date}, {category}, {description}")
                else:
                    print("Expense not found")
                input("\nPress Enter to continue...")

            # ---------- Update Expense ----------
            elif choice == "4":
                clear()
                eid = int(input("Expense ID to update: "))
                amt = input("New Amount (blank to skip): ")
                cat = input("New Category (blank to skip): ")
                desc = input("New Description (blank to skip): ")
                manager.update_expense(
                    eid, user.user_id,
                    float(amt) if amt else None,
                    cat if cat else None,
                    desc if desc else None
                )
                input("\nPress Enter to continue...")

            # ---------- Delete Expense ----------
            elif choice == "5":
                clear()
                eid = int(input("Expense ID to delete: "))
                manager.delete_expense(eid, user.user_id)
                input("\nPress Enter to continue...")

            # ---------- Filter by Category ----------
            elif choice == "6":
                clear()
                cat = input("Category: ")
                for expense in manager.filter_by_category(user.user_id, cat):
                    expense_id, user_id, amount, expense_date, category, description = expense
                    if float(amount) == int(amount):
                        amt_display = f"{int(amount):,}"
                    else:
                        amt_display = f"{float(amount):,.2f}"
                    print(f"{expense_id}, {user_id}, {amt_display}, {expense_date}, {category}, {description}")
                input("\nPress Enter to continue...")

            # ---------- Filter by Date Range ----------
            elif choice == "7":
                clear()
                start = input("Start Date (YYYY-MM-DD): ")
                end = input("End Date (YYYY-MM-DD): ")
                for expense in manager.filter_by_date_range(user.user_id, start, end):
                    expense_id, user_id, amount, expense_date, category, description = expense
                    if float(amount) == int(amount):
                        amt_display = f"{int(amount):,}"
                    else:
                        amt_display = f"{float(amount):,.2f}"
                    print(f"{expense_id}, {user_id}, {amt_display}, {expense_date}, {category}, {description}")
                input("\nPress Enter to continue...")

            # ---------- Reports ----------
            elif choice == "8":
                clear()
                print("--- Reports ---")

                print("\nDaily Report:")
                print("Date        | Amount")
                for d, amt in manager.daily_report(user.user_id):
                    if float(amt) == int(amt):
                        amt_display = f"{int(amt):,}"
                    else:
                        amt_display = f"{float(amt):,.2f}"
                    print(f"{d} | {amt_display}")

                print("\nWeekly Report:")
                print("Year | Week | Amount")
                for year, week, amt in manager.weekly_report(user.user_id):
                    if float(amt) == int(amt):
                        amt_display = f"{int(amt):,}"
                    else:
                        amt_display = f"{float(amt):,.2f}"
                    print(f"{year} | {week} | {amt_display}")

                print("\nMonthly Report:")
                print("Year-Month | Amount")
                for year, month, amt in manager.monthly_report(user.user_id):
                    if float(amt) == int(amt):
                        amt_display = f"{int(amt):,}"
                    else:
                        amt_display = f"{float(amt):,.2f}"
                    print(f"{year}-{month:02d} | {amt_display}")

                print("\nYearly Report:")
                print("Year | Amount")
                for year, amt in manager.yearly_report(user.user_id):
                    if float(amt) == int(amt):
                        amt_display = f"{int(amt):,}"
                    else:
                        amt_display = f"{float(amt):,.2f}"
                    print(f"{year} | {amt_display}")
                input("\nPress Enter to continue...")

            # ---------- Budget Recommendation ----------
            elif choice == "9":
                clear()
                budget = Recommendation(user.total_amount)
                budget.show()
                input("\nPress Enter to continue...")

            # ---------- Add Balance ----------
            elif choice == "10":
                clear()
                amt = float(input("Amount to add: "))
                user.add_balance(amt)
                input("\nPress Enter to continue...")

            # ---------- View Profile ----------
            elif choice == "11":
                clear()
                user.view_profile()
                input("\nPress Enter to continue...")

            # ---------- Logout ----------
            elif choice == "12":
                clear()
                user.logout()
                input("\nPress Enter to continue...")