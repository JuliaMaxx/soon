import re
from flask import Flask
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
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import imghdr
db = SQL("sqlite:///movies.db")

# define a dictionary with scheduled jobs
jobs = {}


def send_email(receiver, subject, message, date_, time_, img):
    # set up the email
    msg = EmailMessage()
    msg['From'] = 'jjuliamaxxx@gmail.com'
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.set_content(message)
    # if there is an image - attach it to the message
    if img:
        # get response from image url
        resp = requests.get(img)
        # get the data
        data = resp.content
        # add the filename
        filename = 'content_image.jpg'
        # add image as an attachment to the message
        msg.add_attachment(data, maintype='image', subtype='jpeg',
                           filename=filename)
    # convert date and time to datetime
    dt = datetime.datetime.strptime(
        date_ + ' ' + time_, '%Y-%m-%d %H:%M')

    def email(msg, user_id):
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            # log in
            smtp.login('jjuliamaxxx@gmail.com', 'lguvzwzsishpgtbf')
            # send email
            smtp.send_message(msg)
            # change notified to true
            db.execute("UPDATE movies SET notified = 'TRUE' WHERE id = ? AND image=?;",
                       user_id, img)
            print("Email sent!")
    # make sure the jobs are not repeating
    if not jobs.get((receiver, subject, message, dt, img)):
        # schedule a job
        job = schedule.every().day.at(time_).do(
            email, msg, session['user_id'])
        # add a job to the dictionary of jobs
        jobs[(receiver, subject, message, dt, img)] = job
        print(jobs)
        # set the next run to datetime
        job.next_run = dt

    def run_schedule():
        # run the schedule
        while True:
            schedule.run_pending()
            time.sleep(1)
    threading.Thread(target=run_schedule, daemon=True).start()


def cancel_email(receiver, subject, message, date, time, img):
    # convert date and time to datetime
    dt = datetime.datetime.strptime(
        date + ' ' + time, '%Y-%m-%d %H:%M')

    # get the job that matches given parameters
    job = jobs.get((receiver, subject, message, dt, img))
    # if such job exists
    if job:
        # cancel the job and thus email
        schedule.cancel_job(job)
        jobs.pop((receiver, subject, message, dt, img))


def search_movie(title):
    # get data using tmdb api
    url = f"https://api.themoviedb.org/3/search/multi?api_key=8e5c4304a2b0fc02884f12935ccffac9&query={title}"
    # get response from the url and convert it to json
    resp = requests.get(url)
    resp = resp.json()
    results = resp["results"]
    # initialize a list of movies
    movies = []
    for result in results:
        # check if the result is a movie or tv show
        if result["media_type"] in ["movie", "tv"]:
            info = {}
            # get the title of a movie
            if result["media_type"] == "movie":
                info["title"] = result["title"]
            # get the title of a tv show
            else:
                info["title"] = result["name"]

            # get the release date of a movie
            if result["media_type"] == "movie":
                info["date"] = result["release_date"]
            # get the release date of a tv show
            else:
                info["date"] = result["first_air_date"]
            # get the image of a movie or a tv show
            info["image"] = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
            # add information about current movie to the list of movies
            movies.append(info)
    return movies


def search_album(title):
    # get data from deezer api
    url = "https://api.deezer.com/search/album"
    # search based on the title provided
    params = {"q": f"{title}"}
    # get response from the api
    resp = requests.get(url, params=params)
    # initialize a list of album ids
    ids = []
    # check if the response was ok
    if resp.status_code == 200:
        # convert data to json
        resp = resp.json()
        # check if there is a data key in the response dictionary
        if "data" in resp and len(resp["data"]) > 0:
            # iterate through the data
            for d in resp['data']:
                # get the id of each album
                id = d["id"]
                # add id to the ids list
                ids.append(id)
        else:
            # exit if there was an error
            exit()
    else:
        # if there was an error - print the status code and exit
        print(f"Error:{resp.status_code}")
        exit()

    info = []
    # iterate through the ids list
    for id in ids:
        # get the data from deezer api
        url1 = f"https://api.deezer.com/album/{id}"
        # get the response from the api
        resp1 = requests.get(url1)

        # check if the response was ok
        if resp1.status_code == 200:
            # convert response to json
            resp1 = resp1.json()
            inf = {}
            # get the title and the artist name of the album
            inf["title"] = resp1["title"] + \
                " " + '-'+' ' + resp1["artist"]["name"]
            # get the release date of the album
            inf["date"] = resp1["release_date"]

            # if there is no image - get image from another api
            if resp1['cover_xl'] == '' or resp1['cover_xl'] == None:
                img = get_image(resp1['title'])
                inf['image'] = img
            # if there is an image - get the image
            else:
                inf["image"] = resp1["cover_xl"]
            # add information about current album to the list of all the albums
            info.append(inf)
        else:
            # if there was an error - print the status code
            print(f"Error:{resp1.status_code}")
    return info

# helper function to get the image from last fm api if the deezer api provides none


def get_image(title):
    # get the data from the url
    url = "http://ws.audioscrobbler.com/2.0/?method=album.search&api_key=5d6840079ddfebe3815942e2f55a8599&format=json"
    # search for a given album title
    params = {"album": f"{title}"}
    # get the response from the api
    resp = requests.get(url, params=params)
    # convert response to json and get the image
    image = resp.json()[
        'results']['albummatches']['album'][0]['image'][-1]['#text']
    return image


def upcoming():
    key = "8e5c4304a2b0fc02884f12935ccffac9"
    # get the data from tmdb api
    m_url = f"https://api.themoviedb.org/3/movie/upcoming?api_key={key}&language=en-US&page="
    t_url = f"https://api.themoviedb.org/3/tv/on_the_air?api_key={key}&language=en-US&page="

    upcoming = []
    counter = 0

    # get movie information
    # initialy - get the information from the page 1 - then increase the page count
    page = 1
    while True:
        # get the response from the api
        movie = requests.get(m_url + str(page))
        # convert response to json
        movie = movie.json()
        m_results = movie["results"]

        # break if there are no more results
        if not m_results:
            break

        for result in m_results:
            info = {}
            # get the title
            info["title"] = result["title"]
            # get the release date
            info["date"] = result["release_date"]
            # get the image
            info["image"] = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
            # get only the movies that haven't come out yet
            if info["date"] >= datetime.datetime.today().strftime('%Y-%m-%d'):
                # add information to the list of upcoming movies and tv shows
                upcoming.append(info)
                counter += 1
                # limit the numer of results to 40
                if counter == 40:
                    return upcoming
        # increase the page count
        page += 1

    # get tv show information
    # initialy - get the information from the page 1 - then increase the page count
    page = 1
    while True:
        # get the resoponse from the api
        tv = requests.get(t_url + str(page))
        # convert the response to json
        tv = tv.json()
        t_results = tv["results"]

        # break if there are no more results
        if not t_results:
            break

        for result in t_results:
            info = {}
            # get the title
            info["title"] = result["name"]
            # get the release date
            info["date"] = result["first_air_date"]
            # get the image
            info["image"] = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
            # get only the tv shows that haven't come out yet
            if info["date"] >= datetime.datetime.today().strftime('%Y-%m-%d'):
                # add information to the list of upcoming movies and tv shows
                upcoming.append(info)
                counter += 1
                # limit the numer of results to 40
                if counter == 40:
                    return upcoming
        # increase the page count
        page += 1

    return upcoming


def check_email(email):
    # check if the email is valid
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


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
