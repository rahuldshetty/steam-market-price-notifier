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
            NAME VARCHAR(20) NOT NULL,
            URL VARCHAR(1000),
            MONEY DOUBLE(7, 2),
            CURRENCY VARCHAR(10),
            UID INTEGER,
            FOREIGN KEY(UID) REFERENCES USERS(UID),
            PRIMARY KEY(URL, UID)
        )
    ''')
    LOGGER.info("Instantiated Tables: USERS, LINKS")