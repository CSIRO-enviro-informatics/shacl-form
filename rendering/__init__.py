import os
from jinja2 import FileSystemLoader, Environment

'''
Properties - a list of tuples containing the name, path and datatype of each property.
'''

URI_EMAIL = "http://xmlns.com/foaf/0.1/mbox"  # Don't feel comfortable pasting this straight into base.html


def render_template(form_name, shape):
    loader = FileSystemLoader(searchpath=os.path.dirname(__file__))
    env = Environment(loader=loader)
    template = env.get_template("base.html")
    return template.render(form_name=form_name, shape=shape, URI_EMAIL=URI_EMAIL)
