import os
import sys
import pytest

# Add the project root to the path so we can import from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.petri_net_generation.generate_net import main, create_petri_net_from_checklist

def test_exception_handling_creates_empty_files(tmp_path, monkeypatch):
    """
    Test that when an exception occurs during Petri net generation
    (e.g., input file not found), the script creates empty output files
    to satisfy Make dependencies.
    """
    input_file = "non_existent_input.md"
    output_pnml = os.path.join(tmp_path, "output", "test_output.pnml")

    # Run the main function with mocked arguments
    monkeypatch.setattr('sys.argv', ['generate_net.py', input_file, output_pnml])
    main()

    # The script should have created the output directory and empty files
    assert os.path.exists(output_pnml), "Empty PNML file was not created"
    assert os.path.getsize(output_pnml) == 0, "PNML file is not empty"

    output_png = os.path.splitext(output_pnml)[0] + ".png"
    assert os.path.exists(output_png), "Empty PNG visualization file was not created"
    assert os.path.getsize(output_png) == 0, "PNG file is not empty"

def test_no_sections_no_items(tmp_path):
    # Setup test file
    md_content = "# Simple Title\n\nJust some text without items or sections."
    test_file = tmp_path / "test1.md"
    test_file.write_text(md_content)

    net, initial_marking, final_marking = create_petri_net_from_checklist(str(test_file))

    assert net.name == "Simple Title"

    # Places: source and sink
    assert len(net.places) == 2
    place_names = {p.name for p in net.places}
    assert "source" in place_names
    assert "sink" in place_names

    # Transitions: one single transition
    assert len(net.transitions) == 1
    transition = list(net.transitions)[0]
    assert transition.name == "single_transition"
    assert transition.label == "Simple Title"

    # Arcs: source -> transition -> sink
    assert len(net.arcs) == 2

def test_no_sections_with_items(tmp_path):
    md_content = "# Items Title\n\n- [ ] Item 1\n- [ ] Item 2\n- [ ] Item 3"
    test_file = tmp_path / "test2.md"
    test_file.write_text(md_content)

    net, initial_marking, final_marking = create_petri_net_from_checklist(str(test_file))

    assert net.name == "Items Title"

    # 2 (source, sink) + 3 intermediate places = 5 places
    assert len(net.places) == 5
    place_names = {p.name for p in net.places}
    assert place_names == {"source", "sink", "p1", "p2", "p3"}

    # 3 item transitions + 1 final transition = 4 transitions
    assert len(net.transitions) == 4
    transition_names = {t.name for t in net.transitions}
    assert transition_names == {"item_1", "item_2", "item_3", "final_transition"}

def test_with_sections_no_items(tmp_path):
    md_content = "# Sections Title\n\n## Section A\n\nSome text.\n\n## Section B"
    test_file = tmp_path / "test3.md"
    test_file.write_text(md_content)

    net, initial_marking, final_marking = create_petri_net_from_checklist(str(test_file))

    assert net.name == "Sections Title"

    # 2 global (source, sink) + 2 section start places = 4 places
    assert len(net.places) == 4

    # 2 section transitions + 1 final transition = 3 transitions
    assert len(net.transitions) == 3

    t_labels = {t.label for t in net.transitions}
    assert t_labels == {"Section A", "Section B", "End"}

def test_with_sections_and_items(tmp_path):
    md_content = "# Complex Title\n\n## Section 1\n\n- [ ] Task 1.1\n- [ ] Task 1.2\n\n## Section 2\n\n- [ ] Task 2.1"
    test_file = tmp_path / "test4.md"
    test_file.write_text(md_content)

    net, initial_marking, final_marking = create_petri_net_from_checklist(str(test_file))

    assert net.name == "Complex Title"

    # Transitions:
    # section_1
    # sec_1_item_1
    # sec_1_item_2
    # section_2
    # sec_2_item_1
    # final_transition
    assert len(net.transitions) == 6
    t_names = {t.name for t in net.transitions}
    assert t_names == {"section_1", "sec_1_item_1", "sec_1_item_2", "section_2", "sec_2_item_1", "final_transition"}

    # Places:
    # source, sink
    # sec_1_start
    # sec_1_p_1
    # sec_1_p_2
    # sec_2_start
    # sec_2_p_1
    assert len(net.places) == 7

def test_title_extraction_fallback(tmp_path):
    # No H1 tag
    md_content = "## Section 1\n- [ ] Task"
    test_file = tmp_path / "test5.md"
    test_file.write_text(md_content)

    net, initial_marking, final_marking = create_petri_net_from_checklist(str(test_file))

    # Fallback is the filename
    assert net.name == "test5.md"

def test_main_success(tmp_path, monkeypatch):
    input_file = tmp_path / "test_success.md"
    input_file.write_text("# Test Title\n- [ ] Item")
    output_pnml = tmp_path / "output" / "out.pnml"

    monkeypatch.setattr('sys.argv', ['generate_net.py', str(input_file), str(output_pnml)])
    main()

    assert os.path.exists(output_pnml)
    assert os.path.getsize(output_pnml) > 0

    output_png = os.path.splitext(str(output_pnml))[0] + ".png"
    assert os.path.exists(output_png)
    assert os.path.getsize(output_png) > 0

def test_main_usage(monkeypatch):
    monkeypatch.setattr('sys.argv', ['generate_net.py'])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1

def test_exception_handling_main_dir_exists(tmp_path, monkeypatch):
    # If the output directory exists, it still creates the empty files
    input_file = "non_existent_input.md"
    output_dir = tmp_path / "existing_out"
    output_dir.mkdir()
    output_pnml = output_dir / "test_output.pnml"

    monkeypatch.setattr('sys.argv', ['generate_net.py', input_file, str(output_pnml)])
    main()

    assert os.path.exists(output_pnml)
    assert os.path.getsize(output_pnml) == 0

    output_png = os.path.splitext(str(output_pnml))[0] + ".png"
    assert os.path.exists(output_png)
    assert os.path.getsize(output_png) == 0

def test_main_success_dir_exists(tmp_path, monkeypatch):
    # Setup test file
    input_file = tmp_path / "test_success_2.md"
    input_file.write_text("# Test Title\n- [ ] Item")

    # Pre-create output dir
    output_dir = tmp_path / "existing_success_out"
    output_dir.mkdir()
    output_pnml = output_dir / "out.pnml"

    monkeypatch.setattr('sys.argv', ['generate_net.py', str(input_file), str(output_pnml)])
    main()

    assert os.path.exists(output_pnml)
    assert os.path.getsize(output_pnml) > 0
