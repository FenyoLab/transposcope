from collections import defaultdict
from functools import reduce

import logging
import pysam


# pysam.AlignedSegment.is
class BamHandler:
    def __init__(self, bam_file_location):
        self.BAM_FILE = pysam.AlignmentFile(bam_file_location, 'rb')
        self.num_reads_in_bam = reduce(lambda x, y: x + y,
               [int(l.split('\t')[2]) + int(l.split('\t')[3]) if l.split('\t')[0] != '*' else 0 for l
                in
                pysam.idxstats(bam_file_location).strip().split('\n')])

    def fetch_reads_in_region(self, insertion):
        reads = defaultdict(list)
        for read in self.BAM_FILE.fetch(reference=insertion.CHROMOSOME, start=insertion.START,
                                        end=insertion.END):
            reads[read.query_name].insert(read.is_read2, read)
        return dict(reads)

    def all_reads(self):
        completed = 0
        ten_percent = self.num_reads_in_bam/10
        next_log = ten_percent
        for read in self.BAM_FILE.fetch():
            yield read
            completed += 1
            if completed > next_log:
                logging.info('Percentage of BAM file processed: {:.2%}.'.format(next_log/self.num_reads_in_bam))
                next_log += ten_percent
