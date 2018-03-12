from rdflib.graph import Graph
from rdflib.term import URIRef

"""
Experimental code that reads information from a SHACL Shapes file and prints it.
For each shape, lists:
    Shape URI
    Target class
    Whether the shape is closed
    Properties associated with the shape
    
This needs further work since some of the properties end in blank nodes and need to be
followed up.
"""

PREFIX_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
PREFIX_SHACL = "http://www.w3.org/ns/shacl#"

g = Graph()
g.parse("permitted_shapes.ttl", format="turtle")
#Get the URI of each shape
shapes = g.subjects(URIRef(PREFIX_RDF + "type"), URIRef(PREFIX_SHACL + "NodeShape"))
for s in shapes:
    print("Shape:", s)

    #Get the target class
    target_class_results = g.objects(s, URIRef(PREFIX_SHACL + "targetClass"))
    #The target class is not always specified, I think in this case because AddressShape
    #is a node in PersonShape
    target_class = "unspecified"
    for t in target_class_results:
        target_class = t
    print("Target class:", target_class)

    #Get whether the shape is closed
    closed_results = g.objects(s, URIRef(PREFIX_SHACL + "closed"))
    #This isn't always specified but it defaults to false
    closed = False
    for c in closed_results:
        closed = True if c == "true" else False
    print("Closed:", closed)

    #Get all the properties associated with the Shape. They will be blank nodes.
    properties = g.objects(s, URIRef(PREFIX_SHACL + "property"))
    for p in properties:
        print("Property:", p)

        #Get each entry associated with each property
        #Path is always specified, but the others are optional
        constraint_results = g.predicate_objects(p)
        for c in constraint_results:
            print("     ", c[0], ":", c[1])

    print()
