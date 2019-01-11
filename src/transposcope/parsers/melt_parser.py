"""
File: melt_parser.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/yourname
Description: Parser which extracts relavant data from MELT vcf files and
             outputs a tab delimited file usable by TranspoScope.
"""

from collections import namedtuple
import os
import re


def load_vcf(file_path):
    """Create a generator which serves up the file one line at a time.
    @param file_path: Path to the file to be iterated over
    @type  file_path: str
    @return: Generator which provides the file one line at a time
    @rtype : Generator
    """
    with open(file_path, "r") as file_handle:
        for line in file_handle.readlines():
            yield line.strip()


def parse_meta_info(melt_file_handler):
    """Extract meta data and header from the top of a MELT vcf file.
   Meta data rows start with ## and the header starts with a singe #.

    @param param:  melt_file_handler
    @type  param:  Generator which returns a line of the melt file at a time.

    @return:  Description
    @rtype :  Type

    @raise e:  Description
    """
    header = None
    meta_data = {}
    for line in melt_file_handler:
        if not line.startswith("##"):
            header = line[1:].split()
            break
        key, value = line[2:].split("=", 1)
        if key not in meta_data:
            meta_data[key] = {}
        if value.startswith("<"):
            data = re.search(r"ID=([^,]+)", value.strip("<>"))
            current_id = data.group(1)
            meta_data[key][current_id] = {}
            chrom_length = re.search(r"length=([^,]+)", value.strip("<>"))
            if chrom_length:
                meta_data[key][current_id]["length"] = chrom_length.group(1)
            description = re.search(r'Description="([^"]+)', value.strip("<>"))
            if description:
                (
                    meta_data[key][current_id]["Description"]
                ) = description.group(1)
                number = re.search(r"Number=([^,]+)", value.strip("<>"))
            if number:
                meta_data[key][current_id]["Number"] = number.group(1)
            data_type = re.search(r"Type=([^,]+)", value.strip("<>"))
            if data_type:
                meta_data[key][current_id]["Type"] = data_type.group(1)
        else:
            meta_data[key] = value

    return meta_data, header


def parse_vcf_content(melt_file_handler, header):
    """return the contents of the melt vcf file as a list of loci

    @param melt_file_handler: Generator which returns single lines of the vcf
    file
    @type  melt_file_handler: Generator -> str

    @return: List of named tuples representing insertion sites
    @rtype : List(NamedTuple)

    @raise e:  None
    """
    insertion = namedtuple("Insertion", header)
    contents = []
    for line in melt_file_handler:
        print(insertion(line.split()))
    return contents


if __name__ in "__main__":
    print(os.getcwd())
    for row in load_vcf("./test/parsers/examples/melt.vcf"):
        print(row)
