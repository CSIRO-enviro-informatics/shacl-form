import rdfhandling

RDF_handler = rdfhandling.RDFHandler("permitted_shapes.ttl")
shapes = RDF_handler.get_shape_uris()
for s in shapes:
    print("Shape:", s)
    print("Target class:", RDF_handler.get_target_class(s))
    print("Closed:", RDF_handler.is_closed(s))
    for p in RDF_handler.get_properties(s):
        print("Property:", p)
        for c in RDF_handler.get_property_constraints(p):
            print("     ", c[0], ":", c[1])
    print()
