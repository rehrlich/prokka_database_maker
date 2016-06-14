from ftplib import FTP
from subprocess import check_output
import os


class FtpUtils:
    @staticmethod
    def login():
        ftp = FTP("ftp.ncbi.nlm.nih.gov")
        ftp.login()
        return ftp

    @staticmethod
    def logout(ftp):
        ftp.quit()

    @staticmethod
    def calc_checksum(checksum_file, local_dir):
        """
        Checks the md5 for all downloaded files from checksum_file.  Raises an
        error if any are wrong.
        :param checksum_file: local path to a checksum file from ncbi
        :param local_dir: directory containing some or all of the files listed
        in checksum_file
        """
        with open(checksum_file) as f:
            for line in f:
                split_line = line.split()
                file_name = local_dir + '/' + split_line[1][2:]
                if not os.path.isfile(file_name):
                    continue

                expected_md5 = split_line[0]
                observed_md5 = check_output(['md5sum', file_name]).decode("utf-8").split()[0]

                if expected_md5 != observed_md5:
                    raise ValueError('MD5 checksum failed for ', file_name)