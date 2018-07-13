from rdflib import Graph, RDF, XSD
from rdflib.util import guess_format
from rdflib.term import Literal, URIRef, BNode
import uuid
import re


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
        self.root_node_class = self.rdf_map.value(Literal('placeholder node_uri'), URIRef(RDF.type), None)
        entry_uuid = str(uuid.uuid4())
        self.root_node = URIRef(self.base_uri + entry_uuid)
        self.rdf_result.add((self.root_node, RDF.type, self.root_node_class))
        # Go through each property and search for entries submitted in the form
        for (subject, property_predicate, property_obj) in self.rdf_map:
            if str(subject) == 'placeholder node_uri' and not property_predicate == RDF.type:
                self.add_entries_for_property(self.root_node, property_predicate, property_obj)
        # Also get any custom properties submitted in the form
        self.add_custom_property_entries(self.root_node)
        return self.rdf_result

    def add_entries_for_property(self, subject, predicate, obj, root_id=None):
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
            m = re.search('nodeKind=(\w+)', obj)
            if m is None:
                raise ValueError('No nodeKind option provided: ' + obj)
            permitted_node_kind = m.group().split('=')[1]
            node_kind_selection = self.get_node_kind_selection(permitted_node_kind, entry_id)
            if node_kind_selection == 'BlankNode':
                if self.add_blank_node_entry(subject, predicate, obj, entry_id):
                    found_at_least_one_entry = True
                    copy_id += 1
                else:
                    break
            elif node_kind_selection == 'IRI':
                if self.add_iri_entry(subject, predicate, entry_id):
                    found_at_least_one_entry = True
                    copy_id += 1
                else:
                    break
            elif node_kind_selection == 'Literal':
                if self.add_literal_entry(subject, predicate, obj, entry_id):
                    found_at_least_one_entry = True
                    copy_id += 1
                else:
                    break
            else:
                break
        return found_at_least_one_entry

    def get_node_kind_selection(self, permitted_node_kind, entry_id):
        # Selection isn't necessary if the nodeKind is specified as one of these
        if permitted_node_kind in ['Literal', 'IRI', 'BlankNode']:
            return permitted_node_kind
        # The permitted nodeKind should be one of these
        if permitted_node_kind not in ['BlankNodeOrIRI', 'BlankNodeOrLiteral', 'IRIOrLiteral']:
            raise ValueError('Not valid nodeKind option: ' + permitted_node_kind)
        # Get the options that the user can select from
        node_kind_options = permitted_node_kind.split('Or')
        # Get user selection for node kind for this entry
        node_kind_id = 'NodeKind ' + entry_id
        node_kind_selection = self.form_input.get(node_kind_id)
        if not node_kind_selection:
            return None
        # Check the user selected one of the options
        if node_kind_selection not in node_kind_options:
            raise ValueError('Not valid nodeKind selection: ' + node_kind_selection)
        return node_kind_selection

    def add_literal_entry(self, subject, predicate, obj, entry_id):
        entry = self.form_input.get(entry_id)
        m = re.search('datatype=[^ ]*', obj)
        if m is None:
            datatype = None
        else:
            datatype = m.group().split('=')[1]
        if datatype == XSD.boolean:
            # Unchecked checkboxes in a form aren't submitted with the form
            # Form has been altered to submit hidden field with prefix 'Unchecked ' if a checkbox isn't checked
            # Normal entry -> True
            if entry:
                self.rdf_result.add((subject, predicate, Literal(True, datatype=XSD.boolean)))
                return True
            # Entry with prefix 'Unchecked ' -> False
            elif self.form_input.get('Unchecked ' + entry_id):
                self.rdf_result.add((subject, predicate, Literal(False, datatype=XSD.boolean)))
                return True
            # Neither -> No value
            else:
                return False
        elif entry:
            self.rdf_result.add((subject, predicate, Literal(entry, datatype=datatype)))
            return True
        return False

    def add_iri_entry(self, subject, predicate, entry_id):
        entry = self.form_input.get(entry_id)
        if entry:
            self.rdf_result.add((subject, predicate, URIRef(self.validate_iri(entry))))
            return True
        else:
            return False

    def add_blank_node_entry(self, subject, predicate, obj, entry_id):
        node = BNode()
        included_properties = list(self.rdf_map.predicate_objects(obj))
        found_entry = False
        for p in included_properties:
            nested_property_id = entry_id + ':' + p[1].split(':')[-1]
            found_entry_for_property = self.add_entries_for_property(node, p[0], p[1], nested_property_id)
            if found_entry_for_property:
                found_entry = True
        if found_entry:
            self.rdf_result.add((subject, predicate, node))
            return True
        else:
            return False

    def add_custom_property_entries(self, root_node):
        copy_id = 0
        # Cycles through entries by ID until no more entries are found
        while True:
            predicate_id = 'Predicate CustomProperty-' + str(copy_id)
            predicate = self.form_input.get(predicate_id)
            type_selection_id = 'Object Type CustomProperty-' + str(copy_id)
            type_selection = self.form_input.get(type_selection_id)
            obj_id = 'Object CustomProperty-' + str(copy_id)
            obj = self.form_input.get(obj_id)
            if predicate is None or type_selection is None or obj is None:
                break
            predicate = URIRef(self.validate_iri(predicate))
            if type_selection == 'IRI':
                obj = URIRef(self.validate_iri(obj))
            elif type_selection == 'Boolean':
                if obj == 'True' or obj == 'true' or obj == '1':
                    obj = Literal(obj, datatype=XSD.boolean)
            else:
                obj = Literal(obj, datatype=XSD.string)
            self.rdf_result.add((root_node, predicate, obj))
            copy_id += 1

    @staticmethod
    def validate_iri(iri):
        if iri is None:
            return
        # Remove enclosing <>
        if iri.startswith('<'):
            iri = iri.strip('<>')
        # Ensure URI is valid
        for char in '<>" {}|\\^`':
            if char in iri:  # Invalid URI
                raise ValueError('Invalid URI: ' + iri)
        return iri
