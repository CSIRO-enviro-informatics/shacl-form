import os
from jinja2 import FileSystemLoader, Environment

'''
Properties - a list of tuples containing the name, path and datatype of each property.
'''

URIs = {
    "NUMBER": [
        "http://www.w3.org/2001/XMLSchema#integer",
        "http://www.w3.org/2001/XMLSchema#float",
        "http://www.w3.org/2001/XMLSchema#double"
    ],
    "EMAIL": "http://xmlns.com/foaf/0.1/mbox",
    "DATE": "http://www.w3.org/2001/XMLSchema#date",
    "PHONE_NUMBER": "http://xmlns.com/foaf/0.1/phone"
}

def render_template(form_name, shape):
    loader = FileSystemLoader(searchpath=os.path.dirname(__file__))
    env = Environment(loader=loader)
    template = env.get_template("base.html")
    return template.render(form_name=form_name, shape=shape, URIs=URIs)
