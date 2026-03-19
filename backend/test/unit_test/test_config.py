SQLALCHEMY_DATABASE_URI = f"postgresql:///"

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'testing' * 10 # override for testing purposes

TESTING = True

RECIPE_GENERATION_URL = f"http://localhost:5010/recipe_generation"

IMAGE_GENERATION_URL = f"http://localhost:5020/create_image"
