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

@unittest.mock.patch('scripts.petri_net_generation.generate_net.create_petri_net_from_checklist')
@unittest.mock.patch('scripts.petri_net_generation.generate_net.pm4py.write_pnml')
@unittest.mock.patch('scripts.petri_net_generation.generate_net.pm4py.save_vis_petri_net')
def test_successful_petri_net_generation(mock_save_vis, mock_write_pnml, mock_create, tmp_path):
    """
    Test the successful path of Petri net generation where input is parsed,
    directory is created, and pm4py writes the files.
    """
    input_file = "valid_input.md"
    output_pnml = os.path.join(tmp_path, "output", "test_output.pnml")

    # Mock create_petri_net_from_checklist to return mock data
    mock_create.return_value = ("mock_net", "mock_im", "mock_fm")

    # Run the main function with mocked arguments
    with unittest.mock.patch('sys.argv', ['generate_net.py', input_file, output_pnml]):
        main()

    # Assert create_petri_net_from_checklist was called with input_file
    mock_create.assert_called_once_with(input_file)

    # Assert directory was created
    assert os.path.exists(os.path.dirname(output_pnml))

    # Assert pm4py.write_pnml was called correctly
    mock_write_pnml.assert_called_once_with("mock_net", "mock_im", "mock_fm", output_pnml)

    # Assert pm4py.save_vis_petri_net was called correctly
    visualization_path = os.path.splitext(output_pnml)[0] + ".png"
    mock_save_vis.assert_called_once_with("mock_net", "mock_im", "mock_fm", visualization_path)
