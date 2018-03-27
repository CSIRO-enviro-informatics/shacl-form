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
PREFIX_RDFS = "http://www.w3.org/2000/01/rdf-schema#"
PREFIX_SHACL = "http://www.w3.org/ns/shacl#"


class RDFHandler:
    def __init__(self, file_name):
        self.g = Graph()
        self.g.parse(file_name, format=guess_format(file_name))

    '''
    The only shapes we are interested in are Node Shapes. They define all the properties and constraints relating
    to a node that we want to create a form for. Property shapes are useful for defining constraints, but are not 
    relevant here
    
    Shapes which match this criteria are subjects of a triple with a predicate of rdf:type and an object of
    sh:NodeShape
    
    Shapes and properties can reference other shapes using the sh:node predicate. Therefore, the root shape is the only
    shape that is not the object of a triple with a predicate of sh:node.
    '''
    def get_root_shape(self):
        shapes = self.g.subjects(URIRef(PREFIX_RDF + "type"), URIRef(PREFIX_SHACL + "NodeShape"))
        for s in shapes:
            if not (None, URIRef(PREFIX_SHACL + "node"), s) in self.g:
                return s

    '''
    Node Shapes have 0-1 target classes. The target class is useful for naming the form.
    Looks for implicit class targets - a shape of type sh:NodeShape and rdfs:Class is a target class of itself.
    '''
    def get_target_class(self, shape_uri):
        if (shape_uri, URIRef(PREFIX_RDF + "type"), URIRef(PREFIX_RDFS + "Class")) in self.g:
            return shape_uri
        return self.g.value(shape_uri, URIRef(PREFIX_SHACL + "targetClass"), None)

    # Get all the properties associated with the Shape. They may be URIs or blank nodes.
    def get_properties(self, shape_uri):
        return self.g.objects(shape_uri, URIRef(PREFIX_SHACL + "property"))

    # Only supports core constraints
    def get_property_constraints(self, property_uri):
        constraints = dict()
        for c in self.g.predicate_objects(property_uri):
            constraints[c[0].split('#')[1]] = c[1]

        # Gets the list of acceptable values for constraint "IN" rather than the blank node representing it
        if "in" in constraints:
            constraints["in"] = list(Collection(self.g, constraints["in"]))
        # If the property doesn't have a name label, fall back to the URI of the path.
        if "name" not in constraints:
            constraints["name"] = constraints["path"].rsplit('/', 1)[1]
        # Get information about the property's group and order
        if "group" not in constraints:
            constraints["group"] = None
        else:
            constraints["group_label"] = self.g.value(constraints["group"], URIRef(PREFIX_RDFS + "label"), None)
            constraints["group_order"] = self.g.value(constraints["group"], URIRef(PREFIX_SHACL + "order", None))
        if "order" not in constraints:
            constraints["order"] = None
        # Validate other input
        if "minCount" in constraints:
            try:
                constraints["minCount"] = int(constraints["minCount"])
            except ValueError:
                raise Exception("MinCount value must be an integer: '{value}'".format(value=constraints["minCount"]))
        if "path" in constraints:
            constraints["path"] = str(constraints["path"])
        return constraints
