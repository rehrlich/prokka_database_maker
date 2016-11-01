#!/usr/bin/env python3

import argparse
import os
import re
from subprocess import Popen, PIPE, call

from assembly_summary import AssemblySummary
from taxonomy_tree import TaxonomyTree
from ncbi_download import NcbiDownload
from ftp_utils import FtpUtils


def make_args():
    parser = argparse.ArgumentParser(
        description='Create a genus database for use with Prokka',
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-d', '--db_dir',
                        help='The directory for the database files\nExample:  /path/to/prokka/db/genus',
                        default=os.getcwd() + '/database_files/db')
    parser.add_argument('-n', '--name',
                        help='A name for the genus database',
                        default='new_genus_database')
    parser.add_argument('-o', '--outdir',
                        help='A directory for storing intermediate outputs',
                        default=os.getcwd() + '/database_files')
    parser.add_argument('-a', '--all_files',
                        help="Use -a if you want to download all files, don't "
                             "use it if you only want the files for the genus database",
                        default=False,
                        action="store_true")
    parser.add_argument('-i', '--include_incomplete',
                        help="Use -i if you want incomplete genomes, don't use it if you don't.",
                        default=False,
                        action="store_true")

    required_flags = parser.add_argument_group('Required argument')

    required_flags.add_argument('-t', '--taxid',
                                help='The ncbi taxids for the database',
                                nargs='+',
                                type=int,
                                required=True)

    return parser.parse_args()


def make_database(gbffs, outdir, genus_db_path, name):
    """
    Creates a Prokka genus database
    :param gbffs: a list of paths to gbff files
    :param outdir: directory to store intermediate files
    :param genus_db_path: the directory to store the database files
    :param name: a name for the database files
    """
    call(['mkdir', '-p', outdir])
    call(['mkdir', '-p', genus_db_path])

    cmd = 'prokka-genbank_to_fasta_db ' + ' '.join(gbffs)
    p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE, stdin=PIPE)
    output = p.communicate()[0].decode(encoding='UTF-8')

    cd_hit_out = outdir + '/' + name
    faa_path = cd_hit_out + '.faa'
    with open(faa_path, 'w') as f:
        f.write(output)

    cmd = 'cd-hit -i ' + faa_path + ' -o ' + cd_hit_out + ' -T 0 -M 0 -g 1 -s 0.8 -c 0.9'
    call(cmd.split())

    cmd = 'makeblastdb -dbtype prot -in ' + cd_hit_out
    call(cmd.split())

    cmd = 'mv ' + cd_hit_out + '.p* ' + genus_db_path
    Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)


def main():
    args = make_args()
    ftp = FtpUtils.login()

    taxa_tree = TaxonomyTree(args.outdir + '/taxonomy', ftp)
    target_taxa = set()
    for taxid in args.taxid:
        target_taxa.update(taxa_tree.get_consistent_below(str(taxid)))

    all_genomes = AssemblySummary(args.outdir, ftp)
    filtered_genomes = all_genomes.filter_genomes(target_taxa, args)

    gbffs = list()
    for line, genome in filtered_genomes.iterrows():
        dl = NcbiDownload(re.search('(/genomes.*)', genome.ftp_path).group(1),
                          args.outdir + '/' + genome['# assembly_accession'])
        dl.download(ftp, all_files=args.all_files)
        FtpUtils.calc_checksum(dl.checksum_file, dl.outdir)
        dl.unzip_gbff()
        gbffs.append(dl.gbff)

    FtpUtils.logout(ftp)

    make_database(gbffs, args.outdir + '/pre_db_files', args.db_dir, args.name)


if __name__ == '__main__':
    main()
