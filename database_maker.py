#!/usr/bin/env python3

import argparse
import os
import pandas as pd
from taxonomy_tree import TaxonomyTree
from ncbi_download import NcbiDownload
import re


def make_args():
    parser = argparse.ArgumentParser(
        description='Create a genus database for use with Prokka',
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-n', '--name',
                        help='A name for the genus database',
                        default='new_genus_database')
    parser.add_argument('-o', '--outdir',
                        help='A directory for storing outputs',
                        default=os.getcwd() + '/database_files')
    parser.add_argument('-a', '--all_files',
                        help='True if you want to download all files for each strain\nFalse if you only want the necessary files',
                        type=bool,
                        default=False)

    required_flags = parser.add_argument_group('Required arguments')

    required_flags.add_argument('-t', '--taxid',
                                help='The ncbi taxids for the database',
                                nargs='+',
                                type=int,
                                required=True)

    return parser.parse_args()


def filter_genomes(filtered_genomes, target_taxa):
    filtered_genomes = filtered_genomes[
        filtered_genomes['assembly_level'] == 'Complete Genome']
    filtered_genomes = filtered_genomes[
        filtered_genomes['version_status'] == 'latest']
    filtered_genomes = filtered_genomes[
        filtered_genomes['taxid'].isin(target_taxa) | filtered_genomes[
            'species_taxid'].isin(target_taxa)]
    return filtered_genomes


def main():
    args = make_args()
    taxa_tree = TaxonomyTree()

    target_taxa = set()
    for taxid in args.taxid:
        target_taxa.update(taxa_tree.get_consistent_below(str(taxid)))

    all_genomes = pd.read_csv('refs/assembly_summary.txt',
                              sep='\t', skiprows=1)

    filtered_genomes = filter_genomes(all_genomes, target_taxa)

    ftp = NcbiDownload.login()

    for line, genome in filtered_genomes.iterrows():
        dl = NcbiDownload(re.search('(genomes.*)', genome.ftp_path).group(1),
                          args.outdir + '/' + genome['# assembly_accession'])
        dl.download(ftp, all_files=False)
        dl.calc_checksum()
        break
    NcbiDownload.logout(ftp)

    print(filtered_genomes.shape)


if __name__ == '__main__':
    main()
