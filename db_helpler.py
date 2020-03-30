#!/usr/bin/python
'''
This package is responsible to store details about
users and items locally
'''
import sqlite3
from utils import *

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
    conn = sqlite3.connect('database.db')
    conn.execute('''
        Create TABLE IF NOT EXISTS USERS
        (
            UID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME VARCHAR(20) NOT NULL,
            EMAIL VARCHAR(30) NOT NULL UNIQUE,
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

def create_link(conn, name, link, email):
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
        return True
    else:
        LOGGER.error("No User with email %s found.", email)
        return False