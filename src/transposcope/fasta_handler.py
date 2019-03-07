import logging
import os

from Bio.SeqIO.FastaIO import SimpleFastaParser


class FastaHandler:
    def __init__(self, line1_reference_path, reference_genome_folder_path):
        # self.LINE1_START = int(line1_start)
        # self.LINE1_END = int(line1_end)
        self._reference_genome_seq = None
        self._reference_genome_folder_path = reference_genome_folder_path
        self._current_chromosome = None
        with open(line1_reference_path, "rU") as handle:
            self._LINE1_REFERENCE_SEQ = next(SimpleFastaParser(handle))[
                1
            ].upper()

    def set_reference_genome(self, reference_genome_chromosome):
        file_path = os.path.join(
            self._reference_genome_folder_path,
            reference_genome_chromosome + ".fa",
        )
        with open(file_path, "r") as handle:
            parser = SimpleFastaParser(handle)
            self._reference_genome_seq = next(parser)[1].upper()

    def get_reference_nucleotides_in_range(
        self, start=None, end=None, chromosome=None
    ):
        if start < 0 or end < 0:
            raise ValueError("start and end positions must be positive")
        if chromosome != self._current_chromosome:
            self.set_reference_genome(chromosome)
            self._current_chromosome = chromosome
        return self._reference_genome_seq[start:end]

    def get_line1_nucleotides_in_range(self, start=None, end=None):
        if start is None and end is None:
            logging.error("The insertion should define the element start/end")
        if end < 0:
            raise ValueError("end positions must be positive")
        if start < 0:
            start = 0
        return self._LINE1_REFERENCE_SEQ[start:end]

    def generate_fasta_sequence(self, insertion):
        reference_genome_sequence = self.get_reference_nucleotides_in_range(
            insertion.START, insertion.END, insertion.CHROMOSOME
        )
        line_1_sequence = self.get_line1_nucleotides_in_range(
            insertion.LINE1_START, insertion.LINE1_END
        )
        insertion.GENOME_SEQUENCE = reference_genome_sequence
        if insertion.ME_IS_COMPLEMENT:
            line_1_sequence = self.reverse_complement(line_1_sequence)

        insertion.LINE1_SEQUENCE = line_1_sequence

        if (insertion.THREE_PRIME and insertion.ME_IS_COMPLEMENT) or (
            not insertion.THREE_PRIME and not insertion.ME_IS_COMPLEMENT
        ):
            return reference_genome_sequence + line_1_sequence

        else:
            return line_1_sequence + reference_genome_sequence

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
