from rdflib.graph import Graph
from rdflib.term import URIRef
from rdflib.util import guess_format
from rdflib.collection import Collection
from rdflib import RDF, RDFS, OWL

"""
Reads information from a SHACL Shapes file.
For each shape, can determine:
    Shape URI
    Target class
    Properties associated with the shape
    
This needs further work since some of the properties end in blank nodes and need to be followed up.
"""

SHACL = "http://www.w3.org/ns/shacl#"


class RDFHandler:
    def __init__(self, file_name):
        self.g = Graph()
        self.g.parse(file_name, format=guess_format(file_name))

    def get_root_shape(self):
        """
        The only shapes we are interested in are Node Shapes. They define all the properties and constraints relating
        to a node that we want to create a form for. Property shapes are useful for defining constraints, but are not
        relevant here

        Shapes which match this criteria are subjects of a triple with a predicate of rdf:type and an object of
        sh:NodeShape

        Shapes and properties can reference other shapes using the sh:node predicate. Therefore, the root shape is the
        only shape that is not the object of a triple with a predicate of sh:node.
        """
        shapes = self.g.subjects(URIRef(RDF + "type"), URIRef(SHACL + "NodeShape"))
        for s in shapes:
            if not (None, URIRef(SHACL + "node"), s) in self.g:
                return s

    def get_target_class(self, shape_uri):
        """
        Node Shapes have 0-1 target classes. The target class is useful for naming the form.
        Looks for implicit class targets - a shape of type sh:NodeShape and rdfs:Class is a target class of itself.
        """
        if (shape_uri, URIRef(RDF + "type"), URIRef(RDFS + "Class")) in self.g:
            return shape_uri
        return self.g.value(shape_uri, URIRef(SHACL + "targetClass"), None)

    def get_properties(self, shape_uri):
        """
        Get all the properties associated with the Shape. They may be URIs or blank nodes.
        """
        return self.g.objects(shape_uri, URIRef(SHACL + "property"))

    def get_property_constraints(self, property_uri):
        """
        Only supports core constraints
        """
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
            constraints["group_label"] = self.g.value(constraints["group"], URIRef(RDFS + "label"), None)
            constraints["group_order"] = self.g.value(constraints["group"], URIRef(SHACL + "order", None))
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
