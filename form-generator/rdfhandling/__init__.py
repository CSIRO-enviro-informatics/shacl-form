from rdflib.graph import Graph
from rdflib.term import URIRef, Literal
from rdflib.util import guess_format
from rdflib.collection import Collection
from rdflib.namespace import RDF, RDFS, XSD
from warnings import warn
import re

SHACL = 'http://www.w3.org/ns/shacl#'


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
        shape_uris = list(self.g.subjects(URIRef(RDF.uri + 'type'), URIRef(SHACL + 'NodeShape')))
        root_uri = None
        if not shape_uris:
            return None
        for s in shape_uris:
            if (None, URIRef(SHACL + 'node'), s) not in self.g:
                root_uri = s
                break
        if not root_uri:
            raise Exception('Recursion not allowed.')

        """
        Add any nodes which may be attached to this root shape.
        Does this by grabbing everything in that node and adding it to the root shape.
        Nodes inside properties are handled in get_property
        """
        nodes = self.g.objects(root_uri, URIRef(SHACL + 'node'))
        for n in nodes:
            for (p, o) in self.g.predicate_objects(n):
                self.add_node(root_uri, p, o)

        """
        Get the target class
        Node Shapes have 0-1 target classes. The target class is useful for naming the form.
        Looks for implicit class targets - a shape of type sh:NodeShape and rdfs:Class is a target class of itself.
        """
        if (root_uri, URIRef(RDF.uri + 'type'), URIRef(RDFS.uri + 'Class')) in self.g:
            shape['target_class'] = root_uri
        else:
            shape['target_class'] = self.g.value(root_uri, URIRef(SHACL + 'targetClass'), None)
        if not shape['target_class']:
            raise Exception('A target class must be specified for shape: ' + root_uri)

        """
        Get the closed status
        Shapes which are open allow the presence of properties not explicitly defined in the shape
        Shapes which are closed will only allow explicitly defined properties
        """
        is_closed = self.g.value(root_uri, URIRef(SHACL + 'closed'), None)
        if is_closed is None:
            shape['closed'] = False
        else:
            shape['closed'] = is_closed.toPython()

        """
        If the shape is closed, get the ignored properties. These properties will be allowed despite the shape
        being closed and not being defined in their own property shape.
        """
        if 'closed' in shape and shape['closed'] is True:
            shape['ignoredProperties'] = [str(l) for l in list(
                Collection(self.g, self.g.value(root_uri, URIRef(SHACL + 'ignoredProperties')))
            )]

        """
        Get the groups
        Some properties belong to groups which determine how they are presented in the form.
        """
        shape['groups'] = list()
        group_uris = self.g.subjects(URIRef(RDF.uri + 'type'), URIRef(SHACL + 'PropertyGroup'))
        for g_uri in group_uris:
            group = dict()
            group['uri'] = g_uri
            group['label'] = self.g.value(g_uri, URIRef(RDFS.uri + 'label'), None)
            group['order'] = self.g.value(g_uri, URIRef(SHACL + 'order'), None)
            group['properties'] = list()
            shape['groups'].append(group)

        """
        Get all the properties associated with the Shape. They may be URIs or blank nodes. Additional shapes may be
        linked as a node.
        If it belongs to a group, place it in the list of properties associated with the group
        Otherwise, place it in the list of ungrouped properties
        """
        shape['properties'] = list()
        property_uris = list(self.g.objects(root_uri, URIRef(SHACL + 'property')))
        for p_uri in property_uris:
            prop = self.get_property(p_uri)
            # Place the property in the correct place
            group_uri = self.g.value(p_uri, URIRef(SHACL + 'group'), None)
            # Belongs to group
            if group_uri:
                # Check if the group referenced actually exists
                existing_group = None
                for g in shape['groups']:
                    if g['uri'] == group_uri:
                        existing_group = g
                if existing_group:
                    existing_group['properties'].append(prop)
                else:
                    raise Exception('Property ' + p_uri + ' references PropertyGroup ' + group_uri
                                    + ' which does not exist.')
            # Does not belong to a group
            else:
                shape['properties'].append(prop)
        return shape

    def get_property(self, uri, path_required=True):
        prop = dict()
        c_uris = list(self.g.predicate_objects(uri))

        # Link nodes
        for c_uri in tuple(c_uris):
            if re.split('[#/]', c_uri[0])[-1] == 'node':
                c_uris.extend(self.g.predicate_objects(c_uri[1]))

        # Go through each constraint and convert/validate them as necessary
        for c_uri in c_uris:
            name = re.split('[#/]', c_uri[0])[-1]
            value = c_uri[1]

            # Get list of values from constraints that supply a list
            if name in ['in', 'languageIn']:
                value = [str(l) for l in list(Collection(self.g, value))]
            # Convert constraints which must be given as an int
            elif name in ['minCount', 'maxCount']:
                try:
                    value = int(value)
                except ValueError:
                    raise Exception(
                        name + ' value must be an integer: "{value}"'.format(value=value))
            # Convert constraints which must be converted from an rdf literal
            elif name in ['hasValue', 'defaultValue']:
                value = value.toPython()
            # Some properties are made up of other properties
            # Handle this with recursion
            elif name == 'property':
                if 'property' in prop:
                    properties = prop['property']
                    properties.append(self.get_property(value))
                    value = properties
                else:
                    value = [self.get_property(value)]
            # Consolidate constraints which may be supplied in different ways
            # minInclusive and minExclusive can be simplified down to one attribute
            elif name in ['minInclusive', 'minExclusive', 'maxInclusive', 'maxExclusive']:
                if name == 'minInclusive':
                    name = 'min'
                    value = float(value)
                elif name == 'minExclusive':
                    name = 'min'
                    value = float(value) + 1
                if name == 'maxInclusive':
                    name = 'max'
                    value = float(value)
                elif name == 'maxExclusive':
                    name = 'max'
                    value = float(value) - 1
            # All other constraints should be converted to strings
            else:
                value = str(value)

            prop[name] = value

        # Validate property as a whole
        # Property must have one and only one path
        if 'path' in prop:
            prop['path'] = prop['path']
        elif path_required:
            raise Exception('Every property must have a path associated with it: ' + uri)

        # Must have a name
        # If the property doesn't have a name label, fall back to the URI of the path.
        if 'name' not in prop and 'path' in prop:
            prop['name'] = re.split('[#/]', prop['path'])[-1]

        # There must be an entry for order even if it is unordered
        if 'order' not in prop:
            prop['order'] = None

        # If sh:nodeKind is not present, an appropriate option will be guessed
        # If nested properties are present -> sh:BlankNodeOrIRI
        # Otherwise -> sh:IRIOrLiteral
        warning = None
        if 'nodeKind' not in prop:
            if 'hasValue' in prop:
                prop['nodeKind'] = SHACL + 'Literal'
            else:
                prop['nodeKind'] = SHACL + 'BlankNodeOrIRI' if 'property' in prop else SHACL + 'IRIOrLiteral'
        elif prop['nodeKind'] not in [SHACL + 'BlankNode', SHACL + 'IRI', SHACL + 'Literal',
                                      SHACL + 'BlankNodeOrIRI', SHACL + 'BlankNodeOrLiteral',
                                      SHACL + 'IRIOrLiteral']:
            if 'hasValue' in prop:
                default_value = SHACL + 'Literal'
            else:
                default_value = SHACL + 'BlankNodeOrIRI' if 'property' in prop else SHACL + 'IRIOrLiteral'
            warning = 'Property "' + prop['name'] + '" has constraint "sh:nodeKind" with invalid value "' + \
                      prop['nodeKind'] + '". Replacing with "' + default_value + '".'
            prop['nodeKind'] = default_value
        # Make sure there is enough information provided to accommodate the selected option
        else:
            # If sh:hasValue is present, the user won't be able to choose between nodeKinds, therefore sh:nodeKind can't
            # be BlankNodeOrIRI, IRIOrLiteral, or BlankNodeOrLiteral
            if 'hasValue' in prop and prop['nodeKind'] in [SHACL + 'BlankNodeOrIRI', SHACL + 'IRIOrLiteral',
                                                           SHACL + 'BlankNodeOrLiteral']:
                if prop['nodeKind'] == SHACL + 'BlankNodeOrIRI':
                    new_node_kind = SHACL + 'IRI'
                elif prop['nodeKind'] == SHACL + 'IRIOrLiteral':
                    new_node_kind = SHACL + 'Literal'
                elif prop['nodeKind'] == SHACL + 'BlankNodeOrLiteral':
                    new_node_kind = SHACL + 'Literal'
                warning = 'Property "' + prop['name'] + '" has constraint "sh:nodeKind" with value "' + \
                          prop['nodeKind'] + '" which is incompatible with constraint sh:hasValue. Replacing ' \
                                             'with "' + new_node_kind + '".'
                prop['nodeKind'] = new_node_kind
            # If sh:BlankNode is selected, nested properties should be provided.
            if prop['nodeKind'] == SHACL + 'BlankNode' and 'property' not in prop:
                warning = 'Property "' + prop['name'] + '" has constraint "sh:nodeKind" with value "sh:BlankNode" but' \
                          ' no property shapes are provided. This property will have no input fields.'
            # If sh:BlankNodeOrIRI or sh:BlankNodeOrLiteral are selected, nested properties should be provided for the
            # blank node option
            elif prop['nodeKind'] in [SHACL + 'BlankNodeOrIRI', SHACL + 'BlankNodeOrLiteral'] \
                    and 'property' not in prop:
                warning = 'Property "' + prop['name'] + '" has constraint "sh:nodeKind" with value "' + \
                          prop['nodeKind'] + '" but no property shapes are provided. If the user selects the ' \
                          '"blank node" option, this property will have no input fields.'
            # If sh:IRI, sh:Literal, or sh:IRIOrLiteral are selected, nested properties will be ignored.
            elif prop['nodeKind'] in [SHACL + 'Literal', SHACL + 'IRI', SHACL + 'IRIOrLiteral'] and 'property' in prop:
                warning = 'Property "' + prop['name'] + '" has constraint "sh:nodeKind" with value "' + \
                          prop['nodeKind'] + '". The property shapes provided in this property will be ignored.'
        if warning:
            warn(warning)
        return prop

    def add_node(self, root_uri, predicate, obj):
        # Adds the contents of the node to the root shape
        # If the node contains a link to another node, use recursion to add nodes at all depths
        if str(predicate) == SHACL + 'node':
            for (p, o) in self.g.predicate_objects(obj):
                self.add_node(root_uri, p, o)
        self.g.add((root_uri, predicate, obj))

    def create_rdf_map(self, shape, destination):
        g = Graph()
        g.namespace_manager = self.g.namespace_manager
        g.bind('sh', SHACL)
        # Create the node associated with all the data entered
        g.add((Literal('Placeholder node_uri'), RDF.type, shape['target_class']))
        # Go through each property and add it
        for group in shape['groups']:
            for prop in group['properties']:
                self.add_property_to_map(g, prop, Literal('Placeholder node_uri'))
        for prop in shape['properties']:
            self.add_property_to_map(g, prop, Literal('Placeholder node_uri'))
        g.serialize(destination=destination, format='turtle')

    def add_property_to_map(self, graph, prop, root):
        # Recursive
        placeholder = re.split('[#/]', prop['nodeKind'])[-1] + ' Placeholder ' + str(prop['id'])
        datatype = None
        if 'datatype' in prop:
            if prop['datatype'] == str(XSD.boolean):
                placeholder = 'Boolean ' + placeholder
            else:
                datatype = prop['datatype']
        graph.add((root, URIRef(prop['path']), Literal(placeholder, datatype=datatype)))
        if 'property' in prop:
            for p in prop['property']:
                self.add_property_to_map(graph, p, Literal(placeholder, datatype=datatype))
