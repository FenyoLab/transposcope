"""
File: insertion_sites_reader.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: Script to process insertion site information from a tab
             separated file
"""

from collections import namedtuple


class InsertionSiteReader:
    """
        Defines methods required for reading insertion site information
        from a tab delimeted file.
        These files must contain a header and the columns should be listed
        in the correct order.
    """

    def __init__(self, insertion_sites_file_path, header=None):
        """
        Constructor

        :param insertion_sites_file_path:
        :param header:
        """
        if header is None:
            header = {
                "strings": ["chromosome", "enzyme_cut_sites", "strand"],
                "ints": [
                    "target_start",
                    "target_end",
                    "clip_start",
                    "clip_end",
                    "me_start",
                    "me_end",
                ],
                "floats": ["pred"],
                "bools": ["three_prime_end"],
            }
        self.insertion_sites_file = open(insertion_sites_file_path, "r")
        self.header = header
        self.all_headers = (
            self.insertion_sites_file.readline().strip().split("\t")
        )
        if not self.valid_header():
            raise SystemExit(
                "\n\nERROR: Insertion sites file '{}' does not contain a valid header".format(
                    insertion_sites_file_path
                )
            )
        self.insertion_line = namedtuple("insertion_line", self.all_headers)

    def valid_header(self) -> bool:
        """Description

        :param path:  The path to the input file
        :type  path  str

        :return:  Whether the file is potentially valid or not
        :rtype :  bool

        """
        if self.all_headers[0] != "chromosome":
            return False
        return True

    def __parse_line(self, line):
        line = line.strip().split("\t")
        line = dict(zip(self.all_headers, line))
        needed_values_from_file = line
        for string in self.header["strings"]:
            needed_values_from_file[string] = line[string]
        for integer in self.header["ints"]:
            needed_values_from_file[integer] = int(line[integer])
        for floating_point in self.header["floats"]:
            needed_values_from_file[floating_point] = float(
                line[floating_point]
            )
        for boolean in self.header["bools"]:
            needed_values_from_file[boolean] = line[boolean] == "True"
        return needed_values_from_file

    def read_lines(self):
        """
        Iterator which returns the next line of the file as a named tuple

        :rtype: named_tuple(
            H1_ClipChr,
            H2_ClipS,
            H3_ClipE,
            H6_TargS,
            H7_TargE,
            H31_pred
        )
        """
        for line in self.insertion_sites_file.readlines():
            if line.strip():
                line = self.__parse_line(line)
                line_with_header = self.insertion_line(**line)
                yield line_with_header
