from sqlalchemy import Integer, Boolean, String
import pytest


def test_model_structure_table_exists(db_inspector):
    assert db_inspector.has_table("attribute_value")


def test_model_structure_column_data_types(db_inspector):
    table = "attribute_value"
    columns = {columns["name"]: columns for columns in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], Integer)
    assert isinstance(columns["attribute_value"]["type"], String)
    assert isinstance(columns["attribute_id"]["type"], Integer)


def test_model_structure_nullable_constraints(db_inspector):
    table = "attribute_value"
    columns = db_inspector.get_columns(table)

    expected_nullable = {
        "id": False,
        "attribute_value": False,
        "attribute_id": False,
    }

    for column in columns:
        column_name = column["name"]
        assert column["nullable"] == expected_nullable.get(
            column_name
        ), f"column '{column_name} is not nullable as expected'"


def test_model_structure_column_constraints(db_inspector):
    table = "attribute_value"
    constraints = db_inspector.get_check_constraints(table)

    assert any(
        constraint["name"] == "attribute_value_name_length_check"
        for constraint in constraints
    )


def test_model_structure_column_lengths(db_inspector):
    table = "attribute_value"
    columns = {columns["name"]: columns for columns in db_inspector.get_columns(table)}

    assert columns["attribute_value"]["type"].length == 100


def test_model_structure_unique_constraints(db_inspector):
    table = "attribute_value"
    constraints = db_inspector.get_unique_constraints(table)

    assert any(
        constraint["name"] == "uq_attribute_value_attribute_id"
        for constraint in constraints
    )


def test_model_structure_foreign_key(db_inspector):
    table = "attribute_value"
    foreign_keys = db_inspector.get_foreign_keys(table)

    attribute_value_foreign_key = next(
        (fk for fk in foreign_keys if fk["constrained_columns"] == ["attribute_id"]),
        None,
    )

    assert attribute_value_foreign_key is not None
