import yaml
import pm4py
import os
import sys

from pm4py.objects.petri_net.obj import PetriNet, PetriNet
from pm4py.objects.petri_net.utils import petri_utils

def create_petri_net_from_checklist(checklist_file):
    """
    Creates a Petri net from a checklist YAML file.
    """
    with open(checklist_file, 'r') as f:
        checklist = yaml.safe_load(f)

    net = PetriNet(checklist['title'])
    source = PetriNet.Place("source")
    net.places.add(source)

    # Create a sink place
    sink = PetriNet.Place("sink")
    net.places.add(sink)

    # Single transition for the whole checklist for now
    transition = PetriNet.Transition(name=checklist['id'], label=checklist['title'])
    net.transitions.add(transition)
    petri_utils.add_arc_from_to(source, transition, net)
    petri_utils.add_arc_from_to(transition, sink, net)

    # Create initial and final markings
    initial_marking = pm4py. Marking({source: 1})
    final_marking = pm4py.Marking({sink: 1})

    return net, initial_marking, final_marking

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_net.py <input_yaml> <output_pnml>")
        sys.exit(1)

    input_yaml = sys.argv[1]
    output_pnml = sys.argv[2]

    print(f"Generating Petri net for {input_yaml}...")
    petri_net = create_petri_net_from_checklist(input_yaml)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_pnml)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

        print(f"Generating Petri net for {input_yaml}...")
    petri_net, initial_marking, final_marking = create_petri_net_from_checklist(input_yaml)

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

    # Save the Petri net
    pm4py.write_pnml(petri_net, initial_marking, final_marking, output_pnml)
    print(f"Petri net saved to {output_pnml}")

    # Save the visualization
    pm4py.save_vis_petri_net(petri_net, initial_marking, final_marking, visualization_path)


if __name__ == "__main__":
    main()