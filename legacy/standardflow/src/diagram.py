import graphviz
import json
import os
import subprocess
from tempfile import TemporaryDirectory

class Diagram:
    """
    A base class for generating diagrams.
    """
    def __init__(self, data):
        """
        Initializes the Diagram object.

        Args:
            data (dict): A dictionary containing the diagram data.
        """
        self.data = data
        self.dot = graphviz.Digraph()
        self.dot.attr('node', shape='box')

    def _apply_styles(self):
        """Applies the styles from the data to the graph."""
        if 'style' in self.data:
            style = self.data['style']
            if 'box_color' in style:
                self.dot.attr('node', style='filled', fillcolor=style['box_color'])
            if 'font_color' in style:
                self.dot.attr('node', fontcolor=style['font_color'])
                self.dot.attr('edge', fontcolor=style['font_color'])
            if 'font_name' in style:
                self.dot.attr('node', fontname=style['font_name'])
                self.dot.attr('edge', fontname=style['font_name'])
            if 'font_size' in style:
                self.dot.attr('node', fontsize=style['font_size'])
                self.dot.attr('edge', fontsize=style['font_size'])
            if 'arrow_color' in style:
                self.dot.attr('edge', color=style['arrow_color'])

    def _build_graph(self):
        """Builds the graph structure. This method should be overridden by subclasses."""
        raise NotImplementedError

    def generate(self, output_filename):
        """
        Generates the diagram and saves it to a file.

        Args:
            output_filename (str): The name of the output file.
        """
        self.dot.clear()
        self.dot.attr('node', shape='box')
        self._apply_styles()
        self._build_graph()

        file_format = os.path.splitext(output_filename)[1][1:] or 'png'
        if not os.path.splitext(output_filename)[1]:
            output_filename = os.fspath(output_filename) + '.png'

        if file_format == 'tiff':
            with TemporaryDirectory() as directory:
                png = self.dot.render(os.path.join(directory, 'diagram'),
                                      format='png', view=False, cleanup=True)
                subprocess.run(['convert', png, os.fspath(output_filename)], check=True)
        elif file_format == 'typ':
            base = os.path.splitext(output_filename)[0]
            svg = self.dot.render(base, format='svg', view=False, cleanup=True)
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(f'#image({json.dumps(os.path.basename(svg), ensure_ascii=False)})\n')
        else:
            base = os.path.splitext(output_filename)[0]
            self.dot.render(base, format=file_format, view=False, cleanup=True)

        print(f"{self.data['diagram_type']} diagram saved as {output_filename}")
