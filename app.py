import json
# Web Appmports
import psycopg2
from tempfile import mkdtemp
from flask_session import Session
from helpers import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
# Webscraping/Twitter interaction Imports
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from scraping_helpers import twitter_harvester_init, harvest_account, report_account
# AI Bot Filter Imports
import numpy as np

#Database connection stuff
# Sourcing for SQL: Psycopg documentation: http://initd.org/psycopg/docs/usage.html
conn = psycopg2.connect("postgres://mhheszaljfxliv:7cf27297de378774bdff97aadf0daf58cc20aa0dc5336fb27d5a74dac9911244@ec2-107-20-155-148.compute-1.amazonaws.com:5432/d44pn0a1kcts7q", sslmode='require')
db = conn.cursor()

# Start the browser, set the login info for the Twitter account
username = "begonebot2023@gmail.com"
password = "begonebot12"
browser = twitter_harvester_init(username=username, password=password)

# Configure application
# Login and flow control are taken from finance pset.
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
#
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # query database for name, username, and score from the users table to be displayed on the leaderboard
    db.execute("SELECT name, username, score FROM users ORDER BY score DESC")
    # commits changes
    users_stored = db.fetchall()
    # for troubleshooting
    print("THIS IS user_stored:", str(users_stored))
    return render_template("index.html", users_stored=users_stored)

@app.route("/reportbotnets", methods=["GET", "POST"])
@login_required
def reportbotnets():
    if request.method == "POST":
        # store url that the user enters
        url = request.form.get("link")
        # query submitted database for isbot and isreported true or false
        db.execute("SELECT isbot, isreported FROM submitted WHERE link = %s", (url,))
        # stores in a variable the sql query
        reported = db.fetchall()
        # for troubleshooting
        print("THIS IS reported:", str(reported))
        # check if bot was already submitted in Submit Botnets page
        if reported == []:
            message="Bot not already submitted to Submit Botnets"
            return render_template("apology.html", message=message)
        # Check if bot was already reported
        if reported[0][1]:
            message="Bot already reported"
            return render_template("apology.html", message=message)
            # check if link inputted was known to be a human
        elif reported[0][0] == False:
                message="Our best guesses indicate that this is a human"
                return render_template("apology.html", message=message)
        # Report the bot
        report_account(browser, url)
        # update submitted table to say that the link was submitted
        db.execute("UPDATE submitted SET isreported = True WHERE id = %s", (session["user_id"],))
        # commits changes
        conn.commit()
        # redirect user to leaderboard
        return render_template("reported.html")
    else:
        return render_template("report_botnets.html")



