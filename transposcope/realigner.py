import os
import subprocess


class Realigner:
    def __init__(self, output_path, visualization_path):
        self.output_path = output_path
        self.visualization_path = visualization_path
        # TODO: Move all this to initialize.py
        if not os.path.exists(os.path.join(self.output_path, "fasta_indexed")):
            os.makedirs(os.path.join(self.output_path, "fasta_indexed"))
        if not os.path.exists(os.path.join(self.output_path, "bam")):
            os.makedirs(os.path.join(self.output_path, "bam"))
        if not os.path.exists(os.path.join(self.visualization_path, "cram")):
            os.makedirs(os.path.join(self.visualization_path, "cram"))
        if not os.path.exists(os.path.join(self.output_path, "bam_sorted")):
            os.makedirs(os.path.join(self.output_path, "bam_sorted"))
        if not os.path.exists(os.path.join(self.output_path, "logs")):
            os.makedirs(os.path.join(self.output_path, "logs"))

        self.al_out = open(
            os.path.join(self.output_path, "logs", "alignment.output.log"), "w"
        )
        self.al_err = open(
            os.path.join(self.output_path, "logs", "alignment.error.log"), "w"
        )

    def realign(self, fasta_file_path, fastq1_path, fastq2_path, file_name):
        cmd = ["samtools", "faidx", fasta_file_path]

        # Python 3.4
        subprocess.call(cmd, stdout=self.al_out, stderr=self.al_err)

        indexed_fa_path = os.path.join(
            self.output_path, "fasta_indexed", file_name + ".indexed.fasta"
        )

        cmd = ["bowtie2-build", fasta_file_path, indexed_fa_path]

        # Python 3.4
        subprocess.call(cmd, stdout=self.al_out, stderr=self.al_err)

        sam_path = os.path.join(
            self.output_path, os.path.join("sam", file_name + ".sam")
        )

        cmd = [
            "bowtie2",
            "-X",
            "1000",
            "--local",
            "--phred33",
            "--sensitive",
            "-p",
            " 6",
            "-x",
            indexed_fa_path,
            "-1",
            fastq1_path,
            "-2",
            fastq2_path,
            "-S",
            sam_path,
        ]

        # Python 3.4
        subprocess.call(cmd, stdout=self.al_out, stderr=self.al_err)

        bam_path = os.path.join(
            self.output_path, os.path.join("bam", file_name + ".bam")
        )

        cmd = ["samtools", "view", "-b", "-o", bam_path, sam_path]

        # Python 3.4
        subprocess.call(cmd, stdout=self.al_out, stderr=self.al_err)
        # Python 3.5
        # p = subprocess.run(cmd, stdout=al_out, stderr=al_err)
        # p.check_returncode()  # change this to log errors

        bam_sorted_path = os.path.join(
            self.output_path, os.path.join("bam_sorted", file_name + ".sort.bam"),
        )

        cmd = ["samtools", "sort", "-o", bam_sorted_path, bam_path]

        # Python 3.4
        subprocess.call(cmd, stdout=self.al_out, stderr=self.al_err)

        bai_path = os.path.join(
            self.output_path, os.path.join("bam_sorted", file_name + ".sort.bam.bai"),
        )

        cmd = ["samtools", "index", bam_sorted_path, bai_path]

        # Python 3.4
        subprocess.call(cmd, stdout=self.al_out, stderr=self.al_err)

        cram_path = os.path.join(
            self.visualization_path, os.path.join("cram", file_name + ".cram")
        )
        cmd = [
            "samtools",
            "view",
            "-T",
            fasta_file_path,
            "-C",
            "-o",
            cram_path,
            bam_sorted_path,
        ]

        subprocess.call(cmd, stdout=self.al_out, stderr=self.al_err)

        cmd = ["samtools", "index", cram_path]

        subprocess.call(cmd, stdout=self.al_out, stderr=self.al_err)

        # dir_path = [
        #     os.path.join(self.output_path, 'fastq'),
        #     os.path.join(self.output_path, 'bam'),
        #     os.path.join(self.output_path, 'sam'),
        #     os.path.join(self.output_path, 'fasta_indexed')]
        # for cur_path in dir_path:
        #     file_list = os.listdir(cur_path)
        #     for fileName in file_list:
        #         os.remove(cur_path + "/" + fileName)
