'''
This package contains server related methods.
'''
import sqlite3
import sys
import datetime
from os import environ
from flask import Flask, escape, request, render_template, redirect, url_for, session
from db_helpler import *


app = Flask(__name__)
app.secret_key = hash_string(str(datetime.datetime.now()))

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
            name = row[1]
            password = row[2]
            if hash_v == hash_string(email + name + password):
                return render_template("index.html")
            else:
                return redirect(url_for('home'))
        else:
            LOGGER.info("No email found with id: %s", email)
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

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