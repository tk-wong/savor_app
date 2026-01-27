import os
import secrets
from dotenv import load_dotenv
load_dotenv(".env_dev")

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

SQLALCHEMY_TRACK_MODIFICATIONS = False

secret_key = secrets.token_hex(32)
SECRET_KEY = os.getenv("SECRET_KEY", secret_key) # generate a random one if not set