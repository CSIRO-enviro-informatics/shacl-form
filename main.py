import rdfhandling
import render

RDF_handler = rdfhandling.RDFHandler("permitted_shapes.ttl")

# Get shape
shapes = list(RDF_handler.get_shape_uris())
if len(shapes) == 0:
    raise Exception("No shapes specified.")

# Get target class
target_class_uri = RDF_handler.get_target_class(shapes[0])
# Cutting off part of the target class URI to find a more human readable name
if target_class_uri:
    target_class = target_class_uri.rsplit('/', 1)[1]
else:
    raise Exception("No target class specified.")

# Get property names and store them in a list
property_uris = list(RDF_handler.get_properties(shapes[0]))
properties = list()
for p in property_uris:
    property_name = RDF_handler.get_property_name(p)
    # Cutting off part of the property name to find a more human readable name
    property_name = property_name.rsplit('/', 1)[1]
    properties.append(property_name)

# Print some info for reference
print("Shape:", shapes[0])
print("Target class:", target_class_uri)
print("Closed:", RDF_handler.is_closed(shapes[0]))
for p in property_uris:
    print("Property:", p)
    for c in RDF_handler.get_property_constraints(p):
        print("     ", c[0], ":", c[1])
print()

# Put things into template
with open('result.html', 'w') as f:
    f.write(render.render_template(target_class, properties))
