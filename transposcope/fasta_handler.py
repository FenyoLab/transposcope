import logging
import os

from Bio.SeqIO.FastaIO import SimpleFastaParser


class FastaHandler:
    def __init__(self, me_reference_path, reference_genome_folder_path):
        self._reference_genome_seq = None
        self._reference_genome_folder_path = reference_genome_folder_path
        self._current_chromosome = None
        with open(me_reference_path, "rU") as handle:
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

        return (
            insertion.five_prime_sequence
            + insertion.me_sequence
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
