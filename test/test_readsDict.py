from collections import namedtuple
from unittest import TestCase

from transposcope_pkg.reads_dict import ReadsDict

Read = namedtuple("Read", ["query_name", "is_read1", "is_read2", "flag"])


class TestReadsDict(TestCase):
    def test_incremental_add(self):
        reads_dict = ReadsDict()
        reads_dict += {"a": 1}
        reads_dict += {"b": 2, "c": 3, "d": 4}
        self.assertDictEqual(reads_dict, {"a": 1, "b": 2, "c": 3, "d": 4})

    def test_reads_from_key_list(self):
        reads_dict = ReadsDict()
        reads_dict += {"a": 1, "b": 2, "c": 3, "d": 4}
        iterator = reads_dict.reads_from_key_list(["b", "d"])
        self.assertEqual(next(iterator), 2)
        self.assertEqual(next(iterator), 4)

    def test_insert_read2_with_read1_present(self):
        reads_dict = ReadsDict({"a": [Read("a", False, True, 0)]})
        result = reads_dict.insert(Read("a", True, False, 0))
        self.assertIs(result, 0)
        self.assertTrue(reads_dict["a"][0].is_read1)
        self.assertTrue(reads_dict["a"][1].is_read2)

    def test_insert_read1_with_read2_present(self):
        reads_dict = ReadsDict({"a": [Read("a", True, False, 0)]})
        result = reads_dict.insert(Read("a", False, True, 0))
        self.assertIs(result, 0)
        self.assertTrue(reads_dict["a"][0].is_read1)
        self.assertTrue(reads_dict["a"][1].is_read2)

    def test_insert_read1_with_both_reads_present(self):
        reads_dict = ReadsDict(
            {"a": [Read("a", False, True, 0), Read("a", True, False, 0)]}
        )
        result = reads_dict.insert(Read("a", True, False, 0))
        self.assertIs(result, -1)

    def test_insert_read2_with_both_reads_present(self):
        reads_dict = ReadsDict(
            {"a": [Read("a", False, True, 0), Read("a", True, False, 0)]}
        )
        result = reads_dict.insert(Read("a", False, True, 0))
        self.assertIs(result, -1)

    def test_insert_read1_with_empty_list(self):
        reads_dict = ReadsDict({"a": []})
        self.assertRaises(
            ValueError, reads_dict.insert, Read("a", True, False, 0)
        )
