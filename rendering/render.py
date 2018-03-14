import os
from jinja2 import Template


def render_template(target_class, properties):
    template_file_path = os.path.join(os.path.dirname(__file__), 'base.html')
    t = Template(open(template_file_path, 'r').read())
    return t.render(target_class=target_class, properties=properties)
