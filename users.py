import sqlite3
import hashlib
import os

# Get the base directory of the current script
basedir = os.path.abspath(os.path.dirname(__file__))

db_path = os.path.join(basedir, 'db', 'titanic.sqlite')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')



# Create the contacts table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT  NOT NULL,
                    message TEXT NOT NULL,
                    current_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# Commit changes and close the connection
conn.commit()
conn.close()