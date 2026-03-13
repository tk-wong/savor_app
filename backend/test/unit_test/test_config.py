import os
from dotenv import load_dotenv



SQLALCHEMY_DATABASE_URI = f"postgresql:///"

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'testing' * 10 # override for testing purposes

TESTING = True
