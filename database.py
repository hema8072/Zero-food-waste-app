import sqlite3

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_food_table():

    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS food_donations(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            donor_email TEXT,

            food_name TEXT NOT NULL,

            quantity TEXT NOT NULL,

            category TEXT NOT NULL,

            expiry_time TEXT,

            address TEXT,

            contact TEXT,
                 
            image TEXT,
                      
            status TEXT DEFAULT 'Available'     

        )
    ''')

    conn.commit()
    conn.close()    
def create_request_table():

    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS food_requests(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            food_id INTEGER,

            receiver_email TEXT,

            status TEXT DEFAULT 'Pending'

        )
    ''')

    conn.commit()
    conn.close()

def create_admin_table():

    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            password TEXT

        )
    ''')


    # create default admin

    conn.execute(
        """
        INSERT OR IGNORE INTO admin(username,password)
        VALUES(?,?)
        """,
        ("admin","admin123")
    )


    conn.commit()
    conn.close()    

if __name__ == "__main__":

    create_table()

    create_food_table()

    create_request_table()

    create_admin_table()

    print("Database created successfully!")