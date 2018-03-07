import sys
import os
from jinja2 import Template


def render_template_basic(title, choice):
    template_file_path = os.path.join(os.path.dirname(__file__), 'basic.html')
    t = Template(open(template_file_path, 'r').read())
    return t.render(title=title, choice=choice)


if __name__ == '__main__':
    with open('result.html', 'w') as f:
        f.write(render_template_basic("New title", 1))
