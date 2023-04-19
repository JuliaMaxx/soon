import os
from cs50 import SQL
import requests
from flask import redirect, session
from functools import wraps
import json
import threading
import datetime
import schedule
import time
from email.message import EmailMessage
import smtplib
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


def upcoming_music():
    return


def search_album(title):

    url = "https://api.deezer.com/search/album"
    params = {"q": f"{title}"}

    # Make the API request to search for the album
    response = requests.get(url, params=params)
    ids = []
    # Check if the search request was successful
    if response.status_code == 200:
        # Get the album ID from the search response
        response = response.json()
        if "data" in response and len(response["data"]) > 0:
            for d in response['data']:
                album_id = d["id"]
                ids.append(album_id)
        else:
            print("Error: Album not found.")
            exit()
    else:
        print("Error:", response.status_code)
        exit()

    info = []
    # Set up the API endpoint to get detailed information about the album
    for id in ids:
        url1 = f"https://api.deezer.com/album/{id}"

        # Make the API request to get detailed information about the album
        response1 = requests.get(url1)

        # Check if the album request was successful
        if response1.status_code == 200:
            # Get the album information from the album response
            response1 = response1.json()
            album_info = {}
            album_info["title"] = response1["title"] + \
                " " + '-'+' ' + response1["artist"]["name"]
            album_info["date"] = response1["release_date"]
            if response1['cover_xl'] == '' or response1['cover_xl'] == None:
                img = get_image(response1['title'])
                album_info['image'] = img
            else:
                album_info["image"] = response1["cover_xl"]
            info.append(album_info)
            # Print out the album information
        else:
            print("Error:", response1.status_code)
    return info


def get_image(title):
    url = "http://ws.audioscrobbler.com/2.0/?method=album.search&api_key=5d6840079ddfebe3815942e2f55a8599&format=json"
    params = {"album": f"{title}"}
    response = requests.get(url, params=params)
    image = response.json()[
        'results']['albummatches']['album'][0]['image'][-1]['#text']
    return image


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
