import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, search_movie, send_email, upcoming, cancel_email, search_album
import datetime
from email.mime.image import MIMEImage


app = Flask(__name__)

# configure session to use filesystem
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


# include sqlite database
db = SQL("sqlite:///movies.db")


@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # forget any user_id
    session.clear()

    # user reached route via POST
    if request.method == "POST":

        # make sure the username was submitted
        if not request.form.get("username"):
            flash('Please enter user name')
            return render_template('login.html')

        # make sure password was submitted
        elif not request.form.get("password"):
            flash('Please enter password')
            return render_template('login.html')
        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # make sure the username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Password does not match")
            return render_template('login.html')

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect("/")

    # user reached route via GET (
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # forget any user_id
    session.clear()

    # redirect user to login form
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
    # if POST
    if request.method == 'POST':
        # get the movie title
        movie = request.args.get("movie")
        # get the information about the movie
        info = search_movie(movie)

        # if user clicked the button notify
        if (request.form.get('notify')):
            # get movie release date
            date = datetime.datetime.strptime(
                request.form.get('notify'), '%Y-%m-%d')
            # get today's date
            now = datetime.datetime.today()

            # if the movie is already out
            if date <= now:
                flash('The movie is already out, go watch it!')
            # if the movie hasn't come out yet
            else:
                # get user's email
                email = db.execute(
                    'SELECT email FROM users WHERE id=?', session['user_id'])
                email = email[0]['email']
                # get movie title
                title = request.form.get('title')
                # set the subject
                subject = f"{title} is out!!!"
                # get the image
                image = request.form.get('image')
                # set the message
                message = f"HEY! {title} has come out today!\nGo ahead and check out {title}"
                # get the date
                d = request.form.get('notify')

                # check if the movies with such title is already in the database
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
                        # add movie to the database
                        db.execute(
                            "INSERT INTO movies (user_id, title, image, date, notified) VALUES (?, ?, ?, ?, ?)", session['user_id'], title, image, date, False)
                # send email
                send_email(email, subject, message,
                           d, '12:00', image)
                flash('You will be notified when the movie is out!')
            return render_template('movies.html')
        return render_template('movies.html', info=info)
    # if the request is GET
    elif request.method == 'GET' and request.args.get('movie') and request.args.get('movie') != None:
        movie = request.args.get("movie")
        info = search_movie(movie)
        return render_template('movies.html', info=info)

    return render_template("movies.html")


@app.route("/upcoming", methods=["GET", "POST"])
@login_required
def upcoming_media():
    # get the information about the upcoming movies
    info = upcoming()
    # if the request is GET
    if request.method == "GET":
        return render_template("upcoming.html", info=info)
    # if the request is POST
    else:
        # if user clicked the button notify
        if (request.form.get('notify')):
            # get movies release date
            date = datetime.datetime.strptime(
                request.form.get('notify'), '%Y-%m-%d')
            # get today's date
            now = datetime.datetime.today()
            # if the movie is already out
            if date <= now:
                flash('the movie is already out, go watch it!')
            # if the movie hasn't come out yet
            else:
                # get user's email
                email = db.execute(
                    'SELECT email FROM users WHERE id=?', session['user_id'])
                email = email[0]['email']
                # get the title
                title = request.form.get('title')
                # get the image
                image = request.form.get('image')
                # make an email subject
                subject = f"{title} is out!!!"
                # make an email message
                message = f"HEY! {title} has come out today!\nGo ahead and check out {title}"
                # get the notify date
                d = request.form.get('notify')
                # check if the movies with such title is already in the database
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
                        # add movie to the database
                        db.execute(
                            "INSERT INTO movies (user_id, title, image, date, notified) VALUES (?, ?, ?, ?, ?)", session['user_id'], title, image, date, False)
                # send email
                send_email(email, subject, message,
                           d, '12:00', image)
                flash('You will be notified when the movie is out!')
        return render_template('upcoming.html', info=info)


@app.route("/notified", methods=["GET", "POST"])
@login_required
def notified():
    # if the request is GET
    if request.method == "GET":
        # get all the information about user's chosen content
        info = db.execute(
            "SELECT title, image, date FROM movies WHERE user_id=?", session['user_id'])
        return render_template('notified.html', info=info)
    # if the request is POST
    else:
        # if clicked on the button cancel
        if (request.form.get('cancel')):
            # get title
            title = request.form.get('title')
            # delete from the database
            db.execute("DELETE FROM movies WHERE title=? AND user_id=?;",
                       title, session['user_id'])
            # get the email
            email = db.execute(
                'SELECT email FROM users WHERE id=?', session['user_id'])
            email = email[0]['email']
            # get the title
            title = request.form.get('title')
            # get the subject
            subject = f"{title} is out!!!"
            # get the date of notification
            d = request.form.get('notify')
            # get the image
            image = request.form.get('image')
            # convert date to datetime
            dt = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
            dt = dt.date()
            # get an email message
            message = f"HEY! {title} has come out today!\nGo ahead and check out {title}"
            # cancel email
            cancel_email(email, subject, message, '2023-04-20', '12:58', image)
            flash('notification was canceled')
        return redirect("/notified")


@app.route("/music", methods=["GET", "POST"])
@login_required
def music():
    # if request is POST
    if request.method == 'POST':
        # get the title of the album
        album = request.args.get("album")
        # get information about the album
        info = search_album(album)
        # if the notification button clicked
        if (request.form.get('notify')):
            # get the release date
            date = datetime.datetime.strptime(
                request.form.get('notify'), '%Y-%m-%d')
            # get today's date
            now = datetime.datetime.today()

            # if the album is already out
            if date <= now:
                flash('the album is already out, go listen to it!')
                return render_template('music.html')

            # if the album hasn't come out yet
            else:
                # get the email
                email = db.execute(
                    'SELECT email FROM users WHERE id=?', session['user_id'])
                email = email[0]['email']
                # get the title
                title = request.form.get('title')
                # create the email subject
                subject = f"{title} is out!!!"
                # get the image
                image = request.form.get('image')
                # create the email message
                message = f"HEY! {title} has come out today!\nGo ahead and check out {title}"
                # get the release date
                d = request.form.get('notify')

                # make sure that the album is not already in the database
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
                        # add album to the database
                        db.execute(
                            "INSERT INTO movies (user_id, title, image, date, notified) VALUES (?, ?, ?, ?, ?)", session['user_id'], title, image, date, False)
                # send the email
                send_email(email, subject, message,
                           str(d), '12:00', image)
                flash('You will be notified when the album is out!')
            return render_template('music.html')
        return render_template('music.html', info=info)

    # if the request is GET
    elif request.method == 'GET' and request.args.get('album'):
        album = request.args.get("album")
        info = search_album(album)
        return render_template('music.html', info=info)
    return render_template("music.html")
