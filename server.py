'''
This package contains server related methods.
'''
import sqlite3
import sys
import time
import datetime
from os import environ
from flask import Flask, escape, request, render_template, redirect, url_for, session
from apscheduler.schedulers.background import BackgroundScheduler
from steam_market_api import *
from db_helpler import *

app = Flask(__name__)
app.secret_key = hash_string(str(datetime.datetime.now()))

TIME_INTERVAL_FOR_JOB_MINUTES = 30

def execute_cost_computation_job():
    print("Started executing Cost Computation Job at %s", str(datetime.datetime.now()))
    # get all links
    conn = sqlite3.connect('database.db')
    link_query = "SELECT URL, NAME, MONEY, CURRENCY, UID from LINKS"
    cursor = conn.execute(link_query)

    items_low_price_for_user = {}
    for row in cursor.fetchall():
        link = row[0]
        name = row[1]
        money = row[2]
        currency = row[3]
        uid = row[4]
        lowest_price = get_current_item_low_price(link, currency)
        if lowest_price <= money:
            if uid in items_low_price_for_user:
                items_low_price_for_user[uid].append({
                    "link": link,
                    "name": name,
                    "price": lowest_price,
                    "currency": currency,
                    "uid": uid
                })
            else:
                items_low_price_for_user[uid] = [{
                    "link": link,
                    "name": name,
                    "price": lowest_price,
                    "currency": currency,
                    "uid": uid
                }]
    # send emails to all the users
    print(items_low_price_for_user)
    print("Completed executing Cost Computation Job at %s", str(datetime.datetime.now()))

sched = BackgroundScheduler(daemon=True)
sched.add_job(execute_cost_computation_job, 'interval', minutes=TIME_INTERVAL_FOR_JOB_MINUTES)
sched.start()

# Database related processing
create_tables()

@app.route('/')
@app.route('/home')
def home():
    # check if user session exists and validate it
    if "email" in session and "hash" in session:
        # validate the hash
        email = session['email']
        hash_v = session['hash']
        conn = sqlite3.connect('database.db')
        s_query = "SELECT UID, NAME, PASSWORD from USERS where EMAIL='{}'".format(email)
        cursor = conn.execute(s_query)
        row = cursor.fetchone()
        if row:
            name = row[1]
            password = row[2]
            if hash_v == hash_string(email + name + password):
                return redirect(url_for('index'))
            else:
                return render_template("home.html")
        else:
            LOGGER.info("No email found with id: %s", email)
            return render_template("home.html")
    else:
        return render_template("home.html", error=request.args.get('error'))    

@app.route('/index')
def index():
    # check if user session exists and validate it
    if "email" in session and "hash" in session:
        # validate the hash
        email = session['email']
        hash_v = session['hash']
        conn = sqlite3.connect('database.db')
        s_query = "SELECT UID, NAME, PASSWORD from USERS where EMAIL='{}'".format(email)
        cursor = conn.execute(s_query)
        row = cursor.fetchone()
        if row:
            uid = row[0]
            name = row[1]
            password = row[2]
            if hash_v == hash_string(email + name + password):

                # get all links based on UID
                link_list = []
                link_query = "SELECT URL, NAME, MONEY, CURRENCY, LID from LINKS where UID={}".format(uid)
                cursor = conn.execute(link_query)
                for row in cursor.fetchall():
                    lowest_price = get_current_item_low_price(row[0], row[3])
                    link_list.append({
                        "link": row[0],
                        "name": row[1],
                        "money": row[2],
                        "currency": row[3],
                        "lowest_price": lowest_price,
                        "lid": row[4]
                    })
                return render_template("index.html", user={'name': name}, links=link_list, currencies=CURRENCY_LIST)
            else:
                return redirect(url_for('home'))
        else:
            LOGGER.info("No email found with id: %s", email)
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

# LINK API SECTION

