import sqlite3

def create_db():
    conn = sqlite3.connect('database.db')
    create_table_query = """
    CREATE TABLE IF NOT EXISTS User (
        username TEXT PRIMARY KEY,
        private_key TEXT UNIQUE NOT NULL
    );
"""
    cursor = conn.cursor()
    cursor.executescript(create_table_query)
    conn.commit()
    conn.close()

def allKeys():
    conn = sqlite3.connect('database.db')
    search_query = """SELECT private_key FROM User;"""
    cursor = conn.cursor()
    cursor.execute(search_query)
    keys = cursor.fetchall()
    conn.close()
    return keys

def allUsers():
    conn = sqlite3.connect('database.db')
    search_query = """SELECT username FROM User;"""
    cursor = conn.cursor()
    cursor.execute(search_query)
    users = cursor.fetchall()
    conn.close()
    return users

def checkUser(username):
    conn = sqlite3.connect('database.db')
    search_query = """SELECT username FROM User WHERE username = ?;"""
    cursor = conn.cursor()
    cursor.execute(search_query, (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def insert_new_user(username, private_key):
    conn = sqlite3.connect('database.db')
    user = checkUser(username)
    if user is None:
        insert_query = """INSERT INTO User (username, private_key) VALUES (?, ?);"""
        cursor = conn.cursor()
        cursor.execute(insert_query, (username, private_key))
        conn.commit()
        conn.close()
        return True, "User added successfully"
    else:
        conn.close()
        return False, "User already exists in the database"

def delete_user_by_username(username):
    conn = sqlite3.connect('database.db')
    delete_query = """DELETE FROM User WHERE username = ?;"""
    cursor = conn.cursor()
    cursor.execute(delete_query, (username,))
    conn.commit()
    conn.close()

def delete_all():
    conn = sqlite3.connect('database.db')
    delete_query = """DELETE FROM User;"""
    cursor = conn.cursor()
    cursor.execute(delete_query)
    conn.commit()
    conn.close()

def search_user_by_private_key(private_key):
    conn = sqlite3.connect('database.db')
    search_query = """SELECT username FROM User WHERE private_key = ?;"""
    cursor = conn.cursor()
    cursor.execute(search_query, (private_key,))
    user = cursor.fetchone()
    conn.close()
    return user
def modify_password_by_username(username, password):
    conn = sqlite3.connect('database.db')
    update_query = """UPDATE User SET private_key = ? WHERE username = ?;"""
    cursor = conn.cursor()
    cursor.execute(update_query, (password, username))
    conn.commit()
    conn.close() 

if __name__ == "__main__":
    create_db()
    modify_password_by_username("progettoiotsicurity@gmail.com", "5689")
