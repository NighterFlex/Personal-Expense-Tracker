#                                          PERSONAL EXPENSE TRACKER
#                                                   Group 6
#                                                    OOAD
# Imama, Haleema, Mishaal, Fatima
# We built a console-based application that tracks and helps manage a user's expenses and gives them cool budget recommendations
# App Version: v1.0
# Submission Date: 18-12-2025


from datetime import date      #to get today's date
import os                        #to clear screen
from db import db_connection   #for db connection


#DB connection 
conn = db_connection()
cursor = conn.cursor()              # cursor for executing SQL queries

# User class 
class User:
    def __init__(self, user_id=0, username="", password="", email="", total_amount=0.0):    #contructor
        self.user_id = user_id                                                              # store user ID
        self.username = username                                                           # store username
        self.password = password                                                            # dtore password
        self.email = email                                                                 # store email
        self.total_amount = float(total_amount)  # ensure balance is float

    def register(self):              # register new user
        # running SQL INSER query
        cursor.execute("""
        INSERT INTO users (username, password, email, total_amount)
        VALUES (%s, %s, %s, %s)
        """, (self.username, self.password, self.email, self.total_amount))   # type: ignore    # Ignore static type checker warnings for cursor.execute
        conn.commit()                                                           # Save changes to database
        self.user_id = cursor.lastrowid                                       # gt auto generated user id
        print(f"User {self.username} registered successfully! :3")                 #success

    def login(self, username, password):
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))       # execute SELECT query and credentials tuple
        user = cursor.fetchone()                                                                          # fetch one matching record

        if user:
            self.user_id, self.username, self.password, self.email, self.total_amount = user         # uunpack DB row
            self.total_amount = float(self.total_amount)  # type: ignore                          # cnvert Decimal to float
            return True                                                                   # login successful
        return False                                                                             # login failed

    def logout(self):
        print(f"User {self.username} logged out successfully!")
        self.user_id, self.username, self.password, self.email, self.total_amount = 0, "", "", "", 0.0                   # reset data

    def add_balance(self, amount):                                       # add balance to user account
        cursor.execute("UPDATE users SET total_amount = total_amount + %s WHERE user_id=%s", (float(amount), self.user_id))  # type: ignore
        conn.commit()                                                                                    
        cursor.execute("SELECT total_amount FROM users WHERE user_id=%s", (self.user_id,)) # type: ignore
        self.total_amount = float(cursor.fetchone()[0])     # type: ignore
        if self.total_amount == int(self.total_amount):
            amt_display = f"{int(self.total_amount):,}"                                           #single rlement tuple (comma is required) python things
        else:
            amt_display = f"{self.total_amount:,.2f}"
        print(f"Balance updated! Total: {amt_display}")

    def view_profile(self):
        # Refresh balance from database to get the most current value
        cursor.execute("SELECT total_amount FROM users WHERE user_id=%s", (self.user_id,))
        result = cursor.fetchone() #type: ignore
        if result:
            self.total_amount = float(result[0])  # type: ignore
        
        if self.total_amount == int(self.total_amount):  # type: ignore
            amt_display = f"{int(self.total_amount):,}"  # type: ignore
        else:
            amt_display = f"{self.total_amount:,.2f}"
        print("\n------- USER SUMMARY -------")
        print("User ID:", self.user_id)
        print("Username:", self.username)
        print("Email:", self.email)
        print("Total Balance:", amt_display)
        print("----------------------------\n")

# Expense class 
class Expense:
    def __init__(self, user_id, amount, category, description, expense_date=None):
        self.expense_id = None        #expense id
        self.user_id = user_id            #user id
        self.amount = float(amount)  #expense amounr(converted to float)
        self.category = category      #category name
        self.description = description
        self.expense_date = expense_date if expense_date else date.today()   #expense date (default if blank)


