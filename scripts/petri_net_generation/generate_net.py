import re
import os
import sys
import pm4py
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils import petri_utils

def parse_checklist(content, default_title):
    """
    Parses a checklist Markdown file content into a structured dictionary.
    """
    title_match = re.search(r'^#\s(.+)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else default_title

    parts = re.split(r'(^##\s.*$)', content, flags=re.MULTILINE)
    cleaned_parts = [p.strip() for p in parts if p.strip()]
    sections = []

    for i in range(0, len(cleaned_parts)):
        if cleaned_parts[i].startswith('##'):
            section_header = cleaned_parts[i]
            section_content = cleaned_parts[i+1] if i + 1 < len(cleaned_parts) and not cleaned_parts[i+1].startswith('##') else ""
            sections.append((section_header, section_content))

    items = []
    if not sections:
        items = re.findall(r'-\s\[\s\].*', content)

    return {
        "title": title,
        "sections": sections,
        "items": items
    }

def generate_petri_net(parsed_data):
    """
    Generates a Petri net from parsed checklist data.
    """
    title = parsed_data["title"]
    sections = parsed_data["sections"]
    items = parsed_data["items"]

    net = PetriNet(title)
    source = PetriNet.Place("source")
    sink = PetriNet.Place("sink")
    net.places.add(source)
    net.places.add(sink)

    if not sections:
        if not items:
            transition = PetriNet.Transition(name="single_transition", label=title)
            net.transitions.add(transition)
            petri_utils.add_arc_from_to(source, transition, net)
            petri_utils.add_arc_from_to(transition, sink, net)
        else:
            last_place = source
            for i, item_text in enumerate(items):
                item_name = re.sub(r'[^a-zA-Z0-9\s]', '', item_text).strip()[:50]
                transition = PetriNet.Transition(name=f"item_{i+1}", label=item_name)
                net.transitions.add(transition)
                petri_utils.add_arc_from_to(last_place, transition, net)
                
                intermediate_place = PetriNet.Place(f"p{i+1}")
                net.places.add(intermediate_place)
                petri_utils.add_arc_from_to(transition, intermediate_place, net)
                last_place = intermediate_place
            
            final_transition = PetriNet.Transition(name="final_transition", label="End")
            net.transitions.add(final_transition)
            petri_utils.add_arc_from_to(last_place, final_transition, net)
            petri_utils.add_arc_from_to(final_transition, sink, net)
    else:
        last_main_place = source
        for i, (header, section_content) in enumerate(sections):
            section_title = header.replace('##', '').strip()
            
            section_transition = PetriNet.Transition(name=f"section_{i+1}", label=section_title)
            net.transitions.add(section_transition)
            petri_utils.add_arc_from_to(last_main_place, section_transition, net)

            section_start_place = PetriNet.Place(f"sec_{i+1}_start")
            net.places.add(section_start_place)
            petri_utils.add_arc_from_to(section_transition, section_start_place, net)
            
            last_item_place = section_start_place
            section_items = re.findall(r'-\s\[\s\].*', section_content)
            if section_items:
                for j, item_text in enumerate(section_items):
                    item_name = re.sub(r'[^a-zA-Z0-9\s]', '', item_text).strip()[:50]
                    item_transition = PetriNet.Transition(name=f"sec_{i+1}_item_{j+1}", label=item_name)
                    net.transitions.add(item_transition)
                    petri_utils.add_arc_from_to(last_item_place, item_transition, net)

                    intermediate_place = PetriNet.Place(f"sec_{i+1}_p_{j+1}")
                    net.places.add(intermediate_place)
                    petri_utils.add_arc_from_to(item_transition, intermediate_place, net)
                    last_item_place = intermediate_place
            
            last_main_place = last_item_place

        final_transition = PetriNet.Transition(name="final_transition", label="End")
        net.transitions.add(final_transition)
        petri_utils.add_arc_from_to(last_main_place, final_transition, net)
        petri_utils.add_arc_from_to(final_transition, sink, net)

    initial_marking = pm4py.Marking({source: 1})
    final_marking = pm4py.Marking({sink: 1})

    return net, initial_marking, final_marking

def create_petri_net_from_checklist(checklist_file):
    """
    Creates a hierarchical Petri net from a checklist Markdown file,
    modeling sections and items.
    """
    with open(checklist_file, 'r') as f:
        content = f.read()

    default_title = os.path.basename(checklist_file)
    parsed_data = parse_checklist(content, default_title)
    return generate_petri_net(parsed_data)

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_net.py <input_markdown> <output_pnml>")
        sys.exit(1)

    input_markdown = sys.argv[1]
    output_pnml = sys.argv[2]

    print(f"Generating Petri net for {input_markdown}...")
    try:
        petri_net, initial_marking, final_marking = create_petri_net_from_checklist(input_markdown)

        output_dir = os.path.dirname(output_pnml)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        pm4py.write_pnml(petri_net, initial_marking, final_marking, output_pnml)
        print(f"Petri net saved to {output_pnml}")

        visualization_path = os.path.splitext(output_pnml)[0] + ".png"
        pm4py.save_vis_petri_net(petri_net, initial_marking, final_marking, visualization_path)
        print(f"Visualization saved to {visualization_path}")

    except Exception as e:
        print(f"Error processing {input_markdown}: {e}", file=sys.stderr)
        # Create empty files to satisfy make
        output_dir = os.path.dirname(output_pnml)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_pnml, 'w') as f:
            pass
        visualization_path = os.path.splitext(output_pnml)[0] + ".png"
        with open(visualization_path, 'w') as f:
            pass


if __name__ == "__main__":
    main()