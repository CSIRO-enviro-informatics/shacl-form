from rdflib.graph import Graph
from rdflib.term import URIRef
from rdflib.util import guess_format
from rdflib.collection import Collection
from rdflib import RDF, RDFS
import re

"""
Reads information from a SHACL Shapes file.
For each shape, can determine:
    Shape URI
    Target class
    Properties associated with the shape
    
This needs further work since some of the properties end in blank nodes and need to be followed up.
Does not support additional shapes at this time.
"""

SHACL = "http://www.w3.org/ns/shacl#"


class RDFHandler:
    def __init__(self, file_name):
        self.g = Graph()
        self.g.parse(file_name, format=guess_format(file_name))

    def get_shape(self):
        # Will hold the target class, groups, and ungrouped properties
        shape = dict()

        """
        First, get the root shape. The only shapes we are interested in are Node Shapes. They define all the properties
        and constraints relating to a node that we want to create a form for. Property shapes are useful for defining 
        constraints, but are not relevant here

        Shapes which match this criteria are subjects of a triple with a predicate of rdf:type and an object of
        sh:NodeShape

        Shapes and properties can reference other shapes using the sh:node predicate. Therefore, the root shape is the
        only shape that is not the object of a triple with a predicate of sh:node.
        """
        shape_uris = self.g.subjects(URIRef(RDF.uri + "type"), URIRef(SHACL + "NodeShape"))
        root_uri = None
        for s in shape_uris:
            if not (None, URIRef(SHACL + "node"), s) in self.g:
                root_uri = s
        if not root_uri:
            return None

        """
        Get the target class
        Node Shapes have 0-1 target classes. The target class is useful for naming the form.
        Looks for implicit class targets - a shape of type sh:NodeShape and rdfs:Class is a target class of itself.
        """
        if (root_uri, URIRef(RDF.uri + "type"), URIRef(RDFS.uri + "Class")) in self.g:
            return root_uri
        shape["target_class"] = self.g.value(root_uri, URIRef(SHACL + "targetClass"), None)
        if not shape["target_class"]:
            raise Exception("A target class must be specified for shape: " + root_uri)

        """
        Get the groups
        Some properties belong to groups which determine how they are presented in the form.
        """
        shape["groups"] = list()
        group_uris = self.g.subjects(URIRef(RDF.uri + "type"), URIRef(SHACL + "PropertyGroup"))
        for g_uri in group_uris:
            group = dict()
            group["uri"] = g_uri
            group["label"] = self.g.value(g_uri, URIRef(RDFS.uri + "label"), None)
            group["order"] = self.g.value(g_uri, URIRef(SHACL + "order"), None)
            group["properties"] = list()
            shape["groups"].append(group)

        """
        Get all the properties associated with the Shape. They may be URIs or blank nodes.
        Go through each property
        If it belongs to a group, place it in the list of properties associated with the group
        Otherwise, place it in the list of ungrouped properties
        """
        shape["properties"] = list()
        property_uris = self.g.objects(root_uri, URIRef(SHACL + "property"))
        for p_uri in property_uris:
            constraints = dict()
            for c in self.g.predicate_objects(p_uri):
                constraints[c[0].split('#')[1]] = c[1]

            # Gets the list of acceptable values for constraint "IN" rather than the blank node representing it
            if "in" in constraints:
                constraints["in"] = list(Collection(self.g, constraints["in"]))
            # Gets the list of acceptable values for constraint "languageIn" rather than the blank node representing it
            if "languageIn" in constraints:
                constraints["languageIn"] = [str(l) for l in list(Collection(self.g, constraints["languageIn"]))]
            # If the property doesn't have a name label, fall back to the URI of the path.
            if "name" not in constraints:
                constraints["name"] = re.split("#|/", constraints["path"])[-1]
            # There must be an entry for order even if it is unordered
            if "order" not in constraints:
                constraints["order"] = None
            # Convert to string
            if "datatype" in constraints:
                constraints["datatype"] = str(constraints["datatype"])
            # Validate other input
            if "minCount" in constraints:
                try:
                    constraints["minCount"] = int(constraints["minCount"])
                except ValueError:
                    raise Exception(
                        "minCount value must be an integer: '{value}'".format(value=constraints["minCount"]))
            if "path" in constraints:
                constraints["path"] = str(constraints["path"])
            else:
                raise Exception("Every property must have a path associated with it: " + p_uri)
            if "minInclusive" in constraints and "minExclusive" in constraints:
                raise Exception("minInclusive and minExclusive constraints are specified for property: " + p_uri +
                                ". Only one may be used.")
            if "maxInclusive" in constraints and "maxExclusive" in constraints:
                raise Exception("maxInclusive and maxExclusive constraints are specified for property: " + p_uri +
                                ". Only one may be used.")

            # Consolidate inclusive and exclusive terms
            if "minInclusive" in constraints:
                constraints["min"] = float(constraints["minInclusive"])
                del constraints["minInclusive"]
            elif "minExclusive" in constraints:
                constraints["min"] = float(constraints["minExclusive"]) + 1
                del constraints["minExclusive"]
            if "maxInclusive" in constraints:
                constraints["max"] = float(constraints["maxInclusive"])
                del constraints["maxInclusive"]
            elif "maxExclusive" in constraints:
                constraints["max"] = float(constraints["maxExclusive"]) - 1
                del constraints["maxExclusive"]

            # Place the property in the correct place
            group_uri = self.g.value(p_uri, URIRef(SHACL + "group"), None)
            # Belongs to group
            if group_uri:
                # Check if the group referenced actually exists
                existing_group = None
                for g in shape["groups"]:
                    if g["uri"] == group_uri:
                        existing_group = g
                if existing_group:
                    existing_group["properties"].append(constraints)
                else:
                    raise Exception("Property " + p_uri + " references PropertyGroup " + group_uri
                                    + " which does not exist.")
            # Does not belong to a group
            else:
                shape["properties"].append(constraints)

        return shape
