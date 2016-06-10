from collections import defaultdict


class TaxonomyTree:
    def __init__(self):
        self.children = defaultdict(list)
        self.nodes_file = 'refs/taxonomy_nodes.txt'
        self.parse_tree()

    def parse_tree(self):
        with open(self.nodes_file, 'r') as f:
            for line in f:
                split_line = line.split('\t|\t')
                self.children[split_line[1]].append(split_line[0])

    def get_consistent_below(self, taxa):
        all_children = set()
        all_children.add(taxa)
        consistent_taxa = set()
        while all_children:
            curr = all_children.pop()
            consistent_taxa.add(curr)
            all_children = all_children.union(self.children[curr])

        return consistent_taxa
