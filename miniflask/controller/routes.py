from flask import Blueprint, render_template, request, Response
import os
from form2rdf import Form2RDFController

routes = Blueprint('controller', __name__)


@routes.route('/')
def index():
    return render_template('index.html')


@routes.route('/form')
def form():
    return render_template('form_contents.html')


@routes.route('/post', methods=['POST'])
def post():
    form2rdf_controller = Form2RDFController('http://example.org/ex#')
    try:
        rdf_result = form2rdf_controller.convert(request, 'map.ttl')
    except ValueError as e:
        return Response(str(e))

    if not os.path.exists('../entries'):
        os.makedirs('../entries')
    rdf_result.serialize(destination='result.ttl', format='turtle')
    return render_template('post.html')

