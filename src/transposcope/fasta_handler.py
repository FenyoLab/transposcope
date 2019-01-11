import logging
import os

from Bio.SeqIO.FastaIO import SimpleFastaParser


class FastaHandler:
    def __init__(
        self,
        line1_reference_path,
        reference_genome_folder_path,
        line1_start,
        line1_end,
    ):
        self.LINE1_START = int(line1_start)
        self.LINE1_END = int(line1_end)
        self._reference_genome_seq = None
        self._reference_genome_folder_path = reference_genome_folder_path
        self._current_chromosome = None
        with open(line1_reference_path, "rU") as handle:
            self._LINE1_REFERENCE_SEQ = next(SimpleFastaParser(handle))[
                1
            ].upper()

    def set_reference_genome(self, reference_genome_chromosome):
        logging.info(
            "changing reference genome to {}".format(
                reference_genome_chromosome
            )
        )
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
            start = self.LINE1_START
            end = self.LINE1_END
        if start < 0 or end < 0:
            raise ValueError("start and end positions must be positive")
        return self._LINE1_REFERENCE_SEQ[start:end]

    def generate_fasta_sequence(self, insertion):
        reference_genome_sequence = self.get_reference_nucleotides_in_range(
            insertion.START, insertion.END, insertion.CHROMOSOME
        )
        line_1_sequence = self.get_line1_nucleotides_in_range(
            self.LINE1_START, self.LINE1_END
        )
        insertion.GENOME_SEQUENCE = reference_genome_sequence
        insertion.LINE1_SEQUENCE = self.get_line1_nucleotides_in_range(
            self.LINE1_START, self.LINE1_END
        )
        if insertion.COMPLEMENT:
            line_1_sequence = self.reverse_complement(line_1_sequence)
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
