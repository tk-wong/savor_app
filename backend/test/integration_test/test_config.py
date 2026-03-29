import os

from dotenv import load_dotenv

base_dir = os.path.dirname(__file__)
selected_env_file = ".env_frontend_integration" if os.getenv("APP_MODE") == "frontend_integration" else ".env_test"
env_load_status = load_dotenv(os.path.join(base_dir, selected_env_file))
if not env_load_status:
    raise FileNotFoundError(f"Could not load {selected_env_file} file")

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Use environment variable for database name, with fallback to savor_test
SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'dev' * 32  # override for testing purposes

TESTING = True

recipe_generation_host = os.getenv("AI_COOKING_AGENT_HOST", "localhost")
recipe_generation_port = os.getenv("AI_COOKING_AGENT_PORT", "5010")
AI_COOKING_AGENT_URL = f"http://{recipe_generation_host}:{recipe_generation_port}/recipe_generation"

image_generation_host = os.getenv("IMAGE_GENERATION_HOST", "localhost")
image_generation_port = os.getenv("IMAGE_GENERATION_PORT", "5020")
IMAGE_GENERATION_URL = f"http://{image_generation_host}:{image_generation_port}/create_image"

MOCK_AI_MODELS = os.getenv("MOCK_AI_MODELS", "0") == "1"
MOCK_IMAGE_URL = os.getenv("MOCK_IMAGE_URL", "static/images/temp.png")

DROP_DB_ON_STARTUP = os.getenv("DROP_DB_ON_STARTUP", "0") == "1"
