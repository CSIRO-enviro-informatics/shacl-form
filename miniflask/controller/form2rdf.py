from rdflib import Graph, RDF, XSD
from rdflib.util import guess_format
from rdflib.term import Literal, URIRef, BNode
import uuid


class Form2RDFController:
    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.form_input = None
        self.rdf_map = None
        self.rdf_result = None
        self.root_node = None
        self.root_node_class = None

    def convert(self, form_input, map_filename):
        self.form_input = form_input.form
        # Get map and result RDF graphs ready
        self.rdf_map = Graph()
        self.rdf_map.parse(map_filename, format=guess_format(map_filename))
        self.rdf_result = Graph()
        self.rdf_result.namespace_manager = self.rdf_map.namespace_manager
        # Get unique URI of the new node
        root_node_class = self.rdf_map.value(Literal('Placeholder node_uri'), URIRef(RDF.type), None)
        entry_uuid = str(uuid.uuid4())
        self.root_node = URIRef(self.base_uri + entry_uuid)
        self.rdf_result.add((self.root_node, RDF.type, root_node_class))
        # Go through each property and search for entries submitted in the form
        for (subject, property_predicate, property_obj) in self.rdf_map:
            if str(subject) == 'Placeholder node_uri' and not property_predicate == RDF.type:
                self.find_entries_for_property(self.root_node, property_predicate, property_obj)
        return self.rdf_result

    def find_entries_for_property(self, subject, predicate, obj, root_id=None):
        """
        :param subject: The subject this property will be attached to. It will be the root node unless this is a nested
                        property
        :param predicate: The predicate of the property
        :param obj: The object of the property. Can be a literal/IRI or a blank node leading to nested properties
        :param root_id: Provides a starting point for building nested property IDs used to get an entry in the form
        :return:
        """
        if not root_id:
            root_id = obj.split(' ')[-1]
        copy_id = 0
        found_at_least_one_entry = False
        # Cycles through entries by ID until no more entries are found
        while True:
            # Every entry for this property shares a root_id, and has a different copy_id
            entry_id = root_id + '-' + str(copy_id)
            # Get user selection for node kind for this entry
            node_kind_id = 'NodeKind ' + entry_id
            node_kind_selection = self.form_input.get(node_kind_id)
            if node_kind_selection:
                if node_kind_selection in obj:
                    # Node kind selection is valid, add the entry according to the selection
                    if node_kind_selection == 'BlankNode':
                        if self.insert_blanknode_entry(subject, predicate, obj, entry_id):
                            found_at_least_one_entry = True
                            copy_id += 1
                        else:
                            break
                    elif node_kind_selection == 'IRI':
                        if self.insert_iri_entry(subject, predicate, entry_id):
                            found_at_least_one_entry = True
                            copy_id += 1
                        else:
                            break
                    elif node_kind_selection == 'Literal':
                        if self.insert_literal_entry(subject, predicate, obj, entry_id):
                            found_at_least_one_entry = True
                            copy_id += 1
                        else:
                            break
                    else:
                        # User entered an invalid node kind
                        raise ValueError('Not valid nodeKind: ' + node_kind_selection)
                else:
                    # User selected a node kind that is not permitted for this property
                    raise ValueError('Not valid nodeKind: ' + node_kind_selection)
            else:
                # User didn't enter a node kind
                if any(x in obj for x in ['BlankNodeOrIRI ', 'BlankNodeOrLiteral ', 'IRIOrLiteral ']):
                    break
                # User does not need to make a choice
                elif 'BlankNode ' in obj:
                    if self.insert_blanknode_entry(subject, predicate, obj, entry_id):
                        found_at_least_one_entry = True
                        copy_id += 1
                    else:
                        break
                elif 'IRI ' in obj:
                    if self.insert_iri_entry(subject, predicate, entry_id):
                        found_at_least_one_entry = True
                        copy_id += 1
                    else:
                        break
                elif 'Literal ' in obj:
                    if self.insert_literal_entry(subject, predicate, obj, entry_id):
                        found_at_least_one_entry = True
                        copy_id += 1
                    else:
                        break
        return found_at_least_one_entry

    def insert_literal_entry(self, subject, predicate, obj, entry_id):
        entry = self.form_input.get(entry_id)
        # Datatype of boolean can't be specified the usual way (i.e. "Placeholder:1"^^xsd:boolean)
        # Boolean properties have prefix of 'Boolean ' (i.e. "Boolean Placeholder 1")
        if 'Boolean ' in obj:
            # Unchecked checkboxes in a form aren't submitted with the form
            # Form has been altered to submit hidden field with prefix 'unchecked:' if a checkbox isn't checked
            # Normal entry -> True
            if entry:
                self.rdf_result.add((subject, predicate, Literal(True, datatype=XSD.boolean)))
                return True
            # Entry with prefix 'unchecked' -> False
            elif self.form_input.get('Unchecked ' + entry_id):
                self.rdf_result.add((subject, predicate, Literal(False, datatype=XSD.boolean)))
                return True
            # Neither -> No value
            else:
                return False
        elif entry:
            self.rdf_result.add((subject, predicate, Literal(entry, datatype=obj.datatype)))
            return True
        return False

    def insert_iri_entry(self, subject, predicate, entry_id):
        entry = self.form_input.get(entry_id)
        if entry:
            # Remove enclosing <>
            if entry.startswith('<'):
                entry = entry.strip('<>')
            # Ensure URI is valid
            for char in '<>" {}|\\^`':
                if char in entry:  # Invalid URI
                    raise ValueError('Invalid URI: ' + entry)
            self.rdf_result.add((subject, predicate, URIRef(entry)))
            return True
        else:
            return False

    def insert_blanknode_entry(self, subject, predicate, obj, entry_id):
        node = BNode()
        included_properties = list(self.rdf_map.predicate_objects(obj))
        found_entry = False
        for p in included_properties:
            nested_property_id = entry_id + ':' + p[1].split(':')[-1]
            found_entry_for_property = self.find_entries_for_property(node, p[0], p[1], nested_property_id)
            if found_entry_for_property:
                found_entry = True
        if found_entry:
            self.rdf_result.add((subject, predicate, node))
            return True
        else:
            return False
