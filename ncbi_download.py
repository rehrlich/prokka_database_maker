from ftplib import FTP
from subprocess import call, check_output
import os


class NcbiDownload:
    def __init__(self, ftp_path, outdir):
        self.ftp_dir = ftp_path
        self.outdir = outdir
        print(self.outdir)

    @staticmethod
    def login():
        ftp = FTP("ftp.ncbi.nlm.nih.gov")
        ftp.login()
        return ftp

    @staticmethod
    def logout(ftp):
        ftp.quit()

    def download(self, ftp, all_files=True):

        ftp.cwd(self.ftp_dir)

        listing = []
        ftp.retrlines("LIST", listing.append)

        call(['mkdir', '-p', self.outdir])

        for row in listing:
            ncbi_filename = row.split(None, 8)[-1].lstrip().split(' ')[0]

            if (all_files or ncbi_filename == 'md5checksums.txt' or
                    ncbi_filename.endswith('gbff.gz')):
                if 'assembly_structure' not in ncbi_filename:

                    with open(self.outdir + '/' + ncbi_filename, "wb") as lf:
                        ftp.retrbinary("RETR " + ncbi_filename, lf.write, 8*1024)

    def calc_checksum(self):
        with open(self.outdir + '/md5checksums.txt') as f:
            for line in f:
                split_line = line.split()
                file_name = self.outdir + '/' + split_line[1][2:]
                if not os.path.isfile(file_name):
                    continue

                expected_md5 = line.split()[0]
                observed_md5 = check_output(['md5sum', file_name]).decode("utf-8").split()[0]

                if expected_md5 != observed_md5:
                    raise ValueError('MD5 checksum failed for ', file_name)

