import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    OMNIVA_COST = 3
    SECRET_KEY = 'A RANDOM STRING, LIKE A PASSWORD'
    STRIPE_SECRET_KEY = 'YOUR LIVE OR TEST KEY'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'store.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False