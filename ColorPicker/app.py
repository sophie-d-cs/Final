import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from ast import literal_eval

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/history")
@login_required
def history():
    rows = db.execute("SELECT * FROM palettes WHERE user_id = ?", session["user_id"])
    return render_template("history.html", rows=rows)

@app.route("/colorPick", methods=["GET", "POST"])
@login_required
def colorPick():
    if request.method == "GET":
        return render_template("colorPick.html")
    else:
        color = request.form.get("colorVal")
        color1 = int(color[1:], 16)

        red = int(color[1:3], 16)
        green = int(color[3:5], 16)
        blue = int(color[5:7], 16)

        #get complementary colors, create complimentary color
        r, g, b = int(255-red), int(255-green), int(255-blue)  # your RGB values
        comp = "#{:02x}{:02x}{:02x}".format(r, g, b)

        #calculate new rgbs
        new_red =255-int(red/2)
        new_green = 255-int(green/2)
        new_blue = 255-int(blue/2)

        #convert new rgb to hex, create new vals
        r, g, b = int(round(new_red)), int(round(new_green)), int(round(new_blue))  # your RGB values
        color_3 = "#{:02x}{:02x}{:02x}".format(r, g, b)

        #get complementary colors again of new rgbs
        r, g, b = int(255-round(new_red)), int(255-round(new_green)), int(255-round(new_blue))  # your RGB values
        comp2 = "#{:02x}{:02x}{:02x}".format(r, g, b)

        global colors
        colors = [color, comp, color_3, comp2]
        #warm colors
        if red*1.5 >255:
            red2 = 255
        else:
            red2 = 1.5*red

        green2 = green*.75
        blue2 = blue*.75

        r, g, b = int(red2), int(green2), int(blue2) # your RGB values
        color_1_red = "#{:02x}{:02x}{:02x}".format(r, g, b) 

        #get complementary colors, create complimentary color
        r, g, b = int(255-red2), int(255-green2), int(255-blue2)  # your RGB values
        color_2_red = "#{:02x}{:02x}{:02x}".format(r, g, b)
        new_red_2 = round(255-red2/2)
        new_green_2 = round(255-green2/2)
        new_blue_2 = round(255-blue2/2)
                     
        #convert new rgb to hex, create new vals
        r, g, b = int(new_red_2), int(new_green_2), int(new_blue_2)  # your RGB values
        color_3_red = "#{:02x}{:02x}{:02x}".format(r, g, b)

        #get complementary colors again of new rgbs
        r, g, b = int(255-new_red_2), int(255-round(new_green_2)), int(255-round(new_blue_2))  # your RGB values
        color_4_red = "#{:02x}{:02x}{:02x}".format(r, g, b)
        global reds
        reds = [color_1_red, color_2_red, color_3_red, color_4_red]

        #cool colors
        if blue*1.5 >255:
            blue3 = 255
        else:
            blue3 = 1.5*blue

        red3 = red*.75

        r, g, b = int(red3), int(green), int(blue3) # your RGB values
        color_1_blue = "#{:02x}{:02x}{:02x}".format(r, g, b) 

        #get complementary colors, create complimentary color
        r, g, b = int(255-red3), int(255-green), int(255-blue3)  # your RGB values
        color_2_blue = "#{:02x}{:02x}{:02x}".format(r, g, b)
        new_red_3 = round(255-red3/2)
        new_green_3 = round(255-green/2)
        new_blue_3 = round(255-blue3/2)
                     
        #convert new rgb to hex, create new vals
        r, g, b = int(new_red_3), int(new_green_3), int(new_blue_3)  # your RGB values
        color_3_blue = "#{:02x}{:02x}{:02x}".format(r, g, b)

        #get complementary colors again of new rgbs
        r, g, b = int(255-new_red_2), int(255-round(new_green_2)), int(255-round(new_blue_2))  # your RGB values
        color_4_blue = "#{:02x}{:02x}{:02x}".format(r, g, b)
        global blues
        blues = [color_1_blue, color_2_blue, color_3_blue, color_4_blue]


        return redirect("/colorPalette")

@app.route("/colorPalette")
@login_required
def colorPalette():
    return render_template('colorPalette.html', colors = colors, reds = reds, blues = blues)    


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")

@app.route("/homePage", methods=["GET"])
def homePage():
    if request.method == "GET":
        return render_template("homePage.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
             return apology("must provide username", 403)

        #Ensure password was submitted
        elif not request.form.get("password"):
             return apology("must provide password", 403)

        #Ensure confirm password was submitted
        elif not request.form.get("confirm_password"):
             return apology("must confirm password", 403)
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if confirm_password != password:
            return apology("password must match confirmation", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        # check if username already exists
        if len(rows) == 1:
            return apology("username already in use", 403)
        id = db.execute("INSERT INTO users (username, hash) VALUES(?,?)",username, generate_password_hash(password))
        # # Remember which user has logged in, set session at register or login, when in other functions/pages, will access this using session["user_id"], bc id is local variable
        session["user_id"] = id

        # # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
