from io import StringIO
from unittest import TestCase
from unittest import mock

from src.transposcope.fasta_handler import FastaHandler
from src.transposcope.insertion import Insertion


class TestFastaHandler(TestCase):
    def setUp(self):
        fake_line1_fasta_file = StringIO(
            ">TEST REFERENCE\n" + "TTTTAAAATTTTAAAA", newline="\n"
        )
        with mock.patch(
            "builtins.open", return_value=fake_line1_fasta_file, create=True
        ):
            self.fasta_handler = FastaHandler("filename", "/")
        fake_reference_genome_fasta_file = StringIO(
            ">FASTA_FILE\nGGGGCCCCGGGGCCCC", newline="\n"
        )
        with mock.patch(
            "builtins.open",
            return_value=fake_reference_genome_fasta_file,
            create=True,
        ):
            self.fasta_handler.set_reference_genome("test")

    def test_get_reference_nucleotides_in_range(self):
        result = self.fasta_handler.get_reference_nucleotides_in_range(0, 8)
        self.assertEqual("GGGGCCCC", result)
        result = self.fasta_handler.get_reference_nucleotides_in_range(4, 8)
        self.assertEqual("CCCC", result)

    def test_get_line1_nucleotides_in_range(self):
        result = self.fasta_handler.get_line1_nucleotides_in_range(0, 8)
        self.assertEqual("TTTTAAAA", result)
        result = self.fasta_handler.get_line1_nucleotides_in_range(2, 10)
        self.assertEqual("TTAAAATT", result)

    def test_generate_fasta_sequence_not_complement(self):
        result = self.fasta_handler.generate_fasta_sequence(
            Insertion(None, 1, 8, 1, 2, "+", 1, 1, 8, True)
        )
        self.assertEqual("TTTTAAAAGGGGCCCC", result)

    def test_generate_fasta_sequence_complement(self):
        result = self.fasta_handler.generate_fasta_sequence(
            Insertion(None, 1, 8, 6, 8, "-", 1, 1, 8, True)
        )
        self.assertEqual("GGGGCCCCTTTTAAAA", result)

    def test_generate_fasta_sequence_5prime_not_complement(self):
        result = self.fasta_handler.generate_fasta_sequence(
            Insertion(None, 1, 8, 6, 8, "+", 1, 1, 8, False)
        )
        self.assertEqual("GGGGCCCCTTTTAAAA", result)

    def test_generate_fasta_sequence_5prime_complement(self):
        result = self.fasta_handler.generate_fasta_sequence(
            Insertion(None, 1, 8, 1, 2, "-", 1, 1, 8, False)
        )
        self.assertEqual("TTTTAAAAGGGGCCCC", result)

    def test_reverse_complement(self):
        result = self.fasta_handler.reverse_complement("acgttgca")
        self.assertEqual("TGCAACGT", result)

        # chromosome=None,
        # target_start=None,
        # target_end=None,
        # clip_start=None,
        # clip_end=None,
        # strand=None,
        # pred=None,
        # me_start=None,
        # me_end=None,
        # three_prime_end=None,
