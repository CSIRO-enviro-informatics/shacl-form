from shaclform.rdfhandling import RDFHandler
import sys
from shaclform.rendering import render_template
import os
import re


def generate_form(shape, form_destination='../miniflask/view/templates/form_contents.html',
                  map_destination='../miniflask/map.ttl'):
    # Get shape
    rdf_handler = RDFHandler(shape)
    shape = rdf_handler.get_shape()

    # Check that the file contained a shape
    if not shape:
        raise Exception('No shape provided.')

    # Get a name for the form by cutting off part of the target class URI to find a more human readable name
    # Example: http://schema.org/Person -> Person
    form_name = shape['target_class'].rsplit('/', 1)[1] if 'target_class' in shape else 'Entry'

    # Add ignored properties
    if 'ignoredProperties' in shape:
        for ignored_property_path in shape['ignoredProperties']:
            ignored_property = {
                'path': ignored_property_path,
                'name': re.split('[#/]', ignored_property_path)[-1],
                'order': None,
                'nodeKind': 'http://www.w3.org/ns/shacl#IRIOrLiteral'
            }
            shape['properties'].append(ignored_property)

    # Sort the groups
    shape['groups'] = sort_by_order(shape['groups'])
    # Sort properties in groups
    for g in shape['groups']:
        g['properties'] = sort_by_order(g['properties'])
        for prop in g['properties']:
            sort_composite_property(prop)
    # Sort ungrouped properties
    shape['properties'] = sort_by_order(shape['properties'])
    for prop in shape['properties']:
        sort_composite_property(prop)

    # Assign every property a unique ID
    next_id = 0
    for g in shape['groups']:
        for prop in g['properties']:
            assign_id(prop, next_id)
            next_id += 1
    for prop in shape['properties']:
        assign_id(prop, next_id)
        next_id += 1

    # Link pair property constraints by ID
    for g in shape["groups"]:
        for prop in g["properties"]:
            for constraint in prop:
                find_paired_properties(shape, prop, constraint)
    for prop in shape["properties"]:
        for constraint in prop:
            find_paired_properties(shape, prop, constraint)

    # Put things into template
    os.makedirs(os.path.dirname(os.path.abspath(form_destination)), exist_ok=True)
    with open(form_destination, 'w') as f:
        f.write(render_template(form_name, shape))

    # Create map for converting submitted data into RDF
    rdf_handler.create_rdf_map(shape, map_destination)


def sort_by_order(properties):
    """
    This lambda expression uses a tuple to sort items with an order before unordered items. Tuples are compared by their
    first element first, then the second, etc. False sorts before True, so all None values will be sorted to the end
    """
    properties.sort(key=lambda x: (x['order'] is None, x['order']))
    return properties


def sort_composite_property(prop):
    if 'property' in prop:
        prop['property'] = sort_by_order(prop['property'])
        for p in prop['property']:
            sort_composite_property(p)


def assign_id(prop, next_id, parent_id=None):
    # Assigns the property an ID
    # Additionally, assigns an ID to any property within this property
    if parent_id is not None:
        prop["id"] = str(parent_id) + ":" + str(next_id)
    else:
        prop["id"] = next_id
    if "property" in prop:
        next_internal_id = 0
        for p in prop["property"]:
            assign_id(p, next_internal_id, parent_id=prop["id"])
            next_internal_id += 1


def find_paired_properties(shape, prop, constraint):
    # If the constraint is a pair property constraint, iterates through all the properties looking for the one that
    # matches
    # Additionally, looks for pair property constraints in the properties contained in this property using recursion
    if constraint == "property":
        for p in prop[constraint]:
            for c in p:
                find_paired_properties(shape, p, c)
    if constraint in ["equals", "disjoint", "lessThan", "lessThanOrEquals"]:
        for g in shape["groups"]:
            for p in g["properties"]:
                result = check_property(p, prop[constraint])
                if result is not None:
                    prop[constraint] = result
                    return
        for p in shape["properties"]:
            result = check_property(p, prop[constraint])
            if result is not None:
                prop[constraint] = result
                return


def check_property(prop, path):
    # If the property path matches the path being searched for, return the property id
    # Also searches the properties inside this property using recursion
    if prop["path"] == path:
        return prop["id"]
    if "property" in prop:
        for p in prop["property"]:
            result = check_property(p, path)
            if result is not None:
                return result


if __name__ == "__main__":
    # File name passed as command-line argument
    if len(sys.argv) < 2:
        raise Exception('Usage - python main.py <SHACL file path> <optional: form destination> '
                        '<optional: map destination')
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        raise Exception('File does not exist')
    if len(sys.argv) >= 4:
        with open(file_path) as f:
            generate_form(f, sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 2:
        with open(file_path) as f:
            generate_form(f)
