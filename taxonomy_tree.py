from collections import defaultdict
from subprocess import call
from ftp_utils import FtpUtils


class TaxonomyTree:
    def __init__(self, outdir, ftp):
        self.children = defaultdict(list)
        self.outdir = outdir
        self.get_nodes_file(ftp)
        self.nodes_file = self.outdir + '/nodes.dmp'
        self.parse_tree()

    def get_nodes_file(self, ftp):
        """
        Downloads taxonomy tree files, checks the md5 and opens the tar.gz
        :param ftp: an ftp connection to ncbi
        """
        ftp.cwd('/pub/taxonomy')

        listing = []
        ftp.retrlines("LIST", listing.append)

        call(['mkdir', '-p', self.outdir])

        for row in listing:
            ncbi_filename = row.split(None, 8)[-1].lstrip().split(' ')[0]
            if ncbi_filename.startswith('taxdump.tar.gz'):
                local_file = self.outdir + '/' + ncbi_filename
                with open(local_file, "wb") as lf:
                    ftp.retrbinary("RETR " + ncbi_filename, lf.write, 8*1024)

        FtpUtils.calc_checksum(self.outdir + '/taxdump.tar.gz.md5', self.outdir)
        call(['tar', '-xzf', self.outdir + '/taxdump.tar.gz', '-C', self.outdir])

    def parse_tree(self):
        """
        Creates a dictionary to represent the ncbi taxonomy tree.  Each key is
        a node in the tree.  The value for a key is the list of children nodes.
        All nodes are ncbi taxonomy ids.
        Example:  The key 561 (Escherichia) has a list of values that includes
        562 (Escherichia coli)
        """
        with open(self.nodes_file, 'r') as f:
            for line in f:
                split_line = line.split('\t|\t')
                self.children[split_line[1]].append(split_line[0])

    def get_consistent_below(self, taxa):
        """
        A taxonomy id is consistent below a given taxa if it is that taxa or
        one of its descendants in the taxonomy tree.
        Example:  Node 562 (Escherichia coli) is consistent below the node
        561 (Escherichia).
        x.get_consistent_below('561') returns a set that includes '562'
        :param taxa: a taxonomy id as a string
        :return: a set of ints of taxonomy ids that are consistent below the
        param taxa
        """
        all_children = set()
        all_children.add(taxa)
        consistent_taxa = set()
        while all_children:
            curr = all_children.pop()
            consistent_taxa.add(curr)
            all_children = all_children.union(self.children[curr])

        return {int(x) for x in consistent_taxa}
