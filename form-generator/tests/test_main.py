import sys
import os
import pytest
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
import main

def test_empty_file():
    with pytest.raises(Exception):
        main.generate_webform("inputs/empty_file.ttl", "results/")

def test_empty_shape():
    main.generate_webform("inputs/empty_shape.ttl", "results/")
    assert os.path.exists("results/view/templates/form_contents.html")
    assert os.path.getsize("results/view/templates/form_contents.html") == 0
    assert open("results/view/templates/form_heading.html", 'r').read() == 'Create New Person'
