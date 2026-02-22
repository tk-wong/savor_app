from database import db


class Recipe(db.Model):
    __tablename__ = 'recipes'
    id: db.Column = db.Column(db.Integer, primary_key=True)
    title: db.Column = db.Column(db.String(255), nullable=False)
    ingredients: db.Column = db.Column(db.Text, nullable=False)
    direction: db.Column = db.Column(db.Text, nullable=False)
    description: db.Column = db.Column(db.Text, nullable=True)
    tips: db.Column = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Recipe {self.title}, id: {self.id}>'
