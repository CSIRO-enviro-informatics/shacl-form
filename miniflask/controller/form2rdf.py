from rdflib import Graph, RDF, XSD
from rdflib.util import guess_format
from rdflib.term import Literal, URIRef, BNode
import uuid

BASE_URI = 'http://example.org/ex#'


def form_to_rdf(request, map_filename):
    # Get map and result RDF graphs ready
    rdf_map = Graph()
    result = Graph()
    result.namespace_manager = rdf_map.namespace_manager
    rdf_map.parse(map_filename, format=guess_format(map_filename))
    # Get unique URI of the new node
    # To do: Other URI options
    node_class = rdf_map.value(Literal('Placeholder node_uri'), URIRef(RDF.type), None)
    entry_uuid = str(uuid.uuid4())
    node_uri = URIRef(BASE_URI + entry_uuid)
    result.add((node_uri, RDF.type, node_class))
    for (subject, predicate, o) in rdf_map:
        if str(subject) == 'Placeholder node_uri' and not predicate == RDF.type:
            insert_entries(request, rdf_map, result, node_uri, predicate, o)
    return node_uri, node_class, result


def insert_entries(request, rdf_map, result, node_uri, predicate, obj, root_id=None):
    """
    :param request: Data collected from the form
    :param rdf_map: The RDF file that describes how the data from the form will fit into the RDF entry.
    :param result: The RDF file that will hold the new entry
    :param node_uri: The node that the property will attach to (the subject)
    :param predicate: The predicate of the property
    :param obj: The object of the property, either a literal or a blank node pointing to more properties
    :param root_id: Used for property recursion, provides a starting point for IDs to iterate through
    :return:
    """
    if not root_id:
        root_id = obj.split(' ')[-1]
    copy_id = 0
    found_at_least_one_entry = False
    # The nodekind type given in the placeholder string determines how this should be handled
    if 'BlankNodeOrIRI ' in obj:
        while True:
            # Figure out if user selected Blank Node or IRI for this entry
            node_kind_id = 'NodeKind ' + root_id + '-' + str(copy_id)
            node_kind_selection = request.form.get(node_kind_id)
            if not node_kind_selection:
                break
            if node_kind_selection == 'BlankNode':
                found_entry, copy_id = insert_blanknode_entry(request, rdf_map, result, node_uri, predicate, obj,
                                                              root_id, copy_id)
                if found_entry:
                    found_at_least_one_entry = True
                else:
                    break
            elif node_kind_selection == 'IRI':
                found_entry, copy_id = insert_iri_entry(request, result, node_uri, root_id, predicate, copy_id)
                if found_entry:
                    found_at_least_one_entry = True
                else:
                    break
            else:
                raise('Not valid nodeKind: ' + node_kind_selection)
    elif 'BlankNodeOrLiteral ' in obj:
        while True:
            # Figure out if the user selected Blank Node or Literal for this entry
            node_kind_id = 'NodeKind ' + root_id + '-' + str(copy_id)
            node_kind_selection = request.form.get(node_kind_id)
            if not node_kind_selection:
                break
            if node_kind_selection == 'BlankNode':
                found_entry, copy_id = insert_blanknode_entry(request, rdf_map, result, node_uri, predicate, obj,
                                                              root_id, copy_id)
                if found_entry:
                    found_at_least_one_entry = True
                else:
                    break
            elif node_kind_selection == 'Literal':
                found_entry, copy_id = insert_literal_entry(request, result, node_uri, root_id, predicate, obj, copy_id)
                if found_entry:
                    found_at_least_one_entry = True
                else:
                    break
            else:
                raise('Not valid nodeKind: ' + node_kind_selection)
    elif 'IRIOrLiteral ' in obj:
        while True:
            # Figure out if the user selected IRI or Literal for this entry
            node_kind_id = 'NodeKind ' + root_id + '-' + str(copy_id)
            node_kind_selection = request.form.get(node_kind_id)
            if not node_kind_selection:
                break
            if node_kind_selection == 'IRI':
                found_entry, copy_id = insert_iri_entry(request, result, node_uri, root_id, predicate, copy_id)
                if found_entry:
                    found_at_least_one_entry = True
                else:
                    break
            elif node_kind_selection == 'Literal':
                found_entry, copy_id = insert_literal_entry(request, result, node_uri, root_id, predicate, obj, copy_id)
                if found_entry:
                    found_at_least_one_entry = True
                else:
                    break
            else:
                raise('Not valid nodeKind: ' + node_kind_selection)
    elif 'Literal ' in obj:
        while True:
            found_entry, copy_id = insert_literal_entry(request, result, node_uri, root_id, predicate, obj, copy_id)
            if found_entry:
                found_at_least_one_entry = True
            else:
                break
    elif 'IRI ' in obj:
        while True:
            found_entry, copy_id = insert_iri_entry(request, result, node_uri, root_id, predicate, copy_id)
            if found_entry:
                found_at_least_one_entry = True
            else:
                break
    elif 'BlankNode ' in obj:
        while True:
            found_entry, copy_id = insert_blanknode_entry(request, rdf_map, result, node_uri, predicate, obj, root_id,
                                                          copy_id)
            if found_entry:
                found_at_least_one_entry = True
            else:
                break
    else:
        raise('Invalid nodeKind.')
    return found_at_least_one_entry


