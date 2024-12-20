from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import hashlib
import pandas as pd
import sqlite3
import os
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Get the base directory of the current script
basedir = os.path.abspath(os.path.dirname(__file__))

# Construct the database path dynamically
db_path = os.path.join(basedir, 'db', 'titanic.sqlite')

@app.route('/second')
def hello_world():
    return render_template('index.html', message='Hello, World!')

@app.route('/form', methods=['GET', 'POST'])
def render_form():
    message = ''
    if request.method == 'POST':
        text = request.form.get('text')
        if request.form['submit_button'] == 'Lowercase':
            message = text.lower()
        elif request.form['submit_button'] == 'Capital':
            message = text.upper()
        elif request.form['submit_button'] == 'Byamba':
            message = "Hi Byamba"
    return render_template('form.html', message=message)

@app.route('/')
def about():
    conn = sqlite3.connect(db_path)
    # Read the 'titanic' table into a pandas DataFrame
    df = pd.read_sql('SELECT Name, Age FROM titanic', conn)
    name = df["Name"][0]
    age = df["Age"][0]
    print(name, age)
    return render_template('about.html',
                            jinja_title = name,
                            jinja_about = age
                            )

@app.route('/posts', methods=['GET', 'POST'])
def submit_post():
    message = ""
    if request.method == 'POST':
        title = request.form['title']
        post_content = request.form['post']
        post_type = request.form['type']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ensure the post table exists (you might want to modify or remove this part)
        cursor.execute('''CREATE TABLE IF NOT EXISTS post (id INTEGER PRIMARY KEY, title TEXT, post TEXT, type TEXT)''')

        # Insert the submitted form data into the post table
        cursor.execute("INSERT INTO post (title, post, type) VALUES (?, ?, ?)", (title, post_content, post_type))
        conn.commit()
        conn.close()

        message = "Post submitted successfully!"

    return render_template('form.html', message=message)

@app.route('/me', methods=['GET', 'POST'])
def about_me():
    message = ""
    if request.method == 'POST':
        name_insert = request.form['name']
        age_insert = request.form['age']
        hobby_insert = request.form['hobby']
        project_insert = request.form['project']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ensure the me table exists (you might want to modify or remove this part)
        cursor.execute('''CREATE TABLE IF NOT EXISTS me (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, hobby TEXT, project TEXT)''')

        # Insert the submitted form data into the me table
        cursor.execute("INSERT INTO me (name, age, hobby, project) VALUES (?, ?, ?, ?)", (name_insert, age_insert, hobby_insert, project_insert))
        conn.commit()
        conn.close()

        message = "Post submitted successfully!"
    return render_template('grace.html', message=message)

@app.route('/blogs')
def show_blogs():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all posts from the database
    cursor.execute("SELECT title, post, type FROM post")
    posts = cursor.fetchall()
    conn.close()

    # Format posts for rendering
    formatted_posts = [{"title": row[0], "content": row[1], "type": row[2]} for row in posts]

    return render_template('blog.html', posts=formatted_posts)

@app.route('/test')
def test_db():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql('SELECT Name, Age FROM titanic', conn)
    name = df["Name"][0]
    return f'Hello from Flask! {name}'


# Route for registration.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please try another one.")
        finally:
            conn.close()
    
    return render_template('register.html')

