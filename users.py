# Run this code once to set up the users table
import sqlite3
import hashlib

conn = sqlite3.connect('db/titanic.sqlite')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')

# cursor.execute('''
#     ALTER TABLE users ADD COLUMN role_id INTEGER DEFAULT 2
# ''')

cursor.execute('''CREATE TABLE IF NOT EXISTS me
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    hobby TEXT,
                    project TEXT)''')
print("execution done")


# Create the roles table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY,
        role_name TEXT UNIQUE NOT NULL
    )
''')

# Insert default roles (admin and user)
cursor.execute('''
    INSERT OR IGNORE INTO roles (id, role_name) VALUES
    (1, 'admin'),
    (2, 'user')
''')



conn.commit()
conn.close()