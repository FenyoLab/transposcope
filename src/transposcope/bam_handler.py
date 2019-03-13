import logging
from collections import defaultdict
from functools import reduce

import pysam
import os


class BamHandler:
    def __init__(self, bam_file_location):
        if not os.path.exists(bam_file_location):
            raise SystemExit(
                "\n\nERROR: BAM file not found '{}'".format(bam_file_location)
            )
        self.BAM_FILE = pysam.AlignmentFile(bam_file_location, "rb")
        self.num_reads_in_bam = reduce(
            lambda x, y: x + y,
            [
                int(l.split("\t")[2]) + int(l.split("\t")[3])
                if l.split("\t")[0] != "*"
                else 0
                for l in pysam.idxstats(bam_file_location).strip().split("\n")
            ],
        )

    def fetch_reads_in_region(self, insertion):
        reads = defaultdict(list)
        for read in self.BAM_FILE.fetch(
            reference=insertion.CHROMOSOME,
            start=insertion.START,
            end=insertion.END,
        ):
            if not read.flag & (0x800 | 0x100):
                reads[read.query_name].insert(read.is_read2, read)
        return dict(reads)

    def all_reads(self):
        completed = 0
        ten_percent = self.num_reads_in_bam / 10
        next_log = ten_percent
        for read in self.BAM_FILE.fetch():
            yield read
            completed += 1
            if completed > next_log:
                logging.info(
                    "   - Percentage of BAM file processed: {:.2%}.".format(
                        completed / self.num_reads_in_bam
                    )
                )
                next_log += ten_percent
