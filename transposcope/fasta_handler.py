import logging
import os

from Bio.SeqIO.FastaIO import SimpleFastaParser


class FastaHandler:
    def __init__(self, me_reference_path, reference_genome_folder_path):
        self._reference_genome_seq = None
        self._reference_genome_folder_path = reference_genome_folder_path
        self._current_chromosome = None
        with open(me_reference_path, "r") as handle:
            self._ME_REFERENCE_SEQ = next(SimpleFastaParser(handle))[1].upper()

    def set_reference_genome(self, reference_genome_chromosome):
        file_path = os.path.join(
            self._reference_genome_folder_path, reference_genome_chromosome + ".fa"
        )
        with open(file_path, "r") as handle:
            parser = SimpleFastaParser(handle)
            self._reference_genome_seq = next(parser)[1].upper()

    def get_reference_nucleotides_in_range(self, start=None, end=None, chromosome=None):
        if start < 0 or end < 0:
            raise ValueError("start and end positions must be positive")
        if chromosome != self._current_chromosome:
            self.set_reference_genome(chromosome)
            self._current_chromosome = chromosome
        return self._reference_genome_seq[start:end]

    def get_me_nucleotides_in_range(self, start=None, end=None):
        if start is None and end is None:
            logging.error("The insertion should define the element start/end")
        if end < 0:
            raise ValueError("end positions must be positive")
        if start < 0:
            start = 0
        return self._ME_REFERENCE_SEQ[start:end]

    def generate_fasta_sequence(self, insertion):
        if insertion.five_prime_target:
            insertion.five_prime_sequence = self.get_reference_nucleotides_in_range(
                insertion.five_prime_target[0],
                insertion.five_prime_target[1],
                insertion.chromosome,
            )

        if insertion.three_prime_target:
            insertion.three_prime_sequence = self.get_reference_nucleotides_in_range(
                insertion.three_prime_target[0],
                insertion.three_prime_target[1],
                insertion.chromosome,
            )

        me_sequence = self.get_me_nucleotides_in_range(
            insertion.me_start, insertion.me_end
        )
        if insertion.strand == "-":
            me_sequence = self.reverse_complement(me_sequence)

        insertion.me_sequence = me_sequence

        if insertion.insertion_window and insertion.type == "melt":
            insertion.three_prime_sequence = (
                insertion.five_prime_sequence[-insertion.insertion_window :]
                + insertion.three_prime_sequence
            )

        return (
            insertion.five_prime_sequence
            + insertion.me_sequence.lower()
            + insertion.three_prime_sequence
        )

    @staticmethod
    def reverse_complement(sequence):
        complement_sequence = "".join(
            [
                {"A": "T", "C": "G", "G": "C", "T": "A", "N": "N"}[x]
                for x in sequence.upper()
            ]
        )
        reverse_complement_sequence = complement_sequence[::-1]
        return reverse_complement_sequence


if __name__ == "__main__":
    import sys
    from collections import namedtuple
    from insertion import Insertion

    ME, GE = sys.argv[1:3] if len(sys.argv) > 1 else None
    RowTuple = namedtuple(
        "insertion",
        [
            "chromosome",
            "target_5p",
            "target_3p",
            "window",
            "me_strand",
            "me_start",
            "me_end",
            "pred",
            "region",
            "type",
            "info",
        ],
    )
    if ME and GE:
        FA = FastaHandler(ME, GE)
        print(
            FA.get_reference_nucleotides_in_range(112636606, 112636616, "chr1"),
            " | ",
            FA.get_reference_nucleotides_in_range(112636616, 112636626, "chr1"),
        )
        print(FA.get_reference_nucleotides_in_range(112636606, 112636626, "chr1"))
        INSERTION = RowTuple(
            chromosome="chr1",
            target_5p=(112635616, 112636616),
            target_3p=(112636616, 112637616),
            window=18,
            me_strand="-",
            me_start=4427,
            me_end=6019,
            pred="5",
            region=[],
            type="melt",
            info={
                "TSD": "AAATAGGGACAGTTTTTT",
                "ASSESS": "5",
                "INTERNAL": "NM_006135,INTRONIC",
                "SVTYPE": "LINE1",
                "SVLEN": "1592",
                "MEINFO": "L1Ta,4427,6019,-",
                "DIFF": "0.16:n1-4426,n5021-5395,t5418a,n5421,t5422a,n5425-5425,n5438-5439,c5443a,n5447,n5449,n5451,n5454,n5456,t5535g,g5538c,n5628,n5659,n5661,n5666,n5668,n5673-5678,n5685,n5687,n5689-5691,n5693,n5701,n5703-5704,n5706-5707,c5709a,n5711,n5713,c5715a,n5718,n5722-5723,g5724a,n5726-5726,n5728,n5730,n5740,n5752,t5753a,n5789-5789,t5808a,a6006g",
                "LP": "10",
                "RP": "21",
                "RA": "-1.07",
                "ISTP": "0",
                "PRIOR": "false",
                "SR": "27",
            },
        )
        INSERTION = Insertion(INSERTION)
        print(FA.generate_fasta_sequence(INSERTION))