def insert_literal_entry(request, result, node_uri, root_id, predicate, o, copy_id):
    full_id = root_id + '-' + str(copy_id)
    entry = request.form.get(full_id)
    # Datatype of boolean can't be specified the usual way (i.e. "Placeholder:1"^^xsd:boolean)
    # Boolean properties have prefix of 'Boolean ' (i.e. "Boolean Placeholder 1")
    if 'Boolean ' in o:
        # Unchecked checkboxes in a form aren't submitted with the form
        # Form has been altered to submit hidden field with prefix 'unchecked:' if a checkbox isn't checked
        # Normal entry -> True
        if entry:
            result.add((node_uri, predicate, Literal(True, datatype=XSD.boolean)))
            copy_id += 1
            return True, copy_id
        # Entry with prefix 'unchecked' -> False
        elif request.form.get('Unchecked ' + full_id):
            result.add((node_uri, predicate, Literal(False, datatype=XSD.boolean)))
            copy_id += 1
            return True, copy_id
        # Neither -> No value
        else:
            return False, copy_id
    elif entry:
        result.add((node_uri, predicate, Literal(entry, datatype=o.datatype)))
        copy_id += 1
        return True, copy_id
    return False, copy_id


def insert_iri_entry(request, result, node_uri, root_id, predicate, copy_id):
    full_id = root_id + '-' + str(copy_id)
    entry = request.form.get(full_id)
    if entry:
        # Remove enclosing <>
        if entry.startswith("<"):
            entry = entry.strip("<>")
        # Ensure URI is valid
        for char in '<>" {}|\\^`':
            if char in entry:  # Invalid URI
                raise ValueError('Invalid URI: ' + entry)
        result.add((node_uri, predicate, URIRef(entry)))
        copy_id += 1
        return True, copy_id
    else:
        return False, copy_id


def insert_blanknode_entry(request, rdf_map, result, node_uri, predicate, o, root_id, copy_id):
    node = BNode()
    included_properties = list(rdf_map.predicate_objects(o))
    found_entry = False
    for p in included_properties:
        full_id = root_id + '-' + str(copy_id) + ':' + p[1].split(':')[-1]
        found_entry_for_property = insert_entries(request, rdf_map, result, node, p[0], p[1], full_id)
        if found_entry_for_property:
            found_entry = True
    copy_id += 1
    if found_entry:
        result.add((node_uri, predicate, node))
        return True, copy_id
    else:
        return False, copy_id
