from io import StringIO
from unittest import TestCase
from unittest import mock

from transposcope.fasta_handler import FastaHandler
from transposcope.insertion import Insertion


class TestFastaHandler(TestCase):
    def setUp(self):
        fake_line1_fasta_file = StringIO(
            '>L1HS	L1	Homo sapiens\ngggaggaggagccaagatggccgaataggaacagctccggtctacagctcccagcgtgagcgacgcagaa',
            newline='\n')
        with mock.patch('builtins.open', return_value=fake_line1_fasta_file, create=True):
            self.fasta_handler = FastaHandler('filename', '/', 58, 71)
        fake_reference_genome_fasta_file = StringIO(
            ">FASTA_FILE\nacgttcga",
            newline='\n'
        )
        with mock.patch('builtins.open', return_value=fake_reference_genome_fasta_file, create=True):
            self.fasta_handler.set_reference_genome('ref_file')

    def test_get_reference_nucleotides_in_range(self):
        result = self.fasta_handler.get_reference_nucleotides_in_range(0, 8)
        self.assertEqual('ACGTTCGA', result)
        result = self.fasta_handler.get_reference_nucleotides_in_range(4, 8)
        self.assertEqual('TCGA', result)

    def test_get_line1_nucleotides_in_range(self):
        result = self.fasta_handler.get_line1_nucleotides_in_range(0, 8)
        self.assertEqual('GGGAGGAG', result)
        result = self.fasta_handler.get_line1_nucleotides_in_range(58, 71)
        self.assertEqual('AGCGACGCAGAA', result)

    def test_generate_fasta_sequence_not_complement(self):
        result = self.fasta_handler.generate_fasta_sequence(Insertion(None, 1, 8, 0, 2))
        self.assertEqual('AGCGACGCAGAAACGTTCGA', result)

    def test_generate_fasta_sequence_complement(self):
        result = self.fasta_handler.generate_fasta_sequence(Insertion(None, 0, 8, 6, 8))
        self.assertEqual('ACGTTCGATTCTGCGTCGCT', result)

    def test_reverse_complement(self):
        result = self.fasta_handler.reverse_complement('acgttgca')
        self.assertEqual('TGCAACGT', result)