@app.route('/add_link', methods=["POST"])
def add_link():
    form = request.form
    if "hash" in session and "email" in session:
        # logged in
        email = session['email']
        if "link" in form and "money" in form and "currency" in form:
            link = form['link']
            money = round(float(form['money']), 2)
            currency = form['currency']
            # get uid
            s_query = "SELECT UID, NAME from USERS where EMAIL='{}'".format(email)
            conn = sqlite3.connect('database.db')
            cursor = conn.execute(s_query)
            row = cursor.fetchone()
            if row:
                # there exists one element in row
                uid = row[0]
                user = row[1]
                name = (link.split('/')[-1]).replace("%20"," ")
                # insert query for link table
                l_query = "INSERT INTO LINKS(NAME, URL, MONEY, CURRENCY, UID) VALUES('{}','{}', {}, '{}', {})"
                l_query = l_query.format(
                    name,
                    link,
                    money,
                    currency,
                    uid
                )
                try:
                    cursor.execute(l_query)
                    conn.commit()
                except Exception as error:
                    LOGGER.error("%s link exists for user %s", link, user)
                return redirect(url_for('home'))
                
            else:
                # no users found
                LOGGER.error("No users found: %s", email)
                return redirect(url_for('logout'))
        else:
            return redirect(url_for('logout'))
    else:
        return redirect(url_for('logout'))
 
@app.route('/edit_link', methods=["POST"])
def edit_link():
    form = request.form
    if "hash" in session and "email" in session:
        # logged in
        email = session['email']
        if "link" in form and "money" in form and "currency" in form:
            link = form['link']
            lid = form['lid']
            name = (link.split('/')[-1]).replace("%20"," ")
            money = round(float(form['money']), 2)
            currency = form['currency']
            # update query query for link table
            l_query = "UPDATE LINKS SET URL = '{}', MONEY = {} , CURRENCY = '{}' WHERE LID = {};".format(
                link,
                money,
                currency,
                lid
            )
            try:
                conn = sqlite3.connect('database.db')
                conn.execute(l_query)
                conn.commit()
            except Exception as error:
                LOGGER.error("Exception - %s", error)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('logout'))

@app.route('/delete_link', methods=["POST"])
def delete_link():
    form = request.form
    if "hash" in session and "email" in session:
        # logged in
        if "lid" in form:
            lid = form['lid']
            l_query = "DELETE FROM LINKS WHERE LID = {};".format(
                lid
            )
            try:
                conn = sqlite3.connect('database.db')
                conn.execute(l_query)
                conn.commit()
            except Exception as error:
                LOGGER.error("Exception - %s", error)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('logout'))

# LOGIN SECTION

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = request.form
    if request.method == "POST" and 'email' in form and 'password' in form:
        email = form['email']
        password = hash_string(form['password'])
        if email is None or password is None or email == "" or password == "":
            return redirect(url_for('home', error="Please type both your email id, password and try again."))
        else:
            #try logging in
            conn = sqlite3.connect('database.db')
            s_query = "SELECT * from USERS where EMAIL='{}' and PASSWORD='{}'".format(email, password)
            cursor = conn.execute(s_query)
            row = cursor.fetchone()
            if row:
                # set session object and load home page
                session['email'] = email
                session['hash'] = hash_string(email + row[1] + password)
                return redirect(url_for('index'))
            else:
                LOGGER.error("Invalid email: %s", email)
                return redirect(url_for('home', error="Invalid email id and password"))
    elif request.method == "GET":
        return redirect(url_for('home', error="Access Denied."))
    else:
        return redirect(url_for('home', error="Please check your email id, password and try again."))

@app.route('/logout', methods=['GET','POST'])
def logout():
    # remove the session data
    session.pop('email', None)
    session.pop('hash', None)
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(event):
    return redirect(url_for('home', error="Error 404"))

# REGISTER SECTION

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = request.form
    if request.method == "POST" and 'email' in form and 'password' in form and 'name' in form:
        email = form['email']
        password = hash_string(form['password'])
        name = form['name']
        if email is None or password is None or email == "" or password == "" or name is None or name == "":
            return redirect(url_for('home', error="Please type both your name, email id, password and try again."))
        else:
            # insert user into database
            status = False
            try:
                conn = sqlite3.connect('database.db')
                query = "INSERT INTO USERS(NAME, EMAIL, PASSWORD) VALUES('{}','{}','{}')"
                query = query.format(
                    name,
                    email,
                    password
                )
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                status = True
            except Exception as error:
                LOGGER.error("Exception - %s", error)
                status = False
            if status:
                # user created
                return redirect(url_for('home', error="User created successfully. Try logging in."))
            else:
                # user exists or error
                return redirect(url_for('home', error="User already exists or try again later."))
    elif request.method == "GET":
        return redirect(url_for('home', error="Access Denied."))
    else:
        return redirect(url_for('home', error="Please check your email id, password and try again."))

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=environ.get("PORT", 5000))