# ExpenseManager class
class ExpenseManager:

    def fetch_categories(self):  # fetches catrgory from db
        cursor.execute("SELECT category_name FROM categories")  # sql fetch query
        return [row[0] for row in cursor.fetchall()]  #type: ignore    # returns list of categories

    def add_expense(self, expense: Expense):  #new expense 
        cursor.execute("""
            INSERT INTO expenses (user_id, amount, expense_date, category, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            expense.user_id,          
            float(expense.amount),    
            expense.expense_date,     
            expense.category,         
            expense.description       
        ))

            #deduct the expense amount from user's total balance
        cursor.execute("UPDATE users SET total_amount = total_amount - %s WHERE user_id=%s", (float(expense.amount), expense.user_id))
        conn.commit()  #save changes to db
        expense.expense_id = cursor.lastrowid #type: ignore  #store generated expense id   
        print(f"Expense added successfully! (ID: {expense.expense_id})")  #  confirmation msg

    def view_all(self, user_id):  #all expenses of user
        cursor.execute(
            "SELECT * FROM expenses WHERE user_id=%s ORDER BY expense_date",
            (user_id,)
        )  #fetch user expenses sorted by date
        return cursor.fetchall()  #return all records

    def search_expense(self, expense_id, user_id):  #search expense by id
        cursor.execute(
            "SELECT * FROM expenses WHERE expense_id=%s AND user_id=%s",
            (expense_id, user_id)
        )                           #expens belongs to user
        return cursor.fetchone()  #return expense 

    def update_expense(self, expense_id, user_id, amount=None, category=None, description=None):
        if amount is not None:
            # old amount first
            cursor.execute("SELECT amount FROM expenses WHERE expense_id=%s AND user_id=%s", (expense_id, user_id))
            result = cursor.fetchone()
            if result:
                old_amount = float(result[0])  # type: ignore
                difference = float(amount) - old_amount
                
                #update amount
                cursor.execute("UPDATE expenses SET amount=%s WHERE expense_id=%s AND user_id=%s", 
                            (float(amount), expense_id, user_id))
                #upadte balance by the difference
                cursor.execute("UPDATE users SET total_amount = total_amount - %s WHERE user_id=%s", 
                            (difference, user_id))
        
        if category: #upadating category
            cursor.execute("UPDATE expenses SET category=%s WHERE expense_id=%s AND user_id=%s", 
                        (category, expense_id, user_id))
        if description: #updating description
            cursor.execute("UPDATE expenses SET description=%s WHERE expense_id=%s AND user_id=%s", 
                        (description, expense_id, user_id))
        conn.commit() #save changes
        print("Expense updated successfully!")

    def delete_expense(self, expense_id, user_id):
        #expense amount before deleting
        cursor.execute("SELECT amount FROM expenses WHERE expense_id=%s AND user_id=%s", (expense_id, user_id))
        result = cursor.fetchone()
        
        if result:
            amount = float(result[0])  # type: ignore
            #delete the expense
            cursor.execute("DELETE FROM expenses WHERE expense_id=%s AND user_id=%s", (expense_id, user_id))
            # asd the amount back to user's balance
            cursor.execute("UPDATE users SET total_amount = total_amount + %s WHERE user_id=%s", (amount, user_id))
            conn.commit()
            print("Expense deleted successfully!")
            print(f"Balance restored: {amount:,.2f}") #show restored balance
        else:
            print("Expense not found!")

    def filter_by_category(self, user_id, category):  #dilter expenses by category
        cursor.execute(
            "SELECT * FROM expenses WHERE user_id=%s AND category=%s ORDER BY expense_date",
            (user_id, category)
        )
        return cursor.fetchall()  #return filtered results

    def filter_by_date_range(self, user_id, start_date, end_date):  #filter expenses by date range
        cursor.execute(
            "SELECT * FROM expenses WHERE user_id=%s AND expense_date BETWEEN %s AND %s ORDER BY expense_date",
            (user_id, start_date, end_date)
        )
        return cursor.fetchall()  #return filtered expenses

    def daily_report(self, user_id):  #daily expense report
        cursor.execute(
            "SELECT expense_date, SUM(amount) FROM expenses WHERE user_id=%s GROUP BY expense_date ORDER BY expense_date DESC",
            (user_id,)
        )
        return cursor.fetchall()  #return daily totals

    def weekly_report(self, user_id):  #weekly expense report
        cursor.execute(
            "SELECT YEAR(expense_date), WEEK(expense_date,1), SUM(amount) FROM expenses WHERE user_id=%s GROUP BY YEAR(expense_date), WEEK(expense_date,1)",
            (user_id,)
        )
        return cursor.fetchall()  #return weekly totals

    def monthly_report(self, user_id):  #monthly expense report
        cursor.execute(
            "SELECT YEAR(expense_date), MONTH(expense_date), SUM(amount) FROM expenses WHERE user_id=%s GROUP BY YEAR(expense_date), MONTH(expense_date)",
            (user_id,)
        )
        return cursor.fetchall()  #return monthly totals

    def yearly_report(self, user_id):  #yearly expense report
        cursor.execute(
            "SELECT YEAR(expense_date), SUM(amount) FROM expenses WHERE user_id=%s GROUP BY YEAR(expense_date)",
            (user_id,)
        )
        return cursor.fetchall()  #return yearly totals


# Budget class 
class Budget:
    def __init__(self, total_amount):
        self.total_amount = float(total_amount)   #total balance
        self.essential = self.total_amount * 0.5   #50% essential balance
        self.lifestyle = self.total_amount * 0.3      #30% lifestyle bakance
        self.savings = self.total_amount * 0.2      #20% savings balance

    #display budget summary
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


# Main 
if __name__ == "__main__": #start of program execution
    #user and expense manager objects
    user = User()
    manager = ExpenseManager()

    # clear terminal screen
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    #application loop
    while True:
        clear()
        #if user is not logged in
        if not user.user_id:
            print("^"*40)
            print("\033[1;32m       PERSONAL EXPENSE TRACKER       \033[0m")
            print("^"*40)
            print("\033[1;49;94m1. Register \033[0m")
            print("\033[1;49;94m2. Login \033[0m")
            print("\033[1;49;94m3. Exit \033[0m")
            print("-"*40)
            choice = input("Choose an option: ")

            # Register 
            if choice == "1":
                clear()
                print("------ Register ---------")
                username = input("Username: ")

                #email validation loop
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

            # Login 
            elif choice == "2":
                clear()
                print("---------- Login -------------")
                username = input("Username: ")
                password = input("Password: ")
                if user.login(username, password):
                    print(f"Login successful! Welcome {user.username}! YAY")
                else:
                    print("Login failed! Check username/password.")
                input("\nPress Enter to continue...")

            # Exit 
            elif choice == "3":
                clear()
                print("Goodbye! SEE YAAAA")
                break

            #invalid option handling
            else:
                print("Invalid option!")
                input("Press Enter to continue...")

        # Menu 
        else:
            clear()
            print("^"*40)
            print(f"       Logged in as: \033[1;32m{user.username}\033[0m       ")
            print("^"*40)
            print("1. Add Balance")
            print("2. Add Expense")
            print("3. View All Expenses")
            print("4. Search Expense")
            print("5. Update Expense")
            print("6. Delete Expense")
            print("7. Filter by Category")
            print("8. Filter by Date Range")
            print("9. Reports")
            print("10. Budget Recommendation")
            print("11. View Profile")
            print("12. Logout")
            print("-"*40)
            choice = input("Choose an option: ")

            # Add Balance
            if choice == "1":
                clear()
                amt = float(input("Amount to add: "))
                user.add_balance(amt)
                input("\nPress Enter to continue...")

            # Add Expense 
            elif choice == "2":
                clear()
                print("------------- Add Expense -----------")
                categories = manager.fetch_categories()
                print("Available Categories:", categories)
                amt = float(input("Amount: "))
                cat = input("Category: ")
                if cat not in categories:
                    print("Invalid category!")
                    input("\nPress Enter to continue...")
                    continue
                desc = input("Description (optional): ") or None
                exp_date_input = input("Expense Date: ")
                if exp_date_input:
                    exp_date = exp_date_input
                else:
                    exp_date = date.today()
                exp = Expense(user.user_id, amt, cat, desc, exp_date)
                manager.add_expense(exp)
                
                #refresh user's balance from db
                cursor.execute("SELECT total_amount FROM users WHERE user_id=%s", (user.user_id,)) 
                user.total_amount = float(cursor.fetchone()[0])  # type: ignore
                
                if user.total_amount == int(user.total_amount):
                    amt_display = f"{int(user.total_amount):,}"
                else:
                    amt_display = f"{user.total_amount:,.2f}"
                print(f"Current Balance: {amt_display}")
                
                input("\nPress Enter to continue...")

            # View All Expenses 
            elif choice == "3":
                clear()
                print("---------- All Expenses -----------")
                for expense in manager.view_all(user.user_id):
                    expense_id, user_id, amount, expense_date, category, description = expense
                    if float(amount) == int(amount):    # type: ignore
                        amt_display = f"{int(amount):,}"    # type: ignore
                    else:
                        amt_display = f"{float(amount):,.2f}"    # type: ignore
                    print(f"{expense_id}, {user_id}, {amt_display}, {expense_date}, {category}, {description}")
                input("\nPress Enter to continue...")

            # Search Expense
            elif choice == "4":
                clear()
                eid = int(input("Expense ID to search: "))
                expense = manager.search_expense(eid, user.user_id)
                if expense:
                    expense_id, user_id, amount, expense_date, category, description = expense
                    if float(amount) == int(amount):    # type: ignore
                        amt_display = f"{int(amount):,}"   # type: ignore
                    else:
                        amt_display = f"{float(amount):,.2f}"    # type: ignore
                    print(f"{expense_id}, {user_id}, {amt_display}, {expense_date}, {category}, {description}")
                else:
                    print("Expense not found")
                input("\nPress Enter to continue...")

            # Update Expense 
            elif choice == "5":
                clear()
                eid = int(input("Expense ID to update: "))
                amt = input("New Amount: ")
                cat = input("New Category: ")
                desc = input("New Description: ")
                manager.update_expense(
                    eid, user.user_id,
                    float(amt) if amt else None,
                    cat if cat else None,
                    desc if desc else None
                )
                input("\nPress Enter to continue...")

            # Delete Expense
            elif choice == "6":
                clear()
                eid = int(input("Expense ID to delete: "))
                manager.delete_expense(eid, user.user_id)
                input("\nPress Enter to continue...")

            # Filter by Category
            elif choice == "7":
                clear()
                cat = input("Category: ")
                for expense in manager.filter_by_category(user.user_id, cat):
                    expense_id, user_id, amount, expense_date, category, description = expense
                    if float(amount) == int(amount):      # type: ignore
                        amt_display = f"{int(amount):,}"    # type: ignore
                    else:
                        amt_display = f"{float(amount):,.2f}"   # type: ignore
                    print(f"{expense_id}, {user_id}, {amt_display}, {expense_date}, {category}, {description}")
                input("\nPress Enter to continue...")

            # Filter by Date Range 
            elif choice == "8":
                clear()
                start = input("Start Date: ")
                end = input("End Date: ")
                for expense in manager.filter_by_date_range(user.user_id, start, end):
                    expense_id, user_id, amount, expense_date, category, description = expense
                    if float(amount) == int(amount):       # type: ignore
                        amt_display = f"{int(amount):,}"        # type: ignore
                    else:
                        amt_display = f"{float(amount):,.2f}"    # type: ignore
                    print(f"{expense_id}, {user_id}, {amt_display}, {expense_date}, {category}, {description}")
                input("\nPress Enter to continue...")

            # Reports 
            elif choice == "9":
                clear()
                print("---------- Reports -----------")

                print("\nDaily Report:")
                print("Date        | Amount")
                for d, amt in manager.daily_report(user.user_id):
                    if float(amt) == int(amt):    # type: ignore
                        amt_display = f"{int(amt):,}"    # type: ignore
                    else:
                        amt_display = f"{float(amt):,.2f}"     # type: ignore
                    print(f"{d} | {amt_display}")

                print("\nWeekly Report:")
                print("Year | Week | Amount")
                for year, week, amt in manager.weekly_report(user.user_id):
                    if float(amt) == int(amt):          # type: ignore
                        amt_display = f"{int(amt):,}"      # type: ignore
                    else:
                        amt_display = f"{float(amt):,.2f}"      # type: ignore
                    print(f"{year} | {week} | {amt_display}")

                print("\nMonthly Report:")
                print("Year-Month | Amount")
                for year, month, amt in manager.monthly_report(user.user_id):
                    if float(amt) == int(amt):      # type: ignore
                        amt_display = f"{int(amt):,}"         # type: ignore
                    else:
                        amt_display = f"{float(amt):,.2f}"        # type: ignore
                    print(f"{year}-{month:02d} | {amt_display}")

                print("\nYearly Report:")
                print("Year | Amount")
                for year, amt in manager.yearly_report(user.user_id):
                    if float(amt) == int(amt):       # type: ignore
                        amt_display = f"{int(amt):,}"      # type: ignore
                    else:
                        amt_display = f"{float(amt):,.2f}"       # type: ignore
                    print(f"{year} | {amt_display}")
                input("\nPress Enter to continue...")

            # Budget Recommendation 
            elif choice == "10":
                clear()
                budget = Budget(user.total_amount)
                budget.show()
                input("\nPress Enter to continue...")

            # View Profile 
            elif choice == "11":
                clear()
                user.view_profile()
                input("\nPress Enter to continue...")

            # Logout 
            elif choice == "12":
                clear()
                user.logout()
                input("\nPress Enter to continue...")
