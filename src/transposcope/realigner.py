import os
import subprocess


class Realigner:
    def __init__(
        self, output_path, bowtie_index_fasta_script, bowtie_realign_script
    ):
        self.output_path = output_path
        self.fa_index_script = bowtie_index_fasta_script
        self.realign_script = bowtie_realign_script
        if not os.path.exists(os.path.join(self.output_path, "fasta_indexed")):
            os.makedirs(os.path.join(self.output_path, "fasta_indexed"))
        if not os.path.exists(os.path.join(self.output_path, "bam")):
            os.makedirs(os.path.join(self.output_path, "bam"))
        if not os.path.exists(os.path.join(self.output_path, "bam_sorted")):
            os.makedirs(os.path.join(self.output_path, "bam_sorted"))
        if not os.path.exists(os.path.join(self.output_path, "bowtie")):
            os.makedirs(os.path.join(self.output_path, "bowtie"))

        self.BTOUT = open(
            os.path.join(self.output_path, "bowtie", "bt2.output.log"), "w"
        )
        self.BTERR = open(
            os.path.join(self.output_path, "bowtie", "bt2.error.log"), "w"
        )

    def realign(self, fasta_file_path, fastq1_path, fastq2_path, file_name):
        cmd = ["samtools", "faidx", fasta_file_path]

        # Python 3.4
        subprocess.call(cmd, stdout=self.BTOUT, stderr=self.BTERR)

        indexed_fa_path = os.path.join(
            self.output_path, "fasta_indexed", file_name + ".indexed.fasta"
        )

        cmd = [
            os.path.join(
                os.getcwd(), "shell_scripts/runBowtie2v223BuildIndex.sh"
            ),
            fasta_file_path,
            indexed_fa_path,
        ]

        # Python 3.4
        subprocess.call(cmd, stdout=self.BTOUT, stderr=self.BTERR)

        sam_path = os.path.join(
            self.output_path, os.path.join("sam", file_name + ".sam")
        )

        cmd = [
            os.path.join(os.getcwd(), "shell_scripts/runBowtie2v223PE.sh"),
            indexed_fa_path,
            fastq1_path,
            fastq2_path,
            sam_path,
            "2",
            "1000",
            "FALSE",
        ]

        # Python 3.4
        subprocess.call(cmd, stdout=self.BTOUT, stderr=self.BTERR)

        bam_path = os.path.join(
            self.output_path, os.path.join("bam", file_name + ".bam")
        )

        cmd = ["samtools", "view", "-b", "-o", bam_path, sam_path]

        # Python 3.4
        subprocess.call(cmd, stdout=self.BTOUT, stderr=self.BTERR)
        # Python 3.5
        # p = subprocess.run(cmd, stdout=BTOUT, stderr=BTERR)
        # p.check_returncode()  # change this to log errors

        bam_sorted_path = os.path.join(
            self.output_path,
            os.path.join("bam_sorted", file_name + ".sort.bam"),
        )

        cmd = ["samtools", "sort", "-o", bam_sorted_path, bam_path]

        # Python 3.4
        subprocess.call(cmd, stdout=self.BTOUT, stderr=self.BTERR)

        bai_path = os.path.join(
            self.output_path,
            os.path.join("bam_sorted", file_name + ".sort.bam.bai"),
        )

        cmd = ["samtools", "index", bam_sorted_path, bai_path]

        # Python 3.4
        subprocess.call(cmd, stdout=self.BTOUT, stderr=self.BTERR)

        # dir_path = [
        #     os.path.join(self.output_path, 'fastq'),
        #     os.path.join(self.output_path, 'bam'),
        #     os.path.join(self.output_path, 'sam'),
        #     os.path.join(self.output_path, 'fasta_indexed')]
        # for cur_path in dir_path:
        #     file_list = os.listdir(cur_path)
        #     for fileName in file_list:
        #         os.remove(cur_path + "/" + fileName)

        return bam_sorted_path
