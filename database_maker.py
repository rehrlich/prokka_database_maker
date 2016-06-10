#!/usr/bin/env python3

import argparse
import os


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

    required_flags = parser.add_argument_group('Required arguments')

    required_flags.add_argument('-t', '--taxid',
                                help='The ncbi taxid for the database',
                                type=int,
                                required=True)

    return parser.parse_args()


def main():
    args = make_args()


if __name__ == '__main__':
    main()
