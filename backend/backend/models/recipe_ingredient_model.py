from backend.db_manager import db


class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'
    id: db.Column = db.Column(db.Integer, primary_key=True)
    recipe_id: db.Column = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    ingredient_id: db.Column = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantity: db.Column = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<RecipeIngredient id: {self.id}, recipe_id: {self.recipe_id}, ingredient_id: {self.ingredient_id}, quantity: {self.quantity}>'
