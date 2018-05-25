from rdflib.graph import Graph
from rdflib.term import URIRef, Literal, BNode
from rdflib.util import guess_format
from rdflib.collection import Collection
from rdflib.namespace import RDF, RDFS
import re

SHACL = "http://www.w3.org/ns/shacl#"


class RDFHandler:
    """
    Reads information from a SHACL Shapes file.
    For each shape, can determine:
        Shape URI
        Target class
        Properties associated with the shape
    """
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
        shape_uris = list(self.g.subjects(URIRef(RDF.uri + "type"), URIRef(SHACL + "NodeShape")))
        root_uri = None
        if not shape_uris:
            return None
        for s in shape_uris:
            if (None, URIRef(SHACL + "node"), s) not in self.g:
                root_uri = s
                break
        if not root_uri:
            raise Exception('Recursion not allowed.')

        """
        Add any nodes which may be attached to this root shape.
        Does this by grabbing everything in that node and adding it to the root shape.
        Nodes inside properties are handled in get_property
        """
        nodes = self.g.objects(root_uri, URIRef(SHACL + "node"))
        for n in nodes:
            for (p, o) in self.g.predicate_objects(n):
                self.add_node(root_uri, p, o)

        """
        Get the target class
        Node Shapes have 0-1 target classes. The target class is useful for naming the form.
        Looks for implicit class targets - a shape of type sh:NodeShape and rdfs:Class is a target class of itself.
        """
        if (root_uri, URIRef(RDF.uri + "type"), URIRef(RDFS.uri + "Class")) in self.g:
            shape["target_class"] = root_uri
        else:
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
        Get all the properties associated with the Shape. They may be URIs or blank nodes. Additional shapes may be 
        linked as a node.
        If it belongs to a group, place it in the list of properties associated with the group
        Otherwise, place it in the list of ungrouped properties
        """
        shape["properties"] = list()
        property_uris = list(self.g.objects(root_uri, URIRef(SHACL + "property")))
        for p_uri in property_uris:
            property = self.get_property(p_uri)
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
                    existing_group["properties"].append(property)
                else:
                    raise Exception("Property " + p_uri + " references PropertyGroup " + group_uri
                                    + " which does not exist.")
            # Does not belong to a group
            else:
                shape["properties"].append(property)
        return shape

    def get_property(self, uri, path_required=True):
        property = dict()
        c_uris = list(self.g.predicate_objects(uri))

        # Link nodes
        for c_uri in tuple(c_uris):
            if re.split("#|/", c_uri[0])[-1] == "node":
                c_uris.extend(self.g.predicate_objects(c_uri[1]))

        # Go through each constraint and convert/validate them as necessary
        for c_uri in c_uris:
            name = re.split("#|/", c_uri[0])[-1]
            value = c_uri[1]

            # Gets acceptable values for constraints which supply a list
            if name in ["in", "languageIn"]:
                value = [str(l) for l in list(Collection(self.g, value))]

            # Convert constraints which must be given as an int
            if name in ["minCount", "maxCount"]:
                try:
                    value = int(value)
                except ValueError:
                    raise Exception(
                        name + " value must be an integer: '{value}'".format(value=value))

            # Convert constraints which must be given in string format
            if name in ["datatype", "path"]:
                value = str(value)

            # Convert constraints which must be converted from an rdf literal
            if name in ["hasValue", "defaultValue"]:
                value = value.toPython()

            # Consolidate constraints which may be supplied in different ways
            # minInclusive and minExclusive can be simplified down to one attribute
            if name == "minInclusive":
                name = "min"
                value = float(value)
            elif name == "minExclusive":
                name = "min"
                value = float(value) + 1
            if name == "maxInclusive":
                name = "max"
                value = float(value)
            elif name == "maxExclusive":
                name = "max"
                value = float(value) - 1

            # Some properties are made up of other properties
            # Handle this with recursion
            if name == "property":
                if "property" in property:
                    properties = property["property"]
                    properties.append(self.get_property(value))
                    value = properties
                else:
                    value = [self.get_property(value)]

            property[name] = value

        # Validate property as a whole
        # Property must have one and only one path
        if "path" in property:
            property["path"] = str(property["path"])
        elif path_required:
            raise Exception("Every property must have a path associated with it: " + uri)

        # Must have a name
        # If the property doesn't have a name label, fall back to the URI of the path.
        if "name" not in property and "path" in property:
            property["name"] = re.split("#|/", property["path"])[-1]

        # There must be an entry for order even if it is unordered
        if "order" not in property:
            property["order"] = None

        return property

    def add_node(self, root_uri, predicate, object):
        # Adds the contents of the node to the root shape
        # If the node contains a link to another node, use recursion to add nodes at all depths
        print(predicate, object)
        if str(predicate) == SHACL + "node":
            for (p, o) in self.g.predicate_objects(object):
                self.add_node(root_uri, p, o)
        self.g.add((root_uri, predicate, object))

    def create_rdf_map(self, shape, destination):
        g = Graph()
        g.namespace_manager = self.g.namespace_manager
        g.bind('sh', SHACL)
        # Create the node associated with all the data entered
        g.add((Literal('placeholder:node_uri'), RDF.type, shape['target_class']))
        # Go through each property and add it
        for group in shape["groups"]:
            for property in group["properties"]:
                self.add_property_to_map(g, property, Literal('placeholder:node_uri'))
        for property in shape["properties"]:
            self.add_property_to_map(g, property, Literal('placeholder:node_uri'))
        g.serialize(destination=destination+'map.ttl', format='turtle')

    def add_property_to_map(self, graph, property, root):
        # Create a template for the property
        # Recursion may be required
        if 'property' in property:
            node = BNode()
            graph.add((root, URIRef(property['path']), node))
            for p in property['property']:
                self.add_property_to_map(graph, p, node)
        else:
            graph.add((root, URIRef(property['path']), Literal('placeholder:' + str(property['id']))))
