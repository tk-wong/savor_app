import datetime


def _auth_headers(sample_login):
    return {"Authorization": f"Bearer {sample_login['user']['access_token']}"}


def test_get_recipe_by_id(client, sample_login, sample_recipe, sample_recipe_ingredients):
    recipe_id = 1
    response = client.get(f"/api/recipes/{recipe_id}", headers=_auth_headers(sample_login))
    correct_response = {
        "recipe": {
            "id": recipe_id,
            "title": "Recipe 1",
            "description": "Test description 1",
            "direction": ["Step 1", "Step 2"],
            "ingredients": [
                {"id": 1, "name": "Ingredient 1", "quantity": "100g"},
                {"id": 2, "name": "Ingredient 2", "quantity": "200g"},
            ],
            "image_url": "https://example.com/recipe1.jpg",
            "tips": ["Tip 1", "Tip 2"],
        }
    }
    assert response.status_code == 200
    assert response.json == correct_response


def test_get_recipe_by_id_not_found(client, sample_login):
    recipe_id = 999
    response = client.get(f"/api/recipes/{recipe_id}", headers=_auth_headers(sample_login))
    assert response.status_code == 404
    assert response.json == {"message": "Recipe not found"}


def test_get_recipe_by_id_empty_tips(app, client, sample_login, sample_recipe, sample_recipe_ingredients):
    from backend.db_manager import db
    from backend.models.recipe_model import Recipe

    with app.app_context():
        recipe = Recipe.query.filter_by(id=1).first()
        recipe.tips = ""
        db.session.commit()

    recipe_id = 1
    response = client.get(f"/api/recipes/{recipe_id}", headers=_auth_headers(sample_login))
    correct_response = {
        "recipe": {
            "id": recipe_id,
            "title": "Recipe 1",
            "description": "Test description 1",
            "direction": ["Step 1", "Step 2"],
            "ingredients": [
                {"id": 1, "name": "Ingredient 1", "quantity": "100g"},
                {"id": 2, "name": "Ingredient 2", "quantity": "200g"},
            ],
            "image_url": "https://example.com/recipe1.jpg",
            "tips": [],
        }
    }
    assert response.status_code == 200
    assert response.json == correct_response


def test_get_recipe_by_id_empty_ingredients(client, sample_login, sample_recipe):
    recipe_id = 2
    response = client.get(f"/api/recipes/{recipe_id}", headers=_auth_headers(sample_login))
    correct_response = {
        "recipe": {
            "id": recipe_id,
            "title": "Recipe 2",
            "description": "Test description 2",
            "direction": ["Step A", "Step B"],
            "ingredients": [],
            "image_url": "https://example.com/recipe2.jpg",
            "tips": ["Tip A", "Tip B"],
        }
    }
    assert response.status_code == 200
    assert response.json == correct_response


def test_get_recipe_by_id_unauthorized(client):
    recipe_id = 1
    response = client.get(f"/api/recipes/{recipe_id}")
    assert response.status_code == 401
    assert response.json == {"msg": "Missing Authorization Header"}


def test_get_recipe_by_id_expired_token(client, app):
    with app.app_context():
        from flask_jwt_extended import create_access_token
        expired_token = create_access_token(identity="1", expires_delta=datetime.timedelta(seconds=-1))
    recipe_id = 1
    response = client.get(f"/api/recipes/{recipe_id}", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json == {"msg": "Token has expired"}
