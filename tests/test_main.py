import sys
import os
import pytest
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
import main

def test_empty_file():
    with pytest.raises(Exception):
        main.generate_webform("inputs/empty_file.ttl")

def test_empty_shape():
    main.generate_webform("inputs/empty_shape.ttl")
    result = open("result.html", 'r').read()
    expected_result = open("expected_results/empty_shape.html").read()
    assert result == expected_result
