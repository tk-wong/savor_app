import os
from dotenv import load_dotenv

env_load_status = load_dotenv(os.path.join(os.path.dirname(__file__), ".env_test"))
if not env_load_status:
    raise FileNotFoundError("Could not load .env_test file")

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/savor_test"

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'dev' # override for testing purposes

TESTING = True