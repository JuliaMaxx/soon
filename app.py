import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required


app = Flask(__name__)
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


db = SQL("sqlite:///movies.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == 'GET':
        return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template('error.html')

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('error.html')
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template('error.html')

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get('username')
        password = request.form.get('password')
        check = request.form.get('confirmation')
        names = db.execute("SELECT username from users;")
        email = request.form.get('email')
        # make sure user provides valid username
        if not name:
            return render_template('error.html')
        for i in range(len(names)):
            if names[i]['username'] == name:
                return render_template('error.html')

        # make sure that the password is provided
        if not password:
            return render_template('error.html')
        # make sure that the email is provided
        if not email:
            return render_template('error.html')
        # make sure that the password contains at least one letter, number and symbol
        alpha = False
        num = False
        symbol = False
        for p in password:
            if p.isalpha():
                alpha = True
            if p.isnumeric():
                num = True
            if p.isascii() and p.isnumeric() == False and p.isalpha() == False:
                symbol = True
        if alpha == False or num == False or symbol == False:
            return render_template('error.html')

        # make sure that the confirmation for the password is provided
        if not check:
            return render_template('error.html')

        # make sure that password and confirmation thereof matches
        if password != check:
            return render_template('error.html')

        # hash the password
        hash = generate_password_hash(password)

        # add user to the database
        db.execute(
            "INSERT INTO users (username, hash, email) VALUES (?, ?, ?)", name, hash, email)

        id = db.execute("SELECT id FROM users WHERE username = ?", name)
        session['user_id'] = id[0]['id']
        return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change():
    """Change user's password"""
    if request.method == "GET":
        return render_template("change_password.html")
    else:
        # get user's current password
        old = db.execute("SELECT hash FROM users WHERE id = ?",
                         session['user_id'])
        # get the updated password
        new = request.form.get("new_password")
        # get confirmation of the updated password
        confirmation = request.form.get("confirmation")

        # make sure that user typed in valid current password
        if not request.form.get("old_password") or not check_password_hash(old[0]["hash"], request.form.get("old_password")):
            return render_template('error.html')

        # make sure that user provided both updated password and confirmation thereof
        if not new or not confirmation:
            return render_template('error.html')

        # make sure that the password contains at least one letter, number and symbol
        alpha = False
        num = False
        symbol = False
        for p in new:
            if p.isalpha():
                alpha = True
            if p.isnumeric():
                num = True
            if p.isascii() and p.isnumeric() == False and p.isalpha() == False:
                symbol = True
        if alpha == False or num == False or symbol == False:
            return render_template('error.html')

        # make sure that updated password and confirmation thereof matches
        if new != confirmation:
            return render_template('error.html')

        # hash updated password
        hash = generate_password_hash(new)

        # update 'users' table
        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   hash, session["user_id"])
        flash('Password was successfully changed!')
        return redirect("/")
