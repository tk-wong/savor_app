from backend.db_manager import db


class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id: db.Column = db.Column(db.Integer, primary_key=True)
    name: db.Column = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Ingredient id: {self.id},name: {self.name}>'
