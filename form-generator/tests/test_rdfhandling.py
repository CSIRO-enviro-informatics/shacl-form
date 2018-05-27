import sys
import os
import pytest
from rdflib.term import URIRef, Literal
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
from rdfhandling import RDFHandler
import rdflib


def test_empty_file():
    # Checks behaviour when an empty file is supplied
    RDF_handler = RDFHandler("inputs/empty_file.ttl")
    assert RDF_handler.get_shape() is None


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


def test_recursion():
    # Checks to make sure recursion isn't accepted
    RDF_handler = RDFHandler('inputs/recursion.ttl')
    with pytest.raises(Exception):
        RDF_handler.get_shape()


def test_implicit_target_class():
    # Checks to make sure the target class is correctly identified when implicitly declared
    RDF_handler = RDFHandler('inputs/implicit_target_class.ttl')
    shape = RDF_handler.get_shape()
    assert str(shape['target_class']) == 'http://schema.org/Person'


def test_missing_group():
    # Checks to make sure an exception is thrown if a group is referenced but does not exist
    RDF_handler = RDFHandler('inputs/missing_group.ttl')
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
    constraint_generic_test(shape)
    constraint_name_test(shape)
    constraint_order_test(shape)
    constraint_mincount_test(shape)
    constraint_in_test(shape)
    constraint_languagein_test(shape)
    constraint_min_test(shape)
    constraint_max_test(shape)
    nested_properties_test(shape)
    node_test(shape)
    group_test(shape)


def constraint_generic_test(shape):
    # Check the desc is read
    expected_desc = "The first name of a person."
    for p in shape["properties"]:
        if p["path"] == "http://schema.org/givenName":
            assert str(p["description"]) == expected_desc


def constraint_name_test(shape):
    # Check the name is read
    expected_name = "Given name"
    properties = shape["properties"]
    for p in properties:
        if p["path"] == "http://schema.org/givenName":
            assert str(p["name"]) == expected_name

    # Check name derived from URI
    expected_name = "birthDate"
    groups = shape["groups"]
    for g in groups:
        properties.extend(g["properties"])
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


def constraint_mincount_test(shape):
    # Check the minimum count is read
    expected_value = 1
    for p in shape["properties"]:
        if p["path"] == "http://schema.org/birthDate":
            assert int(p["minCount"]) == expected_value


def constraint_in_test(shape):
    # Check that the 'in' constraint options are read
    expected_value = ["Steve", "Terrence"]
    for p in shape["properties"]:
        if p["path"] == "http://schema.org/givenName":
            assert p["in"] == expected_value


def constraint_languagein_test(shape):
    # Check that the 'languageIn' constraint options are read
    expected_value = ["en", "es"]
    for p in shape["properties"]:
        if p["path"] == "http://schema.org/familyName":
            assert p["languageIn"] == expected_value


def constraint_min_test(shape):
    # Check that the min is read
    expected_value = 1
    for p in shape["properties"]:
        if p["path"] == "http://example.org/ex#gpa":
            assert p["min"] == expected_value

    # Check that the minimum is correct when calculated from the minExclusive constraint
    expected_value = 1
    for p in shape['properties']:
        if p['path'] == 'http://example.org/ex#goalGpa':
            assert p['min'] == expected_value


def constraint_max_test(shape):
    # Check that the min is read
    expected_value = 7
    for p in shape["properties"]:
        if p["path"] == "http://example.org/ex#gpa":
            assert p["max"] == expected_value

    # Check that the maximum is correct when calculated from the maxExclusive constraint
    expected_value = 7
    for p in shape['properties']:
        if p['path'] == 'http://example.org/ex#goalGpa':
            assert p['max'] == expected_value


def nested_properties_test(shape):
    # Check that properties within properties are correctly read
    expected_value = [
        {
            'node': rdflib.term.URIRef('http://example.org/ex#StreetAddressShape'),
            'order': rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')),
            'type': rdflib.term.URIRef('http://www.w3.org/ns/shacl#NodeShape'),
            'path': 'http://schema.org/streetAddress',
            'name': 'streetAddress'
        }, {
            'path': 'http://schema.org/postalCode',
            'order': rdflib.term.Literal('2', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')),
            'name': 'postalCode'}]

    for p in shape["properties"]:
        if p['path'] == 'http://schema.org/address':
            p['property'].sort(key=lambda x: (x['order'] is None, x['order']))
            assert p['property'] == expected_value


def node_test(shape):
    # Check that nodes are properly linked within properties
    expected_value = "http://example.org/ex#likesDogs"
    assert any(p["path"] == expected_value for p in shape["properties"])

    # Check that nodes are properly linked outside of properties
    expected_value = "http://example.org/ex#likesBirds"
    assert any(p["path"] == expected_value for p in shape["properties"])


def group_test(shape):
    # Check that groups are structured correctly
    expected_label = "Birth & Death Date"
    expected_order = 0
    groups = shape["groups"]
    # Labels, optional
    assert not any(g["label"] is None for g in groups)
    assert any(str(g["label"]) == expected_label for g in groups)
    # Order, optional
    assert not any(g["order"] is None for g in groups)
    assert any(g["order"] == Literal(expected_order) for g in groups)
    # Contained properties
    for g in groups:
        if str(g["label"]) == expected_label:
            assert any(p["path"] == "http://schema.org/birthDate" for p in g["properties"])
