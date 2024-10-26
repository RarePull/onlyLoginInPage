from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector as c

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Set a secret key for session management

# MySQL connection details
conn = c.connect(
    host="localhost",
    user="root",
    password="asdfghjkl",
    database="rarepull_1"
)

# Function to recommend the genre of NFT to the user
def get_recommendation(username, conn):
    try:
        cur = conn.cursor()
        query = f"SELECT * FROM `{username}`"
        cur.execute(query)
        top_genre = cur.fetchall()

        # Logic to find the genre with the highest `numberLiked`
        max_genre = ("None", 0)
        for genre, number_liked in top_genre:
            if number_liked > max_genre[1]:
                max_genre = (genre, number_liked)

        return max_genre  # Return the top genre
    except Exception as e:
        flash(f"Error fetching recommendations: {str(e)}", "error")
        return None
    finally:
        cur.close()

# Function to sign up a new user
def sign_up(conn, username, password):
    try:
        cur = conn.cursor()
        cur.execute("SHOW TABLES;")
        list_of_tables = [table[0] for table in cur.fetchall()]

        if username in list_of_tables:
            flash(f"Error: Username '{username}' already exists. Please choose another username.", "error")
        else:
            # Insert the new user into userdetails
            cur.execute("INSERT INTO userdetails (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            
            # Create a personalized table for the user
            create_table_query = f"""
            CREATE TABLE `{username}` (
                genre VARCHAR(255),
                numberLiked INT
            );
            """
            cur.execute(create_table_query)
            conn.commit()
            flash(f"User '{username}' signed up successfully.", "success")

            return True
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return False
    finally:
        cur.close()

# Function to log in a user
def login(conn, username, password):
    try:
        cur = conn.cursor()
        cur.execute("SELECT password FROM userdetails WHERE username = %s", (username,))
        stored_password = cur.fetchone()

        if stored_password and stored_password[0] == password:
            flash(f"Login successful! Welcome, {username}.", "success")
            session['username'] = username  # Store username in session
            return True
        else:
            flash("Login failed. Incorrect username or password.", "error")
            return False
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return False
    finally:
        cur.close()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if sign_up(conn, username, password):
            session['username'] = username  # Store username in session
            return redirect(url_for('recommendation'))
    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login(conn, username, password):
            return redirect(url_for('recommendation'))
    return render_template("login.html")

@app.route('/rec')
def recommendation():
    username = session.get('username')
    if not username:
        flash("Please log in to see your recommendations.", "error")
        return redirect(url_for('login_page'))

    top_genre = get_recommendation(username, conn)
    return render_template('rec.html', top_genre=top_genre)

if __name__ == '__main__':
    app.run(debug=True)







