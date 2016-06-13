from subprocess import call


class NcbiDownload:
    def __init__(self, ftp_path, outdir):
        self.ftp_dir = ftp_path
        self.outdir = outdir
        self.gbff = None
        self.checksum_file = self.outdir + '/md5checksums.txt'

    def unzip_gbff(self):
        call(['gunzip', self.gbff])
        self.gbff = self.gbff.replace('.gbff.gz', '.gbff')

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

                    local_file = self.outdir + '/' + ncbi_filename
                    with open(local_file, "wb") as lf:
                        ftp.retrbinary("RETR " + ncbi_filename, lf.write, 8*1024)

                    if local_file.endswith('.gbff.gz'):
                        self.gbff = local_file

