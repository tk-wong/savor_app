import datetime


def test_get_all_recipe(client, mock_jwt_required, mock_get_jwt_identity, mock_recipe_list, mock_session):
    mock_session.query.return_value.filter_by.return_value.all.return_value = mock_recipe_list
    response = client.get("/api/recipes/")
    print(response.json)
    recipe_list = [{'id': id, 'title': title, 'image_url': image_url} for id, title, image_url in mock_recipe_list]
    assert response.status_code == 200
    assert response.json == {"recipes": recipe_list}


def test_get_all_recipe_no_recipes(client, mock_jwt_required, mock_get_jwt_identity, mock_session):
    mock_session.query.return_value.filter_by.return_value.all.return_value = []
    response = client.get("/api/recipes/")
    assert response.status_code == 200
    assert response.json == {"recipes": []}


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
