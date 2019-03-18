from unittest import TestCase

from transposcope_pkg.insertion import Insertion


class TestInsertion(TestCase):
    def test_calculate_if_insertion_is_complement_true(self):
        test_insertion = Insertion(None, 1, 8, 6, 8, "-", 1, 1, 8, False)
        self.assertTrue(test_insertion.ME_IS_COMPLEMENT)

    def test_calculate_if_insertion_is_complement_false(self):
        test_insertion = Insertion(None, 1, 8, 6, 8, "+", 1, 1, 8, False)
        self.assertFalse(test_insertion.ME_IS_COMPLEMENT)
