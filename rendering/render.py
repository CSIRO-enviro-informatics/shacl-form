import os
from jinja2 import Template

'''
Properties - a list of tuples containing the name, path and datatype of each property.
'''

URI_EMAIL = "http://xmlns.com/foaf/0.1/mbox"  # Don't feel comfortable pasting this straight into base.html


def render_template(form_name, shape):
    base_template = Template(open(os.path.join(os.path.dirname(__file__), 'base.html'), 'r').read())
    property_template = Template(open(os.path.join(os.path.dirname(__file__), 'property.html'), 'r').read())
    return base_template.render(
        form_name=form_name,
        shape=shape,
        URI_EMAIL=URI_EMAIL,
        property_template=property_template
    )
