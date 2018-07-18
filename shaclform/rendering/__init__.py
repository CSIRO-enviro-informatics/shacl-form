import os
from jinja2 import FileSystemLoader, Environment

URIs = {
    'NUMBER': [
        'http://www.w3.org/2001/XMLSchema#integer',
        'http://www.w3.org/2001/XMLSchema#float',
        'http://www.w3.org/2001/XMLSchema#double',
        'http://www.w3.org/2001/XMLSchema#decimal'
    ],
    'EMAIL': 'http://xmlns.com/foaf/0.1/mbox',
    'DATE': 'http://www.w3.org/2001/XMLSchema#date',
    'PHONE_NUMBER': 'http://xmlns.com/foaf/0.1/phone',
    'TIME': 'http://www.w3.org/2001/XMLSchema#time',
    'BOOLEAN': 'http://www.w3.org/2001/XMLSchema#boolean',
    'STRING': 'http://www.w3.org/2001/XMLSchema#string',
    'BLANK_NODE': 'http://www.w3.org/ns/shacl#BlankNode',
    'IRI': 'http://www.w3.org/ns/shacl#IRI',
    'LITERAL': 'http://www.w3.org/ns/shacl#Literal',
    'BLANK_NODE_OR_IRI': 'http://www.w3.org/ns/shacl#BlankNodeOrIRI',
    'BLANK_NODE_OR_LITERAL': 'http://www.w3.org/ns/shacl#BlankNodeOrLiteral',
    'IRI_OR_LITERAL': 'http://www.w3.org/ns/shacl#IRIOrLiteral'
}


def render_template(form_name, shape):
    loader = FileSystemLoader(searchpath=os.path.dirname(__file__))
    env = Environment(loader=loader)
    template = env.get_template('base.html')
    return template.render(form_name=form_name, shape=shape, URIs=URIs)
