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

    # Put things into template
    with open('result.html', 'w') as f:
        f.write(render_template(form_name, shape))


if __name__ == "__main__":
    # File name passed as command-line argument
    generate_webform(sys.argv[1])
