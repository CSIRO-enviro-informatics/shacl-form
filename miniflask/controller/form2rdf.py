from rdflib import Graph, RDF, XSD
from rdflib.util import guess_format
from rdflib.term import Literal, URIRef, BNode
import uuid


def form_to_rdf(request, map_filename):
    # Get map and result RDF graphs ready
    rdf_map = Graph()
    result = Graph()
    result.namespace_manager = rdf_map.namespace_manager
    rdf_map.parse(map_filename, format=guess_format(map_filename))
    # Get unique URI of the new node
    # To do: Other URI options
    node_class = rdf_map.value(Literal('placeholder:node_uri'), URIRef(RDF.type), None)
    entry_uuid = str(uuid.uuid4())
    node_uri = URIRef('http://example.org/ex#record/' + entry_uuid)
    result.add((node_uri, RDF.type, node_class))
    for (subject, predicate, o) in rdf_map:
        if str(subject) == 'placeholder:node_uri' and not predicate == RDF.type:
            insert_entries(request, rdf_map, result, node_uri, predicate, o)
    return node_uri, node_class, result


def insert_entries(request, rdf_map, result, node_uri, predicate, o, root_id=None):
    """
    :param request: Data collected from the form
    :param rdf_map: The RDF file that describes how the data from the form will fit into the RDF entry.
    :param result: The RDF file that will hold the new entry
    :param node_uri: The node that the property will attach to (the subject)
    :param predicate: The predicate of the property
    :param o: The object of the property, either a literal or a blank node pointing to more properties
    :param root_id: Used for property recursion, provides a starting point for IDs to iterate through
    :return:
    """
    if 'placeholder' in o:
        # Simple properties
        if not root_id:
            root_id = o.split(':')[-1]
        copy_id = 0
        found_entry = False
        while True:
            full_id = root_id + '-' + str(copy_id)
            entry = request.form.get(full_id)
            # Datatype of boolean can't be specified the usual way (i.e. "placeholder:1"^^xsd:boolean)
            # Boolean properties have prefix of 'boolean-' (i.e. "boolean-placeholder:1")
            if o.startswith('boolean-'):
                # Unchecked checkboxes in a form aren't submitted with the form
                # Form has been altered to submit hidden field with prefix 'unchecked:' if a checkbox isn't checked
                # Normal entry -> True
                if entry:
                    result.add((node_uri, predicate, Literal(True, datatype=XSD.boolean)))
                    found_entry = True
                    copy_id += 1
                # Entry with prefix 'unchecked' -> False
                elif request.form.get('unchecked:' + full_id):
                    result.add((node_uri, predicate, Literal(False, datatype=XSD.boolean)))
                    found_entry = True
                    copy_id += 1
                # Neither -> No value
                else:
                    break
            elif entry:
                result.add((node_uri, predicate, Literal(entry, datatype=o.datatype)))
                found_entry = True
                copy_id += 1
            else:
                break
        return found_entry
    else:
        # Composite properties
        included_properties = list(rdf_map.predicate_objects(o))
        if not root_id:
            if len(included_properties) > 0:
                root_id = included_properties[0][1].split(':')[-2]
            else:
                return False
        copy_id = 0
        while True:
            node = BNode()
            found_entry = False
            for p in included_properties:
                full_id = root_id + '-' + str(copy_id) + ':' + p[1].split(':')[-1]
                found_entry = insert_entries(rdf_map, result, node, p[0], p[1], full_id)
            copy_id += 1
            if found_entry:
                result.add((node_uri, predicate, node))
            else:
                break
