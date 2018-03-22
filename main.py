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

# Get ungrouped properties and store them in a list
property_uris = RDF_handler.get_properties(node_shape)
ungrouped_properties = list()
for p in property_uris:
    constraints = RDF_handler.get_property_constraints(p)
    # Skip all properties which belong to a group.
    if "group" in constraints:
        continue
    ungrouped_properties.append(constraints)

# Get groups of properties and store them in a list
# Groups and grouped properties need to be sorted by their Order constraint
group_uris = RDF_handler.get_groups()
groups = list()
for g_uri in group_uris:
    g = dict()
    g["name"] = RDF_handler.get_group_name(g_uri)
    g["order"] = RDF_handler.get_group_order(g_uri)
    property_uris = RDF_handler.get_properties_in_group(g_uri)
    group_properties = list()
    for p in property_uris:
        group_properties.append(RDF_handler.get_property_constraints(p))
    # Sorts the properties by their Order
    group_properties.sort(key=lambda x: x["order"])
    g["properties"] = group_properties
    groups.append(g)
# Sorts the groups by their Order
groups.sort(key=lambda x: x["order"])

# Put things into template
with open('result.html', 'w') as f:
    f.write(render.render_template(form_name, groups, ungrouped_properties))
