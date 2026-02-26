# from flask_login import UserMixin

from backend.database import db


# from backend.login_manager import login_manager

class User(db.Model):
    __tablename__ = 'users'
    id: db.Column = db.Column(db.Integer, primary_key=True)
    username: db.Column = db.Column(db.String(80), nullable=False)
    email: db.Column = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: db.Column = db.Column(db.String(256), nullable=False)


    def __repr__(self):
        return f'<User {self.username}, Email: {self.email}, id: {self.id}>'

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
