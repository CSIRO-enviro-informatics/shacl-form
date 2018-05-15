from flask import Blueprint, render_template, Response, request
from rdflib import Graph
from rdflib.util import guess_format
from rdflib.namespace import RDF, RDFS
from rdflib.term import URIRef, Literal, BNode
import uuid

routes = Blueprint('controller', __name__)


@routes.route('/')
def index():
    return render_template(
        'index.html'
    )


@routes.route('/form')
def form():
    return render_template(
        'form.html'
    )


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
    node_uri = URIRef('http://example.org/ex#' + str(uuid.uuid4()))
    result.add((node_uri, RDF.type, node_class))
    for (subject, predicate, object) in map:
        if str(subject) == 'placeholder:node_uri':
            insert_entry(map, result, node_uri, predicate, object)

    result.serialize(destination='result.ttl', format='turtle')
    return Response('test', status=201, mimetype='text/plain')


def insert_entry(map, result, node_uri, predicate, object):
    if 'placeholder' in object:
        # Simple properties
        root_id = object.split(':')[1]
        copy_id = 0
        while True:
            full_id = root_id + '-' + str(copy_id)
            entry = request.form.get(full_id)
            if entry:
                result.add((node_uri, predicate, Literal(entry)))
                copy_id += 1
            else:
                break
