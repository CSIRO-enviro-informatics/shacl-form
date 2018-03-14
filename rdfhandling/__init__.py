from rdflib.graph import Graph
from rdflib.term import URIRef
from rdflib.util import guess_format

"""
Reads information from a SHACL Shapes file.
For each shape, lists:
    Shape URI
    Target class
    Whether the shape is closed
    Properties associated with the shape
    
This needs further work since some of the properties end in blank nodes and need to be followed up.
"""

PREFIX_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
PREFIX_SHACL = "http://www.w3.org/ns/shacl#"


class RDFHandler:
    def __init__(self, file_name):
        self.g = Graph()
        self.g.parse(file_name, format=guess_format(file_name))

    def get_shape_uris(self):
        return self.g.subjects(URIRef(PREFIX_RDF + "type"), URIRef(PREFIX_SHACL + "NodeShape"))

    def get_target_class(self, shape_uri):
        # Get the target class
        target_class_results = self.g.objects(shape_uri, URIRef(PREFIX_SHACL + "targetClass"))
        # The target class is not always specified, I think in this case because AddressShape
        # is a node in PersonShape
        target_class = "unspecified"
        for t in target_class_results:
            target_class = t
        return target_class

    def is_closed(self, shape_uri):
        # Get whether the shape is closed
        closed_results = self.g.objects(shape_uri, URIRef(PREFIX_SHACL + "closed"))
        # This isn't always specified but it defaults to false
        closed = False
        for c in closed_results:
            closed = True if str(c) == "true" else False
        return closed

    def get_properties(self, shape_uri):
        # Get all the properties associated with the Shape. They will be blank nodes.
        return self.g.objects(shape_uri, URIRef(PREFIX_SHACL + "property"))

    def get_property_constraints(self, property_uri):
        # Get each entry associated with each property
        # Path is always specified, but the others are optional
        return self.g.predicate_objects(property_uri)
