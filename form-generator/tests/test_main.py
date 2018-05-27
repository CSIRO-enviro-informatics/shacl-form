import sys
import os
import pytest
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
import main
import copy
import shutil


def test_no_filename():
    with pytest.raises(Exception):
        main.generate_webform(None, None)


def test_file_exists():
    with pytest.raises(Exception):
        main.generate_webform('test', None)


def test_empty_file():
    with pytest.raises(Exception):
        main.generate_webform("inputs/empty_file.ttl", "results/")


def test_empty_shape():
    main.generate_webform("inputs/empty_shape.ttl", "results/")
    assert os.path.exists("results/view/templates/form_contents.html")
    assert os.path.getsize("results/view/templates/form_contents.html") == 0
    assert open("results/view/templates/form_heading.html", 'r').read() == 'Create New Person'


def test_sort_composite_property_single():
    # This function changes the structure of its input, make a copy to see whether it changed
    property = {'path': 'http://xmlns.com/foaf/0.1/phone', 'name': 'Phone Number', 'order': None}
    result = copy.deepcopy(property)
    main.sort_composite_property(result)
    assert result == property


def test_sort_composite_property_order():
    # This function changes the structure of its input, make a copy to see whether it changed
    # Should order the two properties by their 'order' key
    property = {'property': [{'order': 2, 'path': 'http://schema.org/streetAddress'},
                             {'order': 1, 'path': 'http://schema.org/postalCode'}],
                'path': 'http://schema.org/address',
                'name': 'Address',
                'order': None}
    result = {'property': [{'order': 1, 'path': 'http://schema.org/postalCode'},
                           {'order': 2, 'path': 'http://schema.org/streetAddress'}],
                'path': 'http://schema.org/address',
                'name': 'Address',
                'order': None}
    main.sort_composite_property(property)
    assert property == result


def test_assign_id_no_parent_id():
    property = dict()
    expected_result = {'id': 0}
    main.assign_id(property, 0)
    assert property == expected_result


def test_assign_id_parent_id():
    property = dict()
    expected_result = {'id': "1:0"}
    main.assign_id(property, 0, "1")
    assert property == expected_result


def test_assign_id_nested_property():
    property = {'property': [{}, {}]}
    expected_result = {'property': [{'id': '0:0'}, {'id': '0:1'}], 'id': 0}
    main.assign_id(property, 0)
    assert property == expected_result


def test_check_property_match():
    property = {'path': 'http://schema.org/givenName', 'id': 0}
    path = 'http://schema.org/givenName'
    result = main.check_property(property, path)
    expected_result = 0
    assert result == expected_result


def test_check_property_no_match():
    property = {'path': 'http://schema.org/familyName', 'id': 0}
    path = 'http://schema.org/givenName'
    result = main.check_property(property, path)
    expected_result = None
    assert result == expected_result


def test_check_property_nested_property_match():
    property = {'path': 'http://schema.org/familyName', 'property': [{'path': 'http://schema.org/givenName', 'id': 0}]}
    path = 'http://schema.org/givenName'
    result = main.check_property(property, path)
    expected_result = 0
    assert result == expected_result


def test_check_property_nested_property_no_match():
    property = {'path': 'http://schema.org/familyName', 'property': [{'path': 'http://schema.org/familyName', 'id': 0}]}
    path = 'http://schema.org/givenName'
    result = main.check_property(property, path)
    expected_result = None
    assert result == expected_result


def test_find_paired_properties_ungrouped():
    shape = {'groups': [], 'properties': [{'path': 'A', 'equals': 'B', 'id': 0, 'property': [{'path': 'B', 'id': 1}]}]}
    property = {'path': 'A', 'equals': 'B', 'id': 0, 'property': [{'path': 'B', 'id': 1}]}
    constraint = 'equals'
    expected_result = {'path': 'A', 'equals': 1, 'id': 0, 'property': [{'path': 'B', 'id': 1}]}
    main.find_paired_properties(shape, property, constraint)
    assert property == expected_result


def test_find_paired_properties_grouped():
    shape = {'groups': [{'properties': [{'path': 'A', 'equals': 'B', 'id': 0, 'property': [{'path': 'B', 'id': 1}]}]}], 'properties': []}
    property = {'path': 'A', 'equals': 'B', 'id': 0, 'property': [{'path': 'B', 'id': 1}]}
    constraint = 'equals'
    expected_result = {'path': 'A', 'equals': 1, 'id': 0, 'property': [{'path': 'B', 'id': 1}]}
    main.find_paired_properties(shape, property, constraint)
    assert property == expected_result


def test_find_paired_properties_nested():
    shape = {'groups': [], 'properties': [{'path': 'A', 'id': 0, 'property': [{'path': 'B', 'equals': 'A', 'id': 1}]}]}
    property = {'path': 'A', 'id': 0, 'property': [{'path': 'B', 'equals': 'A', 'id': 1}]}
    constraint = 'property'
    expected_result = {'path': 'A', 'id': 0, 'property': [{'path': 'B', 'equals': 0, 'id': 1}]}
    main.find_paired_properties(shape, property, constraint)
    assert property == expected_result


def test_shape():
    # Contents of result can't be verified due to RDF and therefore the HTML result being unordered
    if os.path.exists('results'):
        shutil.rmtree('results')
    main.generate_webform('inputs/test_shape.ttl', 'results/')
    assert os.path.exists("results/view/templates/form_contents.html")
    assert open("results/view/templates/form_heading.html", 'r').read() == 'Create New Person'

