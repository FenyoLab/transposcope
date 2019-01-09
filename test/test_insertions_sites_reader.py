from unittest import TestCase
from unittest import mock

from src.transposcope.insertion_sites_reader import InsertionSiteReader


class TestRepredReader(TestCase):
    @mock.patch("builtins.open",
                mock.mock_open(
                    read_data='chromosome\ttarget_start\ttarget_end\t' +
                              'clip_start\tclip_end\tstrand\tlabel\tpred\t' +
                              'three_prime_end\tenzyme_cut_sites\n' +
                              'chr1\t10000\t11000\t10000\t10001\t+\t1\t1.0\t' +
                              'True\tAseI-456'
                )
                )
    def test_get_next(self):
        parser = InsertionSiteReader('test.txt')
        updater = parser.read_lines()
        update = next(updater)
        self.assertEqual('chr1', update.chromosome)
        self.assertEqual(10000, update.target_start)
        self.assertEqual(11000, update.target_end)
        self.assertEqual(10000, update.clip_start)
        self.assertEqual(10001, update.clip_end)
        self.assertEqual('+', update.strand)
        self.assertEqual(1, update.label)
        self.assertEqual(1.0, update.pred)
        self.assertEqual(True, update.three_prime_end)
        self.assertEqual('AseI-456', update.enzyme_cut_sites)
