from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages and session management

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # So we can access columns by name
    return conn

# Home Route (index page)
@app.route('/')
def home():
    # Check if the user is logged in and pass this info to the template
    is_logged_in = 'user_id' in session
    return render_template('index.html', is_logged_in=is_logged_in)

# Sign Up Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        dob = request.form['dob']

        # Check if username or email already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        user = cursor.fetchone()

        if user:
            flash('Username or Email already exists!', 'danger')
            conn.close()
            return redirect(url_for('signup'))

        # Insert new user into the database
        cursor.execute('INSERT INTO users (username, email, password, dob) VALUES (?, ?, ?, ?)',
                       (username, email, password, dob))
        conn.commit()
        conn.close()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']  # Store the user's ID in session to track login state
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to home page after login
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    # Clear the session and log the user out
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))  # Redirect to home page after logout

if __name__ == '__main__':
    app.run(debug=True)
