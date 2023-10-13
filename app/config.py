import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SECRET_KEY = os.environ['SECRET_KEY_FLASK']
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'uploads')
