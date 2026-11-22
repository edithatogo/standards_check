from pathlib import Path

class Checklist:
    """
    A class to generate checklists from a JSON file.
    """
    def __init__(self, data):
        """
        Initializes the Checklist object.

        Args:
            data (dict): A dictionary containing the checklist data.
        """
        self.data = data

    def to_markdown_by_section(self):
        """
        Generates a dictionary of Markdown representations of the checklist, with one entry per section.
        """
        sections = {}
        filenames = {}
        for item in self.data['items']:
            section = item['section']
            if not section.strip() or any(char in section for char in ('/', '\\', '\0')):
                raise ValueError('Checklist sections must be safe file names.')
            filename = section.replace(' ', '_').casefold()
            if filename in filenames and filenames[filename] != section:
                raise ValueError('Checklist section file names must be distinct.')
            filenames[filename] = section
            if section not in sections:
                sections[section] = ""

            sections[section] += f"**{item['id']}**: {item['description']}\n\n"

            if item['type'] == 'boolean':
                sections[section] += f"[ ] Yes\n"
                sections[section] += f"[ ] No\n"
            elif item['type'] in ('string', 'integer'):
                sections[section] += f"Response: ________________\n"
            elif item['type'] == 'multiple_choice':
                for option in item['options']:
                    sections[section] += f"[ ] {option}\n"

            sections[section] += "\n"

        return sections

    def to_markdown(self):
        return ''.join(self.to_markdown_by_section().values())

    def generate(self, output_directory="checklist"):
        """
        Generates the checklist and saves it to a directory of files.

        Args:
            output_directory (str): The name of the output directory.
        """
        sections = self.to_markdown_by_section()
        directory = Path(output_directory)
        directory.mkdir(parents=True, exist_ok=True)
        for section, markdown in sections.items():
            filename = f"{section.replace(' ', '_')}.md"
            (directory / filename).write_text(markdown, encoding='utf-8')

        print(f"Checklist saved to directory {output_directory}")