@app.route("/submitbotnets", methods=["GET", "POST"])
@login_required
def submitbotnets():
    if request.method == "POST":
        # query database for true or false statement of whether the bot the user just submitted has already been submitted
        url = request.form.get("link")
        db.execute("SELECT isbot FROM submitted WHERE link = %s", (url,))
        # stores in a variable the sql query
        reported = db.fetchall()
        # for troubleshooting
        print("THIS IS reported:", str(reported))
        # if the link is in the submitted tqble return whether it was an already submitted bot or a human
        if reported != []:
            if reported[0][0]:
                message="Bot already submitted"
                return render_template("apology.html", message=message)
            elif reported[0][0] == False:
                message="Our best guesses indicate that this is a human"
                return render_template("apology.html", message=message)
        points = 0

        # Validate URL
        if requests.get(url).status_code // 100 != 2:
            message="The URL is not valid."
            return render_template("apology.html", message=message)
        if "https://twitter.com/" not in url:
            message="This does not seem to be a Twitter URL."
            return render_template("apology.html", message=message)
        if "/staus/" in url:
            message="This seems to be a post, not an account. Plese submit an account."
            return render_template("apology.html", message=message)

        # Scrape webpage to get data to pass to neural net
        harvested_data = harvest_account(browser, url, round=1)
        # Make a call to the TF server to check if accounts look like bots or not
        r = requests.post('https://begone-tensor.herokuapp.com/checkbot', json={'all_of_data':harvested_data})
        #Parse out the information we need from the response
        this_object = r.headers
        print("Headers", str(r.headers))
        this_object = this_object['predictions_dict']
        print("Predictions dict", str(this_object))
        # Change formating of response to convert into Python dict and continue to extract
        this_object = this_object.split("'")
        this_object = '"'.join(this_object)
        this_object = json.loads(this_object)
        predictions = this_object['predictions']
        bots_found = int(this_object['bots_found'])
        print("predictions", str(predictions))

        # Look at returned data and notify user of result
        if predictions[0] == 0:
            db.execute("INSERT INTO submitted (id, link, isbot) VALUES(%s, %s, %s)", (session["user_id"], harvested_data[0]['url'], False))
            conn.commit()
            message="Our best guesses indicate that this is a human"
            return render_template("apology.html", message=message)

        # Update points
        db.execute("INSERT INTO history (id, submitted, additional, points) VALUES(%s, %s, %s, %s)", (session["user_id"], 1, bots_found - 1, bots_found * 10))
        conn.commit()

        # Log found accounts if bots or not
        for i,account in enumerate(harvested_data):
             if predictions[i] == 1:
                 db.execute("INSERT INTO submitted (id, link, isbot) VALUES(%s, %s, %s)", (session["user_id"], harvested_data[i]['url'], True))
                 conn.commit()
             else:
                 db.execute("INSERT INTO submitted (id, link, isbot) VALUES(%s, %s, %s)", (session["user_id"], harvested_data[i]['url'], False))
                 conn.commit()
        # Get the number to add points to, update the user's score
        db.execute("SELECT score FROM users WHERE id = %s", (session["user_id"],))
        current_points = db.fetchall()
        #Exploded score calculator to target syntax issue
        score = current_points[0][0]
        score = int(score)
        bot_score = bots_found * 10
        score += bot_score
        # End breakout
        db.execute("UPDATE users SET score = %s WHERE id = %s", (score, session["user_id"]))
        # commits changes
        conn.commit()
        # redirects user to homepage with leaderboard
        return render_template("found.html", botsfound=bots_found, total= score)

    else:
        # Show the submission page
        return render_template("submitbotnets.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # query database for all of the users' submitted botnets and their points to display a table of all submissions of user
    db.execute("SELECT timestamp, submitted, additional, points FROM history WHERE id = %s", (session["user_id"],))
    # commits changes
    history_table = db.fetchall()
    print("THIS IS history_table:", str(history_table))

    return render_template("history.html", history_table=history_table)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = %s;",
                          (request.form.get("username"),))
        rows = db.fetchall()
        print("THIS IS ROWS:", str(rows))
        # Ensure username exists and password is correct
        if rows != None:
            if len(rows) < 1 or not check_password_hash(rows[0][3], request.form.get("password")):
                message="Invalid username and/or password! :("
                return render_template("apology.html", message=message)
        else:
            message="Invalid username and/or password! :("
            return render_template("apology.html", message=message)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

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
    if request.method == "POST":
        # return apology if password and confirmation password don't match
        if (request.form.get("password") != request.form.get("confirmation")):
            message="Passwords don't match :("
            return render_template("apology.html", message=message)
        # query database for users with username inputted
        # Source on how to handle dropped connections: https://stackoverflow.com/questions/35651586/psycopg2-cursor-already-closed
        try:
            db.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username"),))
        except:
            conn = psycopg2.connect("postgres://mhheszaljfxliv:7cf27297de378774bdff97aadf0daf58cc20aa0dc5336fb27d5a74dac9911244@ec2-107-20-155-148.compute-1.amazonaws.com:5432/d44pn0a1kcts7q", sslmode='require')
            db = conn.cursor()
            db.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username"),))
        # commits changes
        checkusername = db.fetchall()
        # returns apology if the username is already in the users table (i.e already used)
        if checkusername != []:
            message="Username already exists :("
            return render_template("apology.html", message=message)
        # hash the password so that password itself is not stored in case of data breach
        hashed = generate_password_hash(request.form.get("password"))
        # insert inputted information into database and returns id
        id = db.execute(
            "INSERT INTO users (name, username, hash) VALUES (%s, %s, %s)", (request.form.get("name"), request.form.get("username"), hashed))
        # commit changes
        conn.commit()

        # returned id is assigned to the userid of current user
        session["user_id"] = id
        # redirects user to homepage
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/badges")
@login_required
def badges():
    """Show badges of user"""
    # query database for the score of the user
    db.execute("SELECT score FROM users WHERE id = %s", (session["user_id"],))
    # commit changes
    totalscore = db.fetchall()
    title = ""
    # query returns a list so need to store an integer in totalscore to use equalities
    totalscore = totalscore[0][0]

    # change whether the website displays if the user is a
    # beginner, competent, advanced, or expert bot hunter based on total totalscore
    # changes color of the word based on the level of bot hunter
    if totalscore < 100:
        title = "Beginner"
        color = "green"
    elif totalscore >= 100 or totalscore < 250:
        title = "Competent"
        color = "blue"
    elif totalscore >= 250 or totalscore < 500:
        title = "Advanced"
        color = "orange"
    elif totalscore >= 500:
        title = "Expert"
        color = "red"

    # defines opacities of the 4 badges
    opacity50 = .2
    opacity100 = .2
    opacity250 = .2
    opacity500 = .2

    # makes certain badges fully shown depending on whether they were earned
    if totalscore >= 50:
        opacity50 = 1
    elif totalscore >= 100:
        opacity50 = 1
        opacity100 = 1
    elif totalscore >= 250:
        opacity50 = 1
        opacity100 = 1
        opacity250 = 1

    elif totalscore >= 500:
        opacity50 = 1
        opacity100 = 1
        opacity250 = 1
        opacity500 = 1


    return render_template("badges.html", title=title, color=color, changeopacity50=opacity50, changeopacity100=opacity100, changeopacity250=opacity250, changeopacity500=opacity500)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