# Route to handle form submission
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # Retrieve form data
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Insert data into the contacts table
    conn = sqlite3.connect(db_path , check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contacts (name, email, message)
        VALUES (?, ?, ?)
    ''', (name, email, message))
    conn.commit()
    conn.close()

    # Redirect to the admin page
    return redirect('/admin')


# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('admin'))
        else:
            flash("Invalid username or password.")
    
    return render_template('login.html')

# Route to log out
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.")
    return redirect(url_for('login'))



# Fetch list of Pokémon names
def fetch_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1000"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [pokemon['name'] for pokemon in data['results']]
    else:
        return []

# Fetch Pokémon sprite URL
def fetch_pokemon_sprite(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    response = requests.get(url)
    if response.status_code == 200:
        raw_data = response.json()
        return raw_data['sprites']['front_default']
    else:
        return None

@app.route("/pokemon", methods=["GET", "POST"])
def index():
    pokemon_names = fetch_pokemon_names()
    selected_pokemon = None
    sprite_url = None

    if request.method == "POST":
        selected_pokemon = request.form.get("pokemon_name")
        sprite_url = fetch_pokemon_sprite(selected_pokemon)

    return render_template(
        "pokemon.html",
        pokemon_names=pokemon_names,
        selected_pokemon=selected_pokemon,
        sprite_url=sprite_url,
    )

@app.route("/sprite/<pokemon_name>")
def sprite(pokemon_name):
    sprite_url = fetch_pokemon_sprite(pokemon_name)
    if sprite_url:
        response = requests.get(sprite_url)
        if response.status_code == 200:
            return Response(response.content, mimetype="image/png")
    return "Sprite not found", 404

# ----- Calculator -----------

@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operation = request.form["operation"]
            
            # Perform the calculation based on the operation
            if operation == "+":
                result = num1 + num2
            elif operation == "-":
                result = num1 - num2
            elif operation == "*":
                result = num1 * num2
            elif operation == "/":
                result = num1 / num2
            else:
                result = "Invalid operation"
        except ValueError:
            result = "Please enter valid numbers."
    
    return render_template("calculator.html", result=result)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in
        if 'username' not in session:
            flash("You need to log in first.", "error")
            return redirect(url_for('login'))

        # Connect to the database and check user's role
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Join users and roles tables to get the user's role
            cursor.execute('''
                SELECT roles.role_name
                FROM users
                JOIN roles ON users.role_id = roles.id
                WHERE users.username = ? AND roles.id = 1
            ''', (session['username'],))
            user_role = cursor.fetchone()
        finally:
            conn.close()

        # If no admin role is found, deny access
        if user_role is None:
            flash("Access denied. Admins only.", "error")
            return redirect(url_for('login'))

        # Allow access if the user is an admin
        return f(*args, **kwargs)

    return decorated_function

@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Fetch all table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    selected_table = None
    table_data = []
    table_columns = []
    
    if request.method == 'POST':
        # Get the selected table from the dropdown
        selected_table = request.form.get('table_name')
        if selected_table:
            # Fetch data and column names for the selected table
            cursor.execute(f"PRAGMA table_info({selected_table})")
            table_columns = [info[1] for info in cursor.fetchall()]
            
            cursor.execute(f"SELECT * FROM {selected_table}")
            table_data = cursor.fetchall()
    
    conn.close()
    
    # Pass `enumerate` to the template
    return render_template(
        'admin.html', 
        tables=tables, 
        selected_table=selected_table, 
        table_data=table_data, 
        table_columns=table_columns,
        enumerate=enumerate  # Pass `enumerate`
    )

@app.route('/update_table/<table_name>', methods=['POST'])
def update_table(table_name):
    # Extract form data
    form_data = request.form.to_dict()  # Flattened dictionary of form data
    if not form_data:
        flash("No data submitted.", "error")
        return redirect(url_for('admin'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Group data by row
        rows = {}
        for key, value in form_data.items():
            # Example key format: data[0][column_name]
            parts = key.split('[')
            row_index = parts[1][:-1]  # Extract row index
            column_name = parts[2][:-1]  # Extract column name
            if row_index not in rows:
                rows[row_index] = {}
            rows[row_index][column_name] = value

        # Iterate through rows and update the database
        for row_index, row_data in rows.items():
            if 'id' not in row_data:
                flash(f"Missing ID for row {row_index}. Skipping.", "error")
                continue
            
            row_id = row_data.pop('id')  # Remove ID from data to update
            update_query = f"""
                UPDATE {table_name}
                SET {', '.join([f"{col} = ?" for col in row_data.keys()])}
                WHERE id = ?
            """
            params = list(row_data.values()) + [row_id]

            # Execute the update
            cursor.execute(update_query, params)

        conn.commit()
        flash("Table updated successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error updating table: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for('admin'))



if __name__ == '__main__':
    app.run(debug=True)