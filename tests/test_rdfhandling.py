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


def test_constraint_name():
    # Check the name is read
    expected_name = "Given name"
    RDF_handler = RDFHandler("inputs/test_shape.ttl")
    properties = RDF_handler.get_shape()["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert str(p["name"]) == expected_name

    # Check name generated from URI
    expected_name = "birthDate"
    for p in properties:
        if p["path"] == "http://schema.org/birthDate":
            assert str(p["name"]) == expected_name


def test_constraint_description():
    # Check the desc is read
    expected_desc = "The first name of a person."
    RDF_handler = RDFHandler("inputs/test_shape.ttl")
    properties = RDF_handler.get_shape()["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert str(p["description"]) == expected_desc


def test_constraint_defaultValue():
    # Check the default value is read
    expected_value = "Steve"
    RDF_handler = RDFHandler("inputs/test_shape.ttl")
    properties = RDF_handler.get_shape()["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert str(p["defaultValue"]) == expected_value


def test_constraint_order():
    # Check the order is read
    expected_value = 1
    RDF_handler = RDFHandler("inputs/test_shape.ttl")
    properties = RDF_handler.get_shape()["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert int(p["order"]) == expected_value


def test_constraint_minCount():
    # Check the minimum count is read
    expected_value = 1
    RDF_handler = RDFHandler("inputs/test_shape.ttl")
    properties = RDF_handler.get_shape()["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/birthDate":
            assert int(p["minCount"]) == expected_value


def test_constraint_in():
    # Check that the 'in' constraint options are read
    expected_value = [Literal("Steve"), Literal("Terrence")]
    RDF_handler = RDFHandler("inputs/test_shape.ttl")
    properties = RDF_handler.get_shape()["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert p["in"] == expected_value


def test_group():
    # Check that groups are structured correctly
    expected_label = "Birth & Death Date"
    expected_order = 0
    RDF_handler = RDFHandler("inputs/test_shape.ttl")
    shape = RDF_handler.get_shape()
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
