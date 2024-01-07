from flask import Flask, render_template, url_for, request, g, redirect, session
from database import connect_to_database, getDatabase
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'eco_db'):
        g.eco_db.close()

def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        db = getDatabase()
        user_cursor = db.execute("select * from users where username = ?", [user])
        user_result = user_cursor.fetchone()
    return user_result

@app.route('/')
def index():
    user = get_current_user()
    show_navbar = True  # Assuming you want the navbar to be shown on the landing page
    return render_template("landing.html", user=user, show_navbar=show_navbar)

@app.route('/login', methods=["POST", "GET"])
def login():
    user = get_current_user()
    error = None
    
    if request.method == "POST":
        name = request.form['username']
        password = request.form['password']
        db = getDatabase()
        fetchedperson_cursor = db.execute("select * from users where username = ?", [name])
        personfromdatabase = fetchedperson_cursor.fetchone()
        
        if personfromdatabase:
            if password == personfromdatabase['password']:
                session['user'] = personfromdatabase['username']
                return redirect(url_for('index'))
            else:
                error = "Username or password did not match. Try again."
        else:
            error = "Username or password did not match. Try again."

    return render_template("login.html", user=user, error=error)

@app.route('/register', methods=["POST", "GET"])
def register():
    user = get_current_user()
    error = None
    
    if request.method == "POST":
        name = request.form['username']
        password = request.form['password']
        db = getDatabase()
        
        user_fetching_cursor = db.execute("select * from users where username = ?", [name])
        existing_user = user_fetching_cursor.fetchone()
        
        if existing_user:
            error = "Username already taken. Please try again."
        else:
            db.execute("insert into users (name, password, teacher, admin) values (?,?,?,?)", [name, password, '0', '0'])
            db.commit()
            session['user'] = name
            return redirect(url_for('index'))

    return render_template("register.html", user=user, error=error, show_navbar=True)

@app.route('/selectATask')
def selectATask():
    return render_template("selectATask.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/homepage')
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
