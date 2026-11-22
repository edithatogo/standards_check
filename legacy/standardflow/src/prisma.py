from .diagram import Diagram

class PrismaDiagram(Diagram):
    """
    A class to generate PRISMA 2020 flow diagrams.
    """
    def __init__(self, data):
        """
        Initializes the PrismaDiagram object.

        Args:
            data (dict): A dictionary containing the PRISMA data.
        """
        super().__init__(data)
        self.dot.comment = 'PRISMA 2020 Flow Diagram'

    def _build_graph(self):
        """Builds the graph structure."""
        if self.data['diagram_type'] == 'PRISMA':
            self._build_prisma_graph()
        elif self.data['diagram_type'] == 'PRISMA_2020_UPDATED':
            self._build_updated_prisma_graph()

    def _build_prisma_graph(self):
        """Builds the graph for the standard PRISMA 2020 flow diagram."""
        self.dot.node('A', f'Records identified through database searching\n(n = {self.data["records_identified"]})')
        self.dot.node('B', f'Records after duplicates removed\n(n = {self.data["records_after_duplicates_removed"]})')
        self.dot.node('C', f'Records screened\n(n = {self.data["records_screened"]})')
        self.dot.node('D', f'Records excluded\n(n = {self.data["records_excluded"]})')
        self.dot.node('E', f'Full-text articles assessed for eligibility\n(n = {self.data["full_text_articles_assessed"]})')
        self.dot.node('F', f'Full-text articles excluded, with reasons\n(n = {self.data["full_text_articles_excluded"]})')
        self.dot.node('G', f'Studies included in qualitative synthesis\n(n = {self.data["studies_included"]})')
        self.dot.node('H', f'Studies included in quantitative synthesis (meta-analysis)\n(n = {self.data["studies_included"]})')

        self.dot.edge('A', 'B')
        self.dot.edge('B', 'C')
        self.dot.edge('C', 'D')
        self.dot.edge('C', 'E')
        self.dot.edge('E', 'F')
        self.dot.edge('E', 'G')
        self.dot.edge('G', 'H')

    def _build_updated_prisma_graph(self):
        """Builds the graph for the updated PRISMA 2020 flow diagram."""
        self.dot.node('A', f'Studies included in previous version of review\n(n = {self.data["previous_studies"]})')
        self.dot.node('B', f'New records identified\n(n = {self.data["new_records_identified"]})')
        self.dot.node('C', f'New records after duplicates removed\n(n = {self.data["new_records_after_duplicates_removed"]})')
        self.dot.node('D', f'New records screened\n(n = {self.data["new_records_screened"]})')
        self.dot.node('E', f'New records excluded\n(n = {self.data["new_records_excluded"]})')
        self.dot.node('F', f'New full-text articles assessed for eligibility\n(n = {self.data["new_full_text_articles_assessed"]})')
        self.dot.node('G', f'New full-text articles excluded, with reasons\n(n = {self.data["new_full_text_articles_excluded"]})')
        self.dot.node('H', f'New studies included in qualitative synthesis\n(n = {self.data["new_studies_included"]})')
        self.dot.node('I', f'Total studies included in qualitative synthesis\n(n = {self.data["total_studies_included"]})')
        self.dot.node('J', f'Total studies included in quantitative synthesis (meta-analysis)\n(n = {self.data["total_studies_included"]})')

        self.dot.edge('A', 'I')
        self.dot.edge('B', 'C')
        self.dot.edge('C', 'D')
        self.dot.edge('D', 'E')
        self.dot.edge('D', 'F')
        self.dot.edge('F', 'G')
        self.dot.edge('F', 'H')
        self.dot.edge('H', 'I')
        self.dot.edge('I', 'J')

