import os

DEBUG = True

SECRET_KEY = os.urandom(24)

DIALECT = 'mysql'
DRIVER = 'pymysql'
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'ccwindow'
USERNAME = 'root'
PASSWORD = 'khalil666'
DB_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(
    DIALECT, DRIVER, USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)

SQLALCHEMY_DATABASE_URI = DB_URI

SQLALCHEMY_TRACK_MODIFICATIONS = False