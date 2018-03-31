#!/usr/bin/python

from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import datetime
from os import urandom
from binascii import b2a_hex
from config import DATABASE as db


def main():
    collection = db['users']
    user = raw_input("Enter your username: ")
    password = raw_input("Enter your password: ")
    permissions = 'superadmin'
    nowtime = datetime.datetime.now()
    userid = b2a_hex(urandom(12))

    try:
        collection.insert({'_id': userid,
                           'username': user,
                           "password": password,
                           "permissions": permissions,
                           "resetnum": 0,
                           "resetlist": [],
                           "maketime": nowtime,
                           "lasttime": nowtime})
        print "User created."
    except DuplicateKeyError:
        print "User already present in DB."


if __name__ == '__main__':
    main()
