import yaml
import pm4py
import os
import sys
import re

from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils import petri_utils

def create_petri_net_from_checklist(checklist_file):
    """
    Creates a Petri net from a checklist Markdown file.
    """
    with open(checklist_file, 'r') as f:
        content = f.read()

    # Extract title from H1
    title_match = re.search(r'^#\s(.+)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(checklist_file)

    net = PetriNet(title)
    source = PetriNet.Place("source")
    sink = PetriNet.Place("sink")
    net.places.add(source)
    net.places.add(sink)

    # Find all checklist items
    items = re.findall(r'-\s\[\s\].*', content)

    if not items:
        # If no items, create a single transition for the whole document
        transition = PetriNet.Transition(name=title, label=title)
        net.transitions.add(transition)
        petri_utils.add_arc_from_to(source, transition, net)
        petri_utils.add_arc_from_to(transition, sink, net)
    else:
        # Create a chain of transitions for the items
        last_place = source
        for i, item_text in enumerate(items):
            # Clean up item text for transition name
            item_name = re.sub(r'[^a-zA-Z0-9\s]', '', item_text).strip()[:50]
            transition = PetriNet.Transition(name=f"item_{i+1}", label=item_name)
            net.transitions.add(transition)

            petri_utils.add_arc_from_to(last_place, transition, net)

            # Create intermediate place
            intermediate_place = PetriNet.Place(f"p{i+1}")
            net.places.add(intermediate_place)
            petri_utils.add_arc_from_to(transition, intermediate_place, net)
            last_place = intermediate_place

        # Add a final transition to the sink
        final_transition = PetriNet.Transition(name="final_transition", label="End")
        net.transitions.add(final_transition)
        petri_utils.add_arc_from_to(last_place, final_transition, net)
        petri_utils.add_arc_from_to(final_transition, sink, net)


    initial_marking = pm4py.Marking({source: 1})
    final_marking = pm4py.Marking({sink: 1})


    return net, initial_marking, final_marking

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_net.py <input_markdown> <output_pnml>")
        sys.exit(1)

    input_markdown = sys.argv[1]
    output_pnml = sys.argv[2]

    print(f"Generating Petri net for {input_markdown}...")
    petri_net, initial_marking, final_marking = create_petri_net_from_checklist(input_markdown)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_pnml)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the Petri net
    pm4py.write_pnml(petri_net, initial_marking, final_marking, output_pnml)
    print(f"Petri net saved to {output_pnml}")

    # Save the visualization
    visualization_path = os.path.splitext(output_pnml)[0] + ".png"
    pm4py.save_vis_petri_net(petri_net, initial_marking, final_marking, visualization_path)
    print(f"Visualization saved to {visualization_path}")


if __name__ == "__main__":
    main()
