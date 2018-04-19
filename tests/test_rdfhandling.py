import sys
import os
import pytest
from rdflib.term import URIRef, Literal
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
from rdfhandling import RDFHandler


def test_empty_file():
    # Checks behaviour when an empty file is supplied
    RDF_handler = RDFHandler("inputs/empty_file.ttl")
    assert RDF_handler.get_shape() == None


def test_no_target_class():
    # Checks behavior when the shape provided doesn't have a target class
    RDF_handler = RDFHandler("inputs/no_target_class.ttl")
    with pytest.raises(Exception):
        RDF_handler.get_shape()


def test_empty_shape():
    # Valid but empty shape
    expected_result = dict()
    expected_result["target_class"] = URIRef("http://schema.org/Person")
    expected_result["groups"] = list()
    expected_result["properties"] = list()
    RDF_handler = RDFHandler("inputs/empty_shape.ttl")
    result = RDF_handler.get_shape()
    assert result == expected_result


def test_no_path():
    # Checks behaviour when a property doesn't have a compulsory path constraint
    RDF_handler = RDFHandler("inputs/no_path.ttl")
    with pytest.raises(Exception):
        RDF_handler.get_shape()


def test_path():
    # Check the path is read
    expected_path = "http://schema.org/givenName"
    RDF_handler = RDFHandler("inputs/test_shape.ttl")
    properties = RDF_handler.get_shape()["properties"]
    assert any(str(p["path"] == expected_path for p in properties))


def test_invalid_mincount():
    # Check that a non-integer minCount raises the appropriate error
    RDF_handler = RDFHandler("inputs/invalid_minCount.ttl")
    with pytest.raises(Exception):
        RDF_handler.get_shape()


def test_shape():
    shape = RDFHandler("inputs/test_shape.ttl").get_shape()
    # Run the following tests on the test shape to avoid getting it every time
    # They won't be automatically discovered by pytest without the test_ prefix
    constraint_generic_constraint_test(shape)
    constraint_name_test(shape)
    constraint_order_test(shape)
    constraint_minCount_test(shape)
    constraint_in_test(shape)
    constraint_languagein_test(shape)
    constraint_min_test(shape)
    constraint_max_test(shape)
    constraint_equals_test(shape)
    constraint_disjoint_test(shape)
    constraint_lessthan_test(shape)
    constraint_lessthanorequals_test(shape)


def constraint_generic_constraint_test(shape):
    # Check the desc is read
    expected_desc = "The first name of a person."
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert str(p["description"]) == expected_desc


def constraint_name_test(shape):
    # Check the name is read
    expected_name = "Given name"
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert str(p["name"]) == expected_name

    # Check name generated from URI
    expected_name = "birthDate"
    for p in properties:
        if p["path"] == "http://schema.org/birthDate":
            assert str(p["name"]) == expected_name


def constraint_order_test(shape):
    # Check the order is read
    expected_value = 1
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert int(p["order"]) == expected_value

    # Check the order is correctly set to None when it isn't given
    for p in properties:
        if p["path"] == "http://schema.org/familyName":
            assert p["order"] is None


def constraint_minCount_test(shape):
    # Check the minimum count is read
    expected_value = 1
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/birthDate":
            assert int(p["minCount"]) == expected_value


def constraint_in_test(shape):
    # Check that the 'in' constraint options are read
    expected_value = ["Steve", "Terrence"]
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert p["in"] == expected_value


def constraint_languagein_test(shape):
    # Check that the 'languageIn' constraint options are read
    expected_value = ["en", "es"]
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/familyName":
            assert p["languageIn"] == expected_value


def constraint_min_test(shape):
    # Check that the min is read
    expected_value = 1
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://example.org/ex#gpa":
            assert p["min"] == expected_value


def constraint_max_test(shape):
    # Check that the min is read
    expected_value = 7
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://example.org/ex#gpa":
            assert p["max"] == expected_value


def constraint_equals_test(shape):
    # Check that the equals is correctly escaped
    expected_value = "http\:\/\/schema\.org\/familyName"
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert p["equals"] == expected_value


def constraint_disjoint_test(shape):
    # Check that the disjoint is correctly escaped
    expected_value = "http\:\/\/example\.org\/ex\#likesDogs"
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://example.org/ex#likesCats":
            assert p["disjoint"] == expected_value


def constraint_lessthan_test(shape):
    # Check that the lessthan uri is correctly escaped
    expected_value = "http\:\/\/example\.org\/ex\#deathDate"
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://example.org/ex#birthDate":
            assert p["lessThan"] == expected_value


def constraint_lessthanorequals_test(shape):
    # Check that the lessthanorequals uri is correctly escaped
    expected_value = "http\:\/\/example\.org\/ex\#goalGpa"
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://example.org/ex#gpa":
            assert p["lessThanOrEquals"] == expected_value


def group_test(shape):
    # Check that groups are structured correctly
    expected_label = "Birth & Death Date"
    expected_order = 0
    groups = shape["groups"]
    # Labels, optional
    assert any(g["label"] is None for g in groups)
    assert any(str(g["label"]) == expected_label for g in groups)
    # Order, optional
    assert any(g["order"] is None for g in groups)
    assert any(g["order"] == Literal(expected_order) for g in groups)
    # Contained properties
    for g in groups:
        if g["label"] == expected_label:
            assert any(p["path"] == "http://schema.org/birthDate" for p in g["properties"])
