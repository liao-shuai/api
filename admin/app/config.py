
from pymongo import MongoClient
import os
import sys

__current_dir = os.path.dirname(os.path.abspath(__file__))
sss_dir = os.path.dirname(__current_dir)
sys.path.append(os.path.dirname(sss_dir))

from api import conf

WTF_CSRF_ENABLED = True
SECRET_KEY = 'Put your secret key here'
DB_NAME = 'admin-test'


DATABASE = MongoClient(conf.mongo_uri, connect=False)[DB_NAME]
USERS_COLLECTION = DATABASE.users
COMMON_COLLECTION = DATABASE.common
SETTINGS_COLLECTION = DATABASE.settings

DEBUG = True


