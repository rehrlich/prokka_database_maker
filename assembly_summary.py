import pandas as pd


class AssemblySummary:
    def __init__(self, outdir, ftp):
        """
        Downloads the bacteria assembly summary file and stores it as a pandas
        dataframe.
        :param outdir: directory to save the downloaded file
        :param ftp: an ftp connectioin to ncbi
        """
        self.outdir = outdir
        self.summ_file = self.outdir + '/assembly_summary.txt'
        self.download_summary_file(ftp)
        self.genomes = pd.read_csv(self.summ_file,
                                   sep='\t', skiprows=1)

    def download_summary_file(self, ftp):
        """
        :param ftp: an ftp connectioin to ncbi
        """
        ftp.cwd('/genomes/genbank/bacteria')

        with open(self.summ_file, "wb") as lf:
            ftp.retrbinary("RETR assembly_summary.txt", lf.write, 8 * 1024)

    def filter_genomes(self, target_taxa, args):
        """
        Filters the assembly summary dataframe for complete genomes that are the
        latest version for a strain and have a taxonomy id in target_taxa.
        :param target_taxa: a set of strings of ncbi taxonomy id numbers
        :return: the filtered dataframe
        """
        filtered_genomes = self.genomes.copy()
        if not args.include_incomplete:
            filtered_genomes = filtered_genomes[
                filtered_genomes['assembly_level'] == 'Complete Genome']

        filtered_genomes = filtered_genomes[
            filtered_genomes['version_status'] == 'latest']
        filtered_genomes = filtered_genomes[
            filtered_genomes['taxid'].isin(target_taxa) | filtered_genomes[
                'species_taxid'].isin(target_taxa)]
        return filtered_genomes
