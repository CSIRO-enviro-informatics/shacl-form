import os
import pytest
import filecmp
import copy
import shutil
from generate_form import generate_form, sort_composite_property, assign_id, check_property, find_paired_properties


def test_no_filename():
    with pytest.raises(Exception):
        generate_form(None, None)


def test_file_exists():
    with pytest.raises(Exception):
        generate_form('test', None)


def test_empty_file():
    with pytest.raises(Exception):
        with open('inputs/empty_file.ttl') as f:
            generate_form(f, form_destination='result.html', map_destination='result.ttl')


def test_empty_shape():
    with open('inputs/empty_shape.ttl') as f:
        generate_form(f, form_destination='result.html', map_destination='result.ttl')
    assert os.path.exists('result.html')
    assert filecmp.cmp('result.html', 'expected_results/empty_shape.html')


def test_sort_composite_property_single():
    # This function changes the structure of its input, make a copy to see whether it changed
    prop = {'path': 'http://xmlns.com/foaf/0.1/phone', 'name': 'Phone Number', 'order': None}
    result = copy.deepcopy(prop)
    sort_composite_property(result)
    assert result == prop


def test_sort_composite_property_order():
    # This function changes the structure of its input, make a copy to see whether it changed
    # Should order the two properties by their 'order' key
    prop = {'property': [{'order': 2, 'path': 'http://schema.org/streetAddress'},
                         {'order': 1, 'path': 'http://schema.org/postalCode'}],
            'path': 'http://schema.org/address',
            'name': 'Address',
            'order': None}
    result = {'property': [{'order': 1, 'path': 'http://schema.org/postalCode'},
                           {'order': 2, 'path': 'http://schema.org/streetAddress'}],
              'path': 'http://schema.org/address',
              'name': 'Address',
              'order': None}
    sort_composite_property(prop)
    assert prop == result


def test_assign_id_no_parent_id():
    prop = dict()
    expected_result = {'id': 0}
    assign_id(prop, 0)
    assert prop == expected_result


def test_assign_id_parent_id():
    prop = dict()
    expected_result = {'id': '1:0'}
    assign_id(prop, 0, '1')
    assert prop == expected_result


def test_assign_id_nested_property():
    prop = {'property': [{}, {}]}
    expected_result = {'property': [{'id': '0:0'}, {'id': '0:1'}], 'id': 0}
    assign_id(prop, 0)
    assert prop == expected_result


def test_check_property_match():
    prop = {'path': 'http://schema.org/givenName', 'id': 0}
    path = 'http://schema.org/givenName'
    result = check_property(prop, path)
    expected_result = 0
    assert result == expected_result


def test_check_property_no_match():
    prop = {'path': 'http://schema.org/familyName', 'id': 0}
    path = 'http://schema.org/givenName'
    result = check_property(prop, path)
    expected_result = None
    assert result == expected_result


def test_check_property_nested_property_match():
    prop = {'path': 'http://schema.org/familyName', 'property': [{'path': 'http://schema.org/givenName', 'id': 0}]}
    path = 'http://schema.org/givenName'
    result = check_property(prop, path)
    expected_result = 0
    assert result == expected_result


def test_check_property_nested_property_no_match():
    prop = {'path': 'http://schema.org/familyName', 'property': [{'path': 'http://schema.org/familyName', 'id': 0}]}
    path = 'http://schema.org/givenName'
    result = check_property(prop, path)
    expected_result = None
    assert result == expected_result


def test_find_paired_properties_ungrouped():
    shape = {'groups': [], 'properties': [{'path': 'A', 'equals': 'B', 'id': 0, 'property': [{'path': 'B', 'id': 1}]}]}
    prop = {'path': 'A', 'equals': 'B', 'id': 0, 'property': [{'path': 'B', 'id': 1}]}
    constraint = 'equals'
    expected_result = {'path': 'A', 'equals': 1, 'id': 0, 'property': [{'path': 'B', 'id': 1}]}
    find_paired_properties(shape, prop, constraint)
    assert prop == expected_result


def test_find_paired_properties_grouped():
    shape = {'groups': [{'properties': [{'path': 'A', 'equals': 'B', 'id': 0, 'property': [{'path': 'B', 'id': 1}]}]}],
             'properties': []}
    prop = {'path': 'A', 'equals': 'B', 'id': 0, 'property': [{'path': 'B', 'id': 1}]}
    constraint = 'equals'
    expected_result = {'path': 'A', 'equals': 1, 'id': 0, 'property': [{'path': 'B', 'id': 1}]}
    find_paired_properties(shape, prop, constraint)
    assert prop == expected_result


def test_find_paired_properties_nested():
    shape = {'groups': [], 'properties': [{'path': 'A', 'id': 0, 'property': [{'path': 'B', 'equals': 'A', 'id': 1}]}]}
    prop = {'path': 'A', 'id': 0, 'property': [{'path': 'B', 'equals': 'A', 'id': 1}]}
    constraint = 'property'
    expected_result = {'path': 'A', 'id': 0, 'property': [{'path': 'B', 'equals': 0, 'id': 1}]}
    find_paired_properties(shape, prop, constraint)
    assert prop == expected_result


def test_shape():
    # Contents of result can't be verified due to RDF and therefore the HTML result being unordered
    if os.path.exists('results'):
        shutil.rmtree('results')
    with open('inputs/test_shape.ttl') as f:
        generate_form(f, form_destination='result.html', map_destination='result.ttl')
    assert os.path.exists('result.html')
