#!/usr/bin/python
from __future__ import absolute_import

from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import datetime
import os
import sys

__current_dir = os.path.dirname(os.path.abspath(__file__))
sss_dir = os.path.dirname(__current_dir)

from api.conf import mongo_uri

def main():
    collection = MongoClient(mongo_uri)['admin-test']['users']
    user = raw_input("Enter your username: ")
    password = raw_input("Enter your password: ")
    permissions = 'superadmin'
    nowtime = datetime.datetime.now()

    try:
        collection.insert({'_id': user,
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
