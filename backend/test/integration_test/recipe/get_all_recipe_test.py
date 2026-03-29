import datetime


def _auth_headers(sample_login):
    return {"Authorization": f"Bearer {sample_login['user']['access_token']}"}


def test_get_all_recipe(client, sample_login, sample_recipe):
    response = client.get("/api/recipes/", headers=_auth_headers(sample_login))
    recipe_list = [
        {"id": 1, "title": "Recipe 1", "image_url": "https://example.com/recipe1.jpg"},
        {"id": 2, "title": "Recipe 2", "image_url": "https://example.com/recipe2.jpg"},
    ]
    assert response.status_code == 200
    assert response.json == {"recipes": recipe_list}


def test_get_all_recipe_no_recipes(client, sample_login):
    response = client.get("/api/recipes/", headers=_auth_headers(sample_login))
    assert response.status_code == 200
    assert response.json == {"recipes": []}


def test_get_all_recipe_filters_other_users_recipe(client, sample_login, sample_recipe, sample_recipe_other_user):
    response = client.get("/api/recipes/", headers=_auth_headers(sample_login))
    assert response.status_code == 200
    assert len(response.json["recipes"]) == 2
    titles = [recipe["title"] for recipe in response.json["recipes"]]
    assert "Other User Recipe" not in titles


def test_get_all_recipe_unauthorized(client):
    response = client.get("/api/recipes/")
    assert response.status_code == 401


def test_get_all_recipe_expired_token(client, app):
    with app.app_context():
        from flask_jwt_extended import create_access_token
        expired_token = create_access_token(identity="1", expires_delta=datetime.timedelta(seconds=-1))
    response = client.get("/api/recipes/", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json == {"msg": "Token has expired"}


def test_get_all_recipe_invalid_token(client):
    response = client.get("/api/recipes/", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 422
    assert response.json == {"msg": "Not enough segments"}
