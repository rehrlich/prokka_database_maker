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
        ftp.cwd('pub/taxonomy')

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

        return {int(x) for x in consistent_taxa}
