# SOON
#### Video Demo:  <https://www.youtube.com/watch?v=elIDwOWeOyo>
#### Description:
A flask website that is meant to notify users about a release of movies, tv shows and/or albums
### Languages
<ul>
<li>Python</li>
<li>HTML</li>
<li>CSS</li>
<li>JavaScript</li>
<li>SQLite</li>
</ul>

### Files and functionality
<ol>
    <li>
        <b>app.py</b>
        <ul>
            <li>main flask app</li>
            <li>configures flask session</li>
            <li>defines '/index' route which displays the home page of the site</li>
            <li>defines '/login' route which lets the user log in</li>
            <li>defines '/logout' route which lets the user log out</li>
            <li>defines '/change_password' route which lets the user change the old password to a new one</li>
            <li>defines '/movies' route which allows the user to seach for any movie of tv show and choose any to be notified about upon the release</li>
            <li>defines '/upcoming' route which displays upcoming movies and tv shows to the user and lets them choose any to be notified about upon the release</li>
            <li>defines '/notified' route which displays any content that the user has chosen to be notified about, also provides the ability to cancel the notification</li>
            <li>defines '/music' route which allows the user to seach for any album and choose any to be notified about upon the release</li>
        </ul>
    </li>
    <br>
    <li>
        <b>helpers.py</b>
        <ul>
            <li>python file that defines additional functions that are eventually going to be imported and used in the main app</li>
            <li>defines 'send_email' function which is used to schedule and send emails to users when a release date of a movie or an album that was chosen comes</li>
            <li>defines 'cancel email function which is used to cancel previously scheduled emails'</li>
            <li>defines 'search_movie' function which uses TMDB API to get information about movies or tv shows</li>
            <li>defines 'search_album' function which uses Deezer API to get information about albums</li>
            <li>defines 'get_image' function which is used to get album covers from Last Fm API when Deezer API provides none</li>
            <li>defines 'upcoming' function which uses TMDB api to get the information about upcoming movies and tv shows </li>
            <li>defines 'check_email' function which checks the email for validity</li>
            <li>defines 'login_required' function which allows me to make sure that the user has loged in before accessing a certain feature of a website</li>
        </ul>
    </li>
    <br>
    <li>
        <b>movies.db</b>
        <ul>
            <li>sqlite3 database that contains two tables</li>
            <li>first table is named users and is used to store email, username and password hash of a given user</li>
            <li>second table is named movies and is used to store titles, images and relese dates of movies, tv shows and abums chosen by the user, besides containing information about which user has chosen it</li>
        </ul>
    </li>
    <br>
    <li>
        <b>templates</b>
        <ul>
            <li>a folder that contains all the html files</li>
            <li>the most important html file is 'layout.html' which defines how all the website pages look( icon, navbar etc.) using jinga syntax</li>
            <li>'index.html' looks exactly the same as 'layout.html' exept for the title</li>
            <li>'login.html', 'logout.html', 'register.html' and 'change password.html' display forms which allow user to accordingly log in, log out, register and change password</li>
            <li>'display.html' is another layout that is used for displaying content (movies, tv shows, albums) as image cards</li>
            <li>'movies.html', 'music.html', 'notified.html' and 'upcoming.html' are all extending 'display.html' but use forms with different actions</li>
        </ul>
    </li>
    <br>
    <li>
        <b>static</b>
        <ul>
            <li>a folder that contains js and css files, also images and an icon</li>
            <li>'styles.css' is a css file that styles navbar, search bar with autocomplete and adds an image as a background to all website pages</li>
            <li>'movie_list.js' and 'album_list.js' are used to fetch titles from TMDB API and Discogs API accordingly, to use as data for autocomplete</li>
            <li>'movies.js' and 'mosic.js' are used to add autocomplete option to 'movies.html' and 'music.html'</li>
        </ul>
    </li>
</ol>

### Acknowledging issues
<ul>
<li>To work properly, this website requires python code to run continuously. Since currently the website is in the process of being deployed, unless my local computer is running 24/7, it won't function as expected. The problem, however, should be resolved once the website is deployed</li>
<li>To create autocomplete bar for 'music.html' I used Discogs API to fetch data, but since I am using the free version, sometimes it will run out of available requests.The issue, however, is not that significant, since even in the worst case scenario it just stops showing the autocomplete results</li>
<li>It would have been really nice to have created a page that would display all the upcoming albums (the way I did that with movies and tv shows), but unfortunately i couldn't find any music APIs that might provide me with such data</li>
</ul>
