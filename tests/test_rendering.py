import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
import rendering


def test_render_template_basic():
    dynamic_result = rendering.render_template_basic('Test Title', 1)
    static_result = open('basic_result.html', 'r').read()

    assert dynamic_result == static_result
