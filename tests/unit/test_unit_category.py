from app.schemas.category_schema import CategoryCreate
import pytest
from pydantic import ValidationError
from tests.factories.models_factory import get_random_category_dict
from app.models import Category
from fastapi import HTTPException


def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value


def test_unit_schema_category_validation():
    valid_data = {"name": "test category", "slug": "test_slug"}
    category = CategoryCreate(**valid_data)
    assert category.name == "test category"
    assert category.is_active is False
    assert category.level == 100
    assert category.parent_id is None

    invalid_data = {"naem": "test_name", "slug": "test_slug"}

    with pytest.raises(ValidationError):
        CategoryCreate(**invalid_data)


def test_unit_create_new_category_succesfully(client, monkeypatch):
    category = get_random_category_dict()

    for key, value in category.items():
        monkeypatch.setattr(Category, key, value)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    body = category.copy()
    body.pop("id")

    response = client.post("api/category", json=body)

    assert response.status_code == 201
    assert response.json() == category


@pytest.mark.parametrize(
    "existing_category, category_data, expected_detail",
    [
        (True, get_random_category_dict(), "Category name and level exists"),
        (True, get_random_category_dict(), "Category slug exists"),
    ],
)
def test_unit_create_new_category_existing(
    client, monkeypatch, existing_category, category_data, expected_detail
):
    def mock_check_existing_category(db, category_data):
        if existing_category:
            raise HTTPException(status_code=400, detail=expected_detail)

    monkeypatch.setattr(
        "app.routers.category_routes.check_existing_category",
        mock_check_existing_category,
    )

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    body = category_data.copy()
    body.pop("id")
    response = client.post("api/category", json=body)

    assert response.status_code == 400

    if expected_detail:
        assert response.json() == {"detail": expected_detail}


def test_unit_create_new_category_with_internal_server_error(client, monkeypatch):
    category = get_random_category_dict()

    def mock_create_category_exception(*args, **kwargs):
        raise Exception("Internal server error")

    for key, value in category.items():
        monkeypatch.setattr(Category, key, value)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_create_category_exception)

    body = category.copy()
    body.pop("id")
    response = client.post("api/category", json=body)

    assert response.status_code == 500


# get
def test_unit_get_all_categories_succesfully(client, monkeypatch):
    category = [get_random_category_dict(i) for i in range(5)]
    monkeypatch.setattr("sqlalchemy.orm.Query.all", mock_output(category))

    response = client.get("api/category")
    assert response.status_code == 200
    assert response.json() == category


def test_unit_get_all_categories_return_empty(client, monkeypatch):
    category = []
    monkeypatch.setattr("sqlalchemy.orm.Query.all", mock_output(category))

    response = client.get("api/category")
    assert response.status_code == 200
    assert response.json() == category


def test_unit_get_category_all_with_internal_server_error(client, monkeypatch):
    def mock_create_category_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.all", mock_create_category_exception)

    response = client.get("api/category")

    assert response.status_code == 500


@pytest.mark.parametrize("category", [get_random_category_dict() for _ in range(3)])
def test_unit_get_single_category_succesfully(client, monkeypatch, category):
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(category))

    response = client.get(f"api/category/slug/{category['slug']}")
    assert response.status_code == 200
    assert response.json() == category


@pytest.mark.parametrize("category", [get_random_category_dict() for _ in range(3)])
def test_unit_get_single_category_not_found(client, monkeypatch, category):
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())

    response = client.get(f"api/category/slug/{category['slug']}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Category does not exist"}


@pytest.mark.parametrize("category", [get_random_category_dict() for _ in range(3)])
def test_unit_get_single_category_with_internal_server_error(
    client, monkeypatch, category
):
    def mock_create_category_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_create_category_exception)

    response = client.get(f"api/category/slug/{category['slug']}")

    assert response.status_code == 500


# put
def test_unit_update_category_succesfully(client, monkeypatch):
    category_dict = get_random_category_dict()
    category_instance = Category(**category_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(category_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    body = category_dict.copy()
    body.pop("id")

    response = client.put("api/category/1", json=body)
    assert response.status_code == 201
    assert response.json() == category_dict


def test_unit_update_category_not_found(client, monkeypatch):
    category_dict = get_random_category_dict()

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    body = category_dict.copy()
    body.pop("id")

    response = client.put("api/category/1", json=body)
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_unit_update_category_internal_error(client, monkeypatch):
    category_dict = get_random_category_dict()

    def mock_create_category_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_create_category_exception)

    body = category_dict.copy()
    body.pop("id")

    response = client.put("api/category/1", json=body)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


# delete
def test_unit_delete_category_succesfully(client, monkeypatch):
    category_dict = get_random_category_dict()
    category_instance = Category(**category_dict)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(category_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.delete", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())

    response = client.delete("api/category/1")
    expected_json = {"id": category_dict["id"], "name": category_dict["name"]}
    assert response.status_code == 200
    assert response.json() == expected_json


def test_unit_delete_category_not_found(client, monkeypatch):
    category = []

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(category))
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    response = client.delete("api/category/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_unit_delete_category_internal_error(client, monkeypatch):
    def mock_create_category_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_create_category_exception)

    response = client.delete("api/category/1")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
