from rdflib.graph import Graph
from rdflib.term import URIRef
from rdflib.util import guess_format
from rdflib.collection import Collection

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

    '''
    The only shapes we are interested in are Node Shapes. They define all the properties and constraints relating
    to a node that we want to create a form for. Property shapes are useful for defining additional constraints,
    but are not relevant here
    
    Shapes which match this criteria are subjects of a triple with a predicate of rdf:type and an object of
    sh:NodeShape
    
    Only supports 1 Node Shape - in the future should be able to determine the hierarchy of multiple Node Shapes
    and find the root
    '''
    def get_root_shape(self):
        shapes = self.g.subjects(URIRef(PREFIX_RDF + "type"), URIRef(PREFIX_SHACL + "NodeShape"))
        for s in shapes:
            return s

    # Node Shapes have 0-1 target classes. The target class is useful for naming the form.
    def get_target_class(self, shape_uri):
        target_class_results = self.g.objects(shape_uri, URIRef(PREFIX_SHACL + "targetClass"))
        for t in target_class_results:
            return t

    # Get all the properties associated with the Shape. They will be blank nodes.
    def get_properties(self, shape_uri):
        return self.g.objects(shape_uri, URIRef(PREFIX_SHACL + "property"))

    # Use the name label if the property has one, otherwise fall back to the URI of the path.
    def get_property_name(self, property_uri):
        names = self.g.objects(property_uri, URIRef(PREFIX_SHACL + "name"))
        for n in names:
            return n
        # Cutting off part of the path URI to find a more human readable name
        path = self.get_property_path(property_uri)
        name = path.rsplit('/', 1)[1]
        return name

    # Properties always have a path.
    def get_property_path(self, property_uri):
        paths = self.g.objects(property_uri, URIRef(PREFIX_SHACL + "path"))
        for p in paths:
            return p

    # Properties have 0-1 datatypes, which is useful for determining input fields in the form.
    def get_property_datatype(self, property_uri):
        datatypes = self.g.objects(property_uri, URIRef(PREFIX_SHACL + "datatype"))
        for d in datatypes:
            return d

    # Description is an optional non-validating property. It is a human-readable description of the property.
    def get_property_desc(self, property_uri):
        descs = self.g.objects(property_uri, URIRef(PREFIX_SHACL + "description"))
        for d in descs:
            return d

    # DefaultValue is an optional non-validating property for form-building.
    def get_property_default_value(self, property_uri):
        defaults = self.g.objects(property_uri, URIRef(PREFIX_SHACL + "defaultValue"))
        for d in defaults:
            return d

    def get_property_in_constraint(self, property_uri):
        collection_uri = self.g.objects(property_uri, URIRef(PREFIX_SHACL + "in"))
        for c_uri in collection_uri:
            return list(Collection(self.g, c_uri))

    def get_property_constraints(self, property_uri):
        # Get each entry associated with each property
        # Path is always specified, but the others are optional
        return self.g.predicate_objects(property_uri)
