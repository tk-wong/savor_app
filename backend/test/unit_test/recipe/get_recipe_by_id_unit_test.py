import datetime


def test_get_recipe_by_id(client, mock_jwt_required, mock_get_jwt_identity, mock_session, mock_recipe_query,
                    mock_detail_recipe, mock_detail_ingredients, mock_recipe_ingredients_query):
    mock_recipe_query.filter_by.return_value.first.return_value = mock_detail_recipe
    mock_recipe_ingredients_query.join.return_value.filter_by.return_value.all.return_value = mock_detail_ingredients
    recipe_id = 1
    response = client.get(f"/api/recipes/{recipe_id}")
    correct_response = {"recipe": {"id": mock_detail_recipe.id, "title": mock_detail_recipe.title,
                                   "description": mock_detail_recipe.description,
                                   "direction": mock_detail_recipe.direction.split("\n\n"), "ingredients": [
            {"id": ingredient.ingredient.id, "name": ingredient.ingredient.name, "quantity": ingredient.quantity} for
            ingredient in mock_detail_ingredients], "image_url": mock_detail_recipe.image_url,
                                   "tips": mock_detail_recipe.tips.split("\n\n")}}
    assert response.status_code == 200
    assert response.json == correct_response

def test_get_recipe_by_id_not_found(client, mock_jwt_required, mock_get_jwt_identity, mock_session, mock_recipe_query):
    mock_recipe_query.filter_by.return_value.first.return_value = None
    recipe_id = 999
    response = client.get(f"/api/recipes/{recipe_id}")
    assert response.status_code == 404
    assert response.json == {"message": "Recipe not found"}

def test_get_recipe_by_id_empty_tips(client, mock_jwt_required, mock_get_jwt_identity, mock_session, mock_recipe_query,
                    mock_detail_recipe, mock_detail_ingredients, mock_recipe_ingredients_query):
    mock_detail_recipe.tips = ""
    mock_recipe_query.filter_by.return_value.first.return_value = mock_detail_recipe
    mock_recipe_ingredients_query.join.return_value.filter_by.return_value.all.return_value = mock_detail_ingredients
    recipe_id = 1
    response = client.get(f"/api/recipes/{recipe_id}")
    correct_response = {"recipe": {"id": mock_detail_recipe.id, "title": mock_detail_recipe.title,
                                   "description": mock_detail_recipe.description,
                                   "direction": mock_detail_recipe.direction.split("\n\n"), "ingredients": [
            {"id": ingredient.ingredient.id, "name": ingredient.ingredient.name, "quantity": ingredient.quantity} for
            ingredient in mock_detail_ingredients], "image_url": mock_detail_recipe.image_url,
                                   "tips": []}}
    assert response.status_code == 200
    assert response.json == correct_response

def test_get_recipe_by_id_empty_ingredients(client, mock_jwt_required, mock_get_jwt_identity, mock_session, mock_recipe_query,
    mock_detail_recipe, mock_recipe_ingredients_query):
    mock_recipe_ingredients_query.join.return_value.filter_by.return_value.all.return_value = []
    mock_recipe_query.filter_by.return_value.first.return_value = mock_detail_recipe
    recipe_id = 1
    response = client.get(f"/api/recipes/{recipe_id}")
    correct_response = {"recipe": {"id": mock_detail_recipe.id, "title": mock_detail_recipe.title,
                                   "description": mock_detail_recipe.description,
                                   "direction": mock_detail_recipe.direction.split("\n\n"), "ingredients": [],
                                   "image_url": mock_detail_recipe.image_url,
                                   "tips": mock_detail_recipe.tips.split("\n\n")}}
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
