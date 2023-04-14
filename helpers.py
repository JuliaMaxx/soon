import os
from cs50 import SQL
import requests
from flask import redirect, render_template, request, session
from functools import wraps
import json
import threading
import datetime
import schedule
import time
from email.message import EmailMessage
import smtplib


import schedule
import time
import smtplib
import datetime
from email.message import EmailMessage

db = SQL("sqlite:///movies.db")

scheduled_jobs = {}


def send_email(recipient, subject, message, send_date, send_time):
    # Create the message
    msg = EmailMessage()
    msg['From'] = 'jjuliamaxxx@gmail.com'
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(message)

    # Convert the send date and time to a datetime object
    send_datetime = datetime.datetime.strptime(
        send_date + ' ' + send_time, '%Y-%m-%d %H:%M')

    def send_email_helper(msg, recipient):
        # Send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('jjuliamaxxx@gmail.com', 'lguvzwzsishpgtbf')
            smtp.send_message(msg)
            db.execute("UPDATE movies SET notified = 'TRUE' WHERE id = ? AND date=?",
                       session['users_id'], send_date)
            print("Email sent!")
    # Schedule the email to be sent
    job = schedule.every().day.at(send_time).do(send_email_helper, msg, recipient)
    scheduled_jobs[(recipient, subject, message, send_datetime)] = job
    job.next_run = send_datetime  # Set the next run time to the send date and time
    # Run the schedule

    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
    threading.Thread(target=run_schedule, daemon=True).start()


def cancel_email(recipient, subject, message, send_date, send_time):
    send_datetime = datetime.datetime.strptime(
        send_date + ' ' + send_time, '%Y-%m-%d %H:%M')
    job = scheduled_jobs.get((recipient, subject, message, send_datetime))

    if job:
        # Cancel the job and remove it from the dictionary
        schedule.cancel_job(job)
        scheduled_jobs.pop((recipient, subject, message, send_datetime))


def search_movie(title):
    url = f"https://api.themoviedb.org/3/search/multi?api_key=8e5c4304a2b0fc02884f12935ccffac9&query={title}"
    response = requests.get(url)
    response_json = response.json()
    results = response_json["results"]
    movies = []
    for result in results:
        # Check if the result is a movie or TV show
        if result["media_type"] in ["movie", "tv"]:
            movie_info = {}
            movie_info["title"] = result["title"] if result["media_type"] == "movie" else result["name"]
            movie_info["date"] = result["release_date"] if result["media_type"] == "movie" else result["first_air_date"]
            movie_info["image"] = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
            movies.append(movie_info)
    return movies


def upcoming():
    api_key = "8e5c4304a2b0fc02884f12935ccffac9"
    movie_url = f"https://api.themoviedb.org/3/movie/upcoming?api_key={api_key}&language=en-US&page="
    tv_url = f"https://api.themoviedb.org/3/tv/on_the_air?api_key={api_key}&language=en-US&page="

    upcoming = []
    counter = 0  # Counter to limit the number of results to 30

    # Loop through all pages of movie results
    page = 1
    while True:
        movie = requests.get(movie_url + str(page))
        movie_json = movie.json()
        movie_results = movie_json["results"]

        # If there are no more results, stop looping
        if not movie_results:
            break

        for result in movie_results:
            media_info = {}
            media_info["title"] = result["title"]
            media_info["date"] = result["release_date"]
            media_info["image"] = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
            media_info["media_type"] = "movie"
            # Only include media that will be released in the future
            if media_info["date"] >= datetime.datetime.today().strftime('%Y-%m-%d'):
                upcoming.append(media_info)
                counter += 1
                if counter == 30:
                    return upcoming

        page += 1

    # Loop through all pages of TV results
    page = 1
    while True:
        tv = requests.get(tv_url + str(page))
        tv_json = tv.json()
        tv_results = tv_json["results"]

        # If there are no more results, stop looping
        if not tv_results:
            break

        for result in tv_results:
            media_info = {}
            media_info["title"] = result["name"]
            media_info["date"] = result["first_air_date"]
            media_info["image"] = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
            media_info["media_type"] = "tv"
            # Only include media that will be released in the future
            if media_info["date"] >= datetime.datetime.today().strftime('%Y-%m-%d'):
                upcoming.append(media_info)
                counter += 1
                if counter == 30:
                    return upcoming

        page += 1

    return upcoming


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
