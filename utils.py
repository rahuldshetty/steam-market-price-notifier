#!/usr/bin/python
'''
This is a utility package for Steam Market Notifier
'''
import logging
from hashlib import md5

# set up the logger
LOGGER = logging.getLogger(__name__)
FILE_HANDLER = logging.FileHandler('all_logs.log')
FORMATTER = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
FILE_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLER)

def hash_string(string):
    '''
    Hashes a string using MD5.
    '''
    result = md5(string.encode())
    return result.hexdigest()

def compare_hashes(str_a, hash_a):
    '''
    Compares if the hases of str_a is equivalent to hash_a or not.
    '''
    return hash_a == hash_string(str_a)