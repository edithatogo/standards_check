from .diagram import Diagram

class ConsortDiagram(Diagram):
    """
    A class to generate CONSORT 2010 flow diagrams.
    """
    def __init__(self, data):
        """
        Initializes the ConsortDiagram object.

        Args:
            data (dict): A dictionary containing the CONSORT data.
        """
        super().__init__(data)
        self.dot.comment = 'CONSORT 2010 Flow Diagram'

    def _build_graph(self):
        """Builds the graph structure."""
        if self.data['diagram_type'] == 'CONSORT':
            self._build_consort_graph()
        elif self.data['diagram_type'] == 'CONSORT_CLUSTER':
            self._build_cluster_graph()

    def _build_consort_graph(self):
        """Builds the graph for the standard CONSORT 2010 flow diagram."""
        self.dot.node('A', f'Assessed for eligibility (n={self.data["assessed_for_eligibility"]})')
        self.dot.node('B', f'Excluded (n={self.data["excluded"]})\n' +
                           '\n'.join(self.data.get("reasons_for_exclusion", [])))
        self.dot.node('C', f'Randomized (n={self.data["randomized"]})')
        self.dot.node('D', f'Allocated to intervention (n={self.data["allocated_to_intervention"]})')
        self.dot.node('E', f'Received allocated intervention (n={self.data["received_allocated_intervention"]})')
        self.dot.node('F', f'Did not receive allocated intervention (n={self.data["did_not_receive_allocated_intervention"]})\n' +
                           '\n'.join(self.data.get("reasons_for_not_receiving_intervention", [])))
        self.dot.node('G', f'Lost to follow-up (n={self.data["lost_to_follow_up"]})\n' +
                           '\n'.join(self.data.get("reasons_for_loss_to_follow_up", [])))
        self.dot.node('H', f'Discontinued intervention (n={self.data["discontinued_intervention"]})\n' +
                           '\n'.join(self.data.get("reasons_for_discontinuing_intervention", [])))
        self.dot.node('I', f'Analysed (n={self.data["analysed"]})')
        self.dot.node('J', f'Excluded from analysis (n={self.data["excluded_from_analysis"]})\n' +
                           '\n'.join(self.data.get("reasons_for_exclusion_from_analysis", [])))

        self.dot.edge('A', 'C')
        self.dot.edge('A', 'B')
        self.dot.edge('C', 'D')
        self.dot.edge('D', 'E')
        self.dot.edge('D', 'F')
        self.dot.edge('E', 'G')
        self.dot.edge('E', 'H')
        self.dot.edge('E', 'I')
        self.dot.edge('I', 'J')

    def _build_cluster_graph(self):
        """Builds the graph for the CONSORT 2010 flow diagram for cluster-randomised trials."""
        self.dot.node('A', f'Assessed for eligibility (n={self.data["clusters_assessed_for_eligibility"]} clusters)')
        self.dot.node('B', f'Excluded (n={self.data["clusters_excluded"]} clusters)\n' +
                           '\n'.join(self.data.get("reasons_for_cluster_exclusion", [])))
        self.dot.node('C', f'Randomized (n={self.data["clusters_randomized"]} clusters)')
        self.dot.node('D', f'Allocated to intervention (n={self.data["clusters_allocated_to_intervention"]} clusters, n={self.data["individuals_in_clusters_allocated_to_intervention"]} individuals)')
        self.dot.node('E', f'Lost to follow-up (n={self.data["clusters_lost_to_follow_up"]} clusters, n={self.data["individuals_lost_to_follow_up"]} individuals)\n' +
                           '\n'.join(self.data.get("reasons_for_cluster_loss_to_follow_up", [])))
        self.dot.node('F', f'Discontinued intervention (n={self.data["clusters_discontinued_intervention"]} clusters, n={self.data["individuals_discontinued_intervention"]} individuals)\n' +
                           '\n'.join(self.data.get("reasons_for_cluster_discontinuation", [])))
        self.dot.node('G', f'Analysed (n={self.data["clusters_analysed"]} clusters, n={self.data["individuals_analysed"]} individuals)')
        self.dot.node('H', f'Excluded from analysis (n={self.data["clusters_excluded_from_analysis"]} clusters, n={self.data["individuals_excluded_from_analysis"]} individuals)\n' +
                           '\n'.join(self.data.get("reasons_for_cluster_exclusion_from_analysis", [])))

        self.dot.edge('A', 'C')
        self.dot.edge('A', 'B')
        self.dot.edge('C', 'D')
        self.dot.edge('D', 'E')
        self.dot.edge('D', 'F')
        self.dot.edge('D', 'G')
        self.dot.edge('G', 'H')

