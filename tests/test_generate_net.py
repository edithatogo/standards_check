import os
import sys
import unittest.mock
import pytest

# Add the project root to the path so we can import from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.petri_net_generation.generate_net import main

def test_exception_handling_creates_empty_files(tmp_path):
    """
    Test that when an exception occurs during Petri net generation
    (e.g., input file not found), the script creates empty output files
    to satisfy Make dependencies.
    """
    input_file = "non_existent_input.md"
    output_pnml = os.path.join(tmp_path, "output", "test_output.pnml")

    # Run the main function with mocked arguments
    with unittest.mock.patch('sys.argv', ['generate_net.py', input_file, output_pnml]):
        main()

    # The script should have created the output directory and empty files
    assert os.path.exists(output_pnml), "Empty PNML file was not created"
    assert os.path.getsize(output_pnml) == 0, "PNML file is not empty"

    output_png = os.path.splitext(output_pnml)[0] + ".png"
    assert os.path.exists(output_png), "Empty PNG visualization file was not created"
    assert os.path.getsize(output_png) == 0, "PNG file is not empty"
