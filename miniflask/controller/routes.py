from flask import Blueprint, render_template, request, Response
import os
from controller.form2rdf import form_to_rdf

routes = Blueprint('controller', __name__)


@routes.route('/')
def index():
    return render_template('index.html')


@routes.route('/form')
def form():
    return render_template('form_contents.html')


@routes.route('/post', methods=['POST'])
def post():
    try:
        node_uri, node_class, result = form_to_rdf(request, 'map.ttl')
    except ValueError as e:
        return Response(str(e))

    if not os.path.exists('../entries'):
        os.makedirs('../entries')
    result.serialize(destination='result.ttl', format='turtle')
    return render_template('post.html')

