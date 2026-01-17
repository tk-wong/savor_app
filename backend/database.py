from flask_sqlalchemy import SQLAlchemy

class Database:
    __db = None
    __instance  = None


    def __init__(self, app):
        if Database.__db is not None:
            raise Exception("This class is a singleton!")
        Database.__db = SQLAlchemy(app)
        Database.__instance =  self

    @staticmethod
    def get_db_instance(app):
        if Database.__instance is None:
            Database.__instance = Database(app)
        return Database.__instance