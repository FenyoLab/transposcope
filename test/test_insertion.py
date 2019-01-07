from unittest import TestCase

from src.transposcope.insertion import Insertion


class TestInsertion(TestCase):

    def test_calculate_if_insertion_is_complement_true(self):
        test_insertion = Insertion('chr1', 1, 100, 95, 100, 1)
        self.assertTrue(test_insertion.COMPLEMENT)

    def test_calculate_if_insertion_is_complement_false(self):
        test_insertion = Insertion('chr1', 1, 100, 1, 10, 1)
        self.assertFalse(test_insertion.COMPLEMENT)


