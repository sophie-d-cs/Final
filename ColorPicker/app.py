import os

#how to import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

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


@app.route("/")
@login_required
def index():
    rows = db.execute("SELECT SUM(shares) AS shares, symbol FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])
    final_rows = []
    for row in rows:
        # get price
        price = lookup(row["symbol"])['price']
        row['price'] = price
        if row['shares'] > 0:
            final_rows.append(row)
    return render_template("index.html", rows=final_rows)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # checks if symbol valid
    if request.method == "POST":
        if not request.form.get("symbol"):
             return apology("must provide symbol", 403)
        symbol = request.form.get("symbol")
        if not symbol.isalpha():
            return apology("symbol should only contain letters", 403)
        if lookup(symbol) == None :
            return apology("symbol not found", 403)
        # check if shares valid
        if not request.form.get("shares"):
             return apology("must provide number of shares", 403)
        shares = (request.form.get("shares"))
        if shares.isalpha():
            return apology("shares should only contain numbers", 403)
        shares = int(shares)
        if shares <= 0:
            return apology("shares should only contain positive numbers", 403)
        # does buy and redirects to homepage
        else:
            # make variables for all parts of sale
            result = lookup(symbol)
            price = result["price"]
            user_id = session.get("user_id")
            date = datetime.now()
            current_date = date.strftime("%Y-%m-%d %H:%M:%S")
            cost = price*shares
            rows = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
            cash = rows[0]["cash"]
            # checks to make sure have enough money in bank
            if cost > cash:
                return apology("you don't have enough money to do this", 403)
            else:
                # does sale, updates amount of money user has and records transaction
                new_cash_value = cash - cost
                db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash_value, user_id)
                db.execute("INSERT INTO transactions (user_id, symbol, date, shares, price) VALUES (?,?,?,?,?)", user_id, symbol, current_date, shares, price)
                # takes user to homepage
                return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    rows = db.execute("SELECT * FROM transactions WHERE user_id = ?", session["user_id"])
    return render_template("history.html", rows=rows)





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

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        # checks if symbol is valid
        if not request.form.get("symbol"):
             return apology("must provide symbol", 403)
        symbol = request.form.get("symbol")
        if not symbol.isalpha():
            return apology("symbol should only contain letters", 403)
        if lookup(symbol) == None :
            return apology("symbol not found", 403)
        # looks up symbol
        else:
            result = lookup(symbol)
            session['symbol'] = result
            return redirect("/quoted")
    else:
        return render_template("quote.html")

@app.route("/quoted")
@login_required
def quoted():
    # shows results of looking up symbol
    result = session.get('symbol', None)
    return render_template('quoted.html', result=result)

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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # think of selling as buying negative stock
    # checks if symbol valid
    if request.method == "POST":
        if not request.form.get("symbol"):
             return apology("must provide symbol", 403)
        symbol = request.form.get("symbol")
        if not symbol.isalpha():
            return apology("symbol should only contain letters", 403)
        if lookup(symbol) == None :
            return apology("symbol not found", 403)
        # check if shares valid
        if not request.form.get("shares"):
             return apology("must provide number of shares", 403)
        shares = (request.form.get("shares"))
        if shares.isalpha():
            return apology("shares should only contain numbers", 403)
        shares = int(shares)
        if shares <= 0:
            return apology("shares should only contain positive numbers", 403)
        #checking to see if have shares of it already
        current_shares = db.execute("SELECT SUM(shares) AS shares FROM transactions WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
        print(current_shares)
        if current_shares[0]['shares'] == None:
            return apology("you haven't bought any", 403)
        current_shares = current_shares[0]['shares']
        print(current_shares)
        # checking to see if selling too many shares
        if current_shares < shares:
            return apology("you are trying to sell too many shares", 403)
        # does sell and redirects to homepage
        else:
            # make variables for all parts of sale
            result = lookup(symbol)
            price = result["price"]
            user_id = session.get("user_id")
            date = datetime.now()
            current_date = date.strftime("%Y-%m-%d %H:%M:%S")
            profit = price*shares
            rows = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
            cash = rows[0]["cash"]
            # does sale, updates amount of money user has and records transaction
            new_cash_value = cash + profit
            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash_value, user_id)
            db.execute("INSERT INTO transactions (user_id, symbol, date, shares, price) VALUES (?,?,?,?,?)", user_id, symbol, current_date, -shares, price)
            # takes user to homepage
            return redirect("/")
    else:
        return render_template("sell.html")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        # check if shares valid
        if not request.form.get("add"):
             return apology("must provide amount of money you want to add", 403)
        add = (request.form.get("add"))
        if add.isalpha():
            return apology("amount of money should only contain numbers", 403)
        add = int(add)
        if add <= 0:
            return apology("money should only contain positive numbers", 403)
        money1 = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash1 = money1[0]["cash"]
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash1+add, session["user_id"])
        return render_template("profile.html", cash=usd(cash1))
    else:
        money = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = money[0]["cash"]
        return render_template("profile.html", cash=usd(cash))
