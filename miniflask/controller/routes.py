from flask import Blueprint, render_template, Response, request
from rdflib import Graph
from rdflib.util import guess_format
from rdflib.namespace import RDF, RDFS
from rdflib.term import URIRef, Literal, BNode
import uuid
import os

routes = Blueprint('controller', __name__)


@routes.route('/')
def index():
    return render_template('index.html')


@routes.route('/form')
def form():
    return render_template('form.html')


@routes.route('/post', methods=['POST'])
def post():
    # Get map and result RDF graphs ready
    map = Graph()
    result = Graph()
    result.namespace_manager = map.namespace_manager
    map.parse('map.ttl', format=guess_format('map.ttl'))
    # Get unique URI of the new node
    # To do: Other URI options
    node_class = map.value(Literal('placeholder:node_uri'), URIRef(RDF.type), None)
    entry_uuid = str(uuid.uuid4())
    node_uri = URIRef('http://example.org/ex#' + entry_uuid)
    result.add((node_uri, RDF.type, node_class))
    for (subject, predicate, object) in map:
        if str(subject) == 'placeholder:node_uri' and not predicate == RDF.type:
            insert_entries(map, result, node_uri, predicate, object)

    if not os.path.exists('../entries'):
        os.makedirs('../entries')
    result.serialize(destination='../entries/' + entry_uuid + '.ttl', format='turtle')
    return render_template('post.html')


def insert_entries(map, result, node_uri, predicate, object, root_id=None):
    """
    :param map: The RDF file that describes how the data from the form will fit into the RDF entry.
    :param result: The RDF file that will hold the new entry
    :param node_uri: The node that the property will attach to (the subject)
    :param predicate: The predicate of the property
    :param object: The object of the property, either a literal or a blank node pointing to more properties
    :param root_id: Used for property recursion, provides a starting point for IDs to iterate through
    :return:
    """
    if 'placeholder' in object:
        # Simple properties
        if not root_id:
            root_id = object.split(':')[-1]
        copy_id = 0
        found_entry = False
        while True:
            full_id = root_id + '-' + str(copy_id)
            entry = request.form.get(full_id)
            if entry:
                result.add((node_uri, predicate, Literal(entry)))
                found_entry = True
                copy_id += 1
            else:
                break
        return found_entry
    else:
        # Composite properties
        included_properties = list(map.predicate_objects(object))
        if not root_id:
            if len(included_properties) > 0:
                root_id = included_properties[0][1].split(':')[-2]
            else:
                return False
        copy_id = 0
        while True:
            node = BNode()
            for p in included_properties:
                full_id = root_id + '-' + str(copy_id) + ':' + p[1].split(':')[-1]
                found_entry = insert_entries(map, result, node, p[0], p[1], full_id)
            copy_id += 1
            if found_entry:
                result.add((node_uri, predicate, node))
            else:
                break


