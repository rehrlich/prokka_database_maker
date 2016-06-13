import pandas as pd


class AssemblySummary:
    def __init__(self, outdir, ftp):
        self.outdir = outdir
        self.summ_file = self.outdir + '/assembly_summary.txt'
        self.download_summary(ftp)
        self.genomes = pd.read_csv('refs/assembly_summary.txt',
                                   sep='\t', skiprows=1)

    def download_summary(self, ftp):
        ftp.cwd('/genomes/genbank/bacteria')

        with open(self.summ_file, "wb") as lf:
            ftp.retrbinary("RETR assembly_summary.txt", lf.write, 8*1024)

    def filter_genomes(self, target_taxa):
        filtered_genomes = self.genomes
        filtered_genomes = filtered_genomes[
            filtered_genomes['assembly_level'] == 'Complete Genome']
        filtered_genomes = filtered_genomes[
            filtered_genomes['version_status'] == 'latest']
        filtered_genomes = filtered_genomes[
            filtered_genomes['taxid'].isin(target_taxa) | filtered_genomes[
                'species_taxid'].isin(target_taxa)]
        return filtered_genomes
