import mysql.connector

def db_connection():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",    
        password="mishtuf", 
        database="expensetracker"  
    )
    return conn

