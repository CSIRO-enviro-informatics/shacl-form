from rdfhandling import RDFHandler
import sys
from rendering import render_template


def generate_webform(filename):
    RDF_handler = RDFHandler(filename)

    # Get shape
    shape = RDF_handler.get_shape()

    # Check that the file contained a shape
    if not shape:
        raise Exception("No shape provided in: " + filename)

    # Get a name for the form by cutting off part of the target class URI to find a more human readable name
    # Example: http://schema.org/Person -> Person
    form_name = shape["target_class"].rsplit('/', 1)[1] if "target_class" in shape else "Entry"
    """
    Sort the groups
    This lambda expression uses a tuple to sort items with an order before unordered items. Tuples are compared by their
    first element first, then the second, etc. False sorts before True, so all None values will be sorted to the end
    """
    shape["groups"].sort(key=lambda x: (x["order"] is None, x["order"]))
    # Sort properties in groups
    for g in shape["groups"]:
        g["properties"].sort(key=lambda x: (x["order"] is None, x["order"]))
    # Sort ungrouped properties
    shape["properties"].sort(key=lambda x: (x["order"] is None, x["order"]))

    # Assign every property a unique ID
    # ID will also depend on whether the property is a part of another property e.g. "3-2"
    next_id = 0
    for g in shape["groups"]:
        for property in g["properties"]:
            next_id = assign_id(property, next_id)
    for property in shape["properties"]:
        next_id = assign_id(property, next_id)

    # Link pair property constraints by ID
    for g in shape["groups"]:
        for property in g["properties"]:
            for constraint in property:
                find_paired_properties(shape, property, constraint)
    for property in shape["properties"]:
        for constraint in property:
            find_paired_properties(shape, property, constraint)

    # Put things into template
    with open('result.html', 'w') as f:
        f.write(render_template(form_name, shape))


def assign_id(property, next_id):
    property["id"] = next_id
    next_id += 1
    if "property" in property:
        for p in property["property"]:
            next_id = assign_id(p, next_id)
    return next_id


def find_paired_properties(shape, property, constraint):
    if constraint == "property":
        for p in property[constraint]:
            for c in p:
                find_paired_properties(shape, p, c)
    if constraint in ["equals", "disjoint", "lessThan", "lessThanOrEquals"]:
        for g in shape["groups"]:
            for p in g["properties"]:
                result = check_property(p, str(property[constraint]))
                if result:
                    property[constraint] = result
                    return
        for p in shape["properties"]:
            result = check_property(p, str(property[constraint]))
            if result:
                property[constraint] = result
                return


def check_property(property, path):
    if str(property["path"]) == path:
        return property["id"]
    if "property" in property:
        for p in property["property"]:
            result = check_property(p, path)
            if result:
                return result


if __name__ == "__main__":
    # File name passed as command-line argument
    generate_webform(sys.argv[1])
