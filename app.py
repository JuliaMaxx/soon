import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, search_movie, send_email, upcoming, cancel_email, search_album
import datetime


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


@app.route("/", methods=["GET"])
@login_required
def index():
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
            flash('enter user name')
            return render_template('login.html')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('enter password')
            return render_template('login.html')
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("password does not match")
            return render_template('login.html')

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
            flash('enter a name')
            return render_template('register.html')
        for i in range(len(names)):
            if names[i]['username'] == name:
                flash('username is taken')
                return render_template('register.html')

        # make sure that the password is provided
        if not password:
            flash('enter a password')
            return render_template('register.html')
        # make sure that the email is provided
        if not email:
            flash('enter email')
            return render_template('register.html')
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
            flash('your password must contain letters, numbers and symbols')
            return render_template('register.html')

        # make sure that the confirmation for the password is provided
        if not check:
            flash('enter confirmation password')
            return render_template('register.html')

        # make sure that password and confirmation thereof matches
        if password != check:
            flash('two password does not match')
            return render_template('register.html')

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
            flash('enter valid password')
            return render_template('change_password.html')

        # make sure that user provided both updated password and confirmation thereof
        if not new or not confirmation:
            flash('enter password')
            return render_template('change_password.html')

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
            flash('password must contain letters, numbers and symbols')
            return render_template('change_password.html')

        # make sure that updated password and confirmation thereof matches
        if new != confirmation:
            flash('two passwords does not match')
            return render_template('change_password.html')

        # hash updated password
        hash = generate_password_hash(new)

        # update 'users' table
        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   hash, session["user_id"])
        flash('Password was successfully changed!')
        return redirect("/")


@app.route("/movies", methods=["GET", "POST"])
@login_required
def movies():
    if request.method == "GET":
        return render_template("movies.html")
    else:
        movie = request.form.get("movie")
        info = search_movie(movie)
        if (request.form.get('notify')):
            date = datetime.datetime.strptime(
                request.form.get('notify'), '%Y-%m-%d')
            now = datetime.datetime.today()
            if date <= now:
                flash('the movie is already out, go watch it!')
            else:
                email = db.execute(
                    'SELECT email FROM users WHERE id=?', session['user_id'])
                email = email[0]['email']
                title = request.form.get('title')
                subject = f"{title} is out!!!"
                image = request.form.get('image')
                message = f"{title} has come out today! Go watch {title}"
                d = request.form.get('notify')
                send_email(email, subject, message, d, '13:00')
                flash('You will be notified when the movie is out!')
                names = db.execute(
                    "SELECT title FROM movies WHERE user_id=?", session['user_id'])
                if not names:
                    db.execute(
                        "INSERT INTO movies (user_id, title, image, date, notified) VALUES (?, ?, ?, ?, ?)", session['user_id'], title, image, date, False)
                else:
                    chosen = False
                    for name in names:
                        if title == name['title']:
                            chosen = True
                            break
                    if chosen != True:
                        db.execute(
                            "INSERT INTO movies (user_id, title, image, date, notified) VALUES (?, ?, ?, ?, ?)", session['user_id'], title, image, date, False)
        return render_template('movies.html', info=info)


@app.route("/upcoming", methods=["GET", "POST"])
@login_required
def upcoming_media():
    info = upcoming()
    if request.method == "GET":
        return render_template("upcoming.html", info=info)
    else:
        if (request.form.get('notify')):
            date = datetime.datetime.strptime(
                request.form.get('notify'), '%Y-%m-%d')
            now = datetime.datetime.today()
            if date <= now:
                flash('the movie is already out, go watch it!')
            else:
                email = db.execute(
                    'SELECT email FROM users WHERE id=?', session['user_id'])
                email = email[0]['email']
                title = request.form.get('title')
                image = request.form.get('image')
                subject = f"{title} is out!!!"
                message = f"{title} has come out today! Enjoy {title}"
                d = request.form.get('notify')
                send_email(email, subject, message, d, '14:00')
                flash('You will be notified when the movie is out!')
                names = db.execute(
                    "SELECT title FROM movies WHERE user_id=?", session['user_id'])
                if not names:
                    db.execute(
                        "INSERT INTO movies (user_id, title, image, date, notified) VALUES (?, ?, ?, ?, ?)", session['user_id'], title, image, date, False)
                else:
                    chosen = False
                    for name in names:
                        if title == name['title']:
                            chosen = True
                            break
                    if chosen != True:
                        db.execute(
                            "INSERT INTO movies (user_id, title, image, date, notified) VALUES (?, ?, ?, ?, ?)", session['user_id'], title, image, date, False)

        return render_template('upcoming.html', info=info)


@app.route("/notified", methods=["GET", "POST"])
@login_required
def notified():
    if request.method == "GET":
        info = db.execute(
            "SELECT title, image, date FROM movies WHERE user_id=?", session['user_id'])
        return render_template('notified.html', info=info)
    else:
        if (request.form.get('cancel')):
            title = request.form.get('title')

            db.execute("DELETE FROM movies WHERE title=? AND user_id=?;",
                       title, session['user_id'])

            email = db.execute(
                'SELECT email FROM users WHERE id=?', session['user_id'])
            email = email[0]['email']
            title = request.form.get('title')
            subject = f"{title} is out!!!"
            d = request.form.get('notify')
            dt = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
            dt = dt.date()
            message = f"{title} has come out today! Enjoy {title}"
            cancel_email(email, subject, message, str(dt), '14:00')
            flash('notification was canceled')
        return redirect("/notified")


@app.route("/music", methods=["GET", "POST"])
@login_required
def music():
    if request.method == "GET":
        return render_template("music.html")
    else:
        album = request.form.get("album")
        info = search_album(album)
        if (request.form.get('notify')):
            date = datetime.datetime.strptime(
                request.form.get('notify'), '%Y-%m-%d')
            now = datetime.datetime.today()
            if date <= now:
                flash('the album is already out, go listen to it!')
            else:
                email = db.execute(
                    'SELECT email FROM users WHERE id=?', session['user_id'])
                email = email[0]['email']
                title = request.form.get('title')
                subject = f"{title} is out!!!"
                image = request.form.get('image')
                message = f"{title} has come out today! Enjoy {title}"
                d = request.form.get('notify')
                send_email(email, subject, message, d, '13:00')
                flash('You will be notified when the album is out!')
                names = db.execute(
                    "SELECT title FROM movies WHERE user_id=?", session['user_id'])
                if not names:
                    db.execute(
                        "INSERT INTO movies (user_id, title, image, date, notified) VALUES (?, ?, ?, ?, ?)", session['user_id'], title, image, date, False)
                else:
                    chosen = False
                    for name in names:
                        if title == name['title']:
                            chosen = True
                            break
                    if chosen != True:
                        db.execute(
                            "INSERT INTO movies (user_id, title, image, date, notified) VALUES (?, ?, ?, ?, ?)", session['user_id'], title, image, date, False)
        return render_template('music.html', info=info)
