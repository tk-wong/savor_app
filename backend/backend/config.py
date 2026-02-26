import os
import secrets

from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env_dev")
env_status = load_dotenv(env_path)
if not env_status:
    print(
        f"Warning: .env_dev file not found at {env_path}. Make sure to create it with the necessary environment variables.")
    exit(1)
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

SQLALCHEMY_TRACK_MODIFICATIONS = False

secret_key = secrets.token_hex(32)
SECRET_KEY = os.getenv("SECRET_KEY", secret_key) # generate a random one if not set

jwt_secret_key = secrets.token_hex(32)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", jwt_secret_key)  # generate a random one if not set
