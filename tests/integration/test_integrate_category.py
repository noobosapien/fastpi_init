from tests.factories.models_factory import get_random_category_dict
from app.models import Category


def test_integrate_create_new_category_succesfully(client, db_session_integration):
    category = get_random_category_dict()
    category_id = category.pop("id")

    response = client.post("api/category/", json=category)

    assert response.status_code == 201

    create_category = (
        db_session_integration.query(Category).filter_by(id=category_id).first()
    )

    assert create_category is not None

    assert response.json() == {
        column.name: getattr(create_category, column.name)
        for column in create_category.__table__.columns
    }


def test_integrate_create_new_category_duplicate(client, db_session_integration):
    category_data = get_random_category_dict()

    new_category = Category(**category_data)
    db_session_integration.add(new_category)
    db_session_integration.commit()
    category_data.pop("id")

    response = client.post("api/category/", json=category_data)

    assert response.status_code == 400


def test_integrate_get_all_categories(client, db_session_integration):
    categories = [get_random_category_dict() for i in range(5)]

    for category_data in categories:
        category_data.pop("id", None)
        new_category = Category(**category_data)
        db_session_integration.add(new_category)
        db_session_integration.commit()

    response = client.get("api/category")
    assert response.status_code == 200
    assert response.json() is not None

    returned_categories = response.json()
    assert isinstance(returned_categories, list)
    assert len(returned_categories) == len(categories)

    for returned_category, inserted_category_data in zip(
        returned_categories, categories
    ):
        assert returned_category["name"] == inserted_category_data["name"]


def test_integrate_update_category_succesfully(client, db_session_integration):
    initial_category_data = get_random_category_dict()

    new_category = Category(**initial_category_data)
    db_session_integration.add(new_category)
    db_session_integration.commit()

    updated_category_data = {
        "name": "Updated Name",
        "slug": "updated_slug",
        "is_active": False,
        "level": 10,
    }

    response = client.put(
        f"/api/category/{new_category.id}", json=updated_category_data
    )

    assert response.status_code == 201

    updated_category = (
        db_session_integration.query(Category).filter_by(id=new_category.id).first()
    )

    assert updated_category is not None

    assert updated_category.name == updated_category_data["name"]
    assert updated_category.slug == updated_category_data["slug"]
    assert updated_category.is_active == updated_category_data["is_active"]
    assert updated_category.level == updated_category_data["level"]


def test_integrate_delete_category_succesfully(client, db_session_integration):
    category_data = get_random_category_dict()
    new_category = Category(**category_data)
    db_session_integration.add(new_category)
    db_session_integration.commit()

    response = client.delete(f"/api/category/{new_category.id}")

    assert response.status_code == 200

    assert response.json()["id"] == category_data["id"]
    assert response.json()["name"] == category_data["name"]

    deleted_category = (
        db_session_integration.query(Category).filter_by(id=new_category.id).first()
    )

    assert deleted_category is None


def test_integrate_create_new_category_duplicate_slug(client, db_session_integration):
    category1 = get_random_category_dict()
    category2 = get_random_category_dict()

    slug = "same-slug"
    category1["slug"] = slug
    category2["slug"] = slug

    db_session_integration.add(Category(**category1))
    db_session_integration.commit()

    response = client.post("api/category", json=category2)

    assert response.status_code == 400
