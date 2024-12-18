from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import hashlib
import pandas as pd
import sqlite3
import os
import requests

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

# Route to display admin page
@app.route('/admin')
def admin():
    # Retrieve all contact records
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    conn.close()

    # Render the admin page with contact data
    return render_template('admin.html', contacts=contacts)

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
            return redirect(url_for('show_blogs'))
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


if __name__ == '__main__':
    app.run(debug=True)