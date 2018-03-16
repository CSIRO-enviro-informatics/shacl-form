import rdfhandling
import render

RDF_handler = rdfhandling.RDFHandler("permitted_shapes.ttl")

# Get root node shape
node_shape = RDF_handler.get_root_shape()

# Get a name for the form
target_class = RDF_handler.get_target_class(node_shape)
# Cutting off part of the target class URI to find a more human readable name
# Example: http://schema.org/Person -> Person
form_name = target_class.rsplit('/', 1)[1] if target_class else "Entry"

# Get properties and store them in a list
property_uris = list(RDF_handler.get_properties(node_shape))
properties = list()
for p in property_uris:
    property_name = RDF_handler.get_property_name(p)
    property_path = RDF_handler.get_property_path(p)
    property_datatype = RDF_handler.get_property_datatype(p)
    properties.append((property_name, property_path, property_datatype))

# Put things into template
with open('result.html', 'w') as f:
    f.write(render.render_template(form_name, properties))
