#!/usr/bin/python
'''
This package is responsible to store details about
users and items locally
'''
import sqlite3
from utils import *

conn = sqlite3.connect('database.db')
LOGGER.info("Opened database connection")

'''

Table Definitions:
------------------
USERS(UID, NAME, EMAIL, PASSWORD)
LINKS(LID, NAME, URL, UID*)

Note: * represents Foreign Key
'''

def create_tables():
    '''
    Create a user and links table
    '''
    conn.execute('''
        Create TABLE IF NOT EXISTS USERS
        (
            UID INTEGER AUTOINCREMENT,
            NAME VARCHAR(20) NOT NULL,
            EMAIL VARCHAR(30) PRIMARY KEY NOT NULL,
            PASSWORD VARCHAR(500) NOT NULL
        );
    ''')

    conn.execute('''
        Create TABLE IF NOT EXISTS LINKS
        (
            LID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME VARCHAR(20) NOT NULL,
            URL VARCHAR(1000) NOT NULL,
            UID INTEGER,
            FOREIGN KEY(UID) REFERENCES USERS(UID)
        )
    ''')
    LOGGER.info("Instantiated Tables: USERS, LINKS")

def create_user(name, email, password):
    '''
    Adds a user into the database
    '''
    # hash the password
    password = hash_string(password)

    # insert query for user table
    query = "INSERT INTO USERS(NAME, EMAIL, PASSWORD) VALUES('{}','{}','{}')"
    query = query.format(
        name,
        email,
        password
    )

    conn.execute(query)
    conn.commit()
    LOGGER.info("Inserted User: %s", name)

def create_link(name, link, email):
    '''
    Adds a link to a particular user
    '''
    # get the uid for the email
    s_query = "SELECT UID from USERS where EMAIL='{}'".format(email)
    cursor = conn.execute(s_query)
    if cursor is not None:
        row = cursor.fetchone()
        uid = row[0]

        # insert query for link table
        l_query = "INSERT INTO LINKS(NAME, URL, UID) VALUES('{}','{}',{})"
        l_query = l_query.format(
            name,
            link,
            uid
        )

        # commit the row
        conn.execute(l_query)
        conn.commit()
    else:
        LOGGER.error("No User with email %s found.", email)

