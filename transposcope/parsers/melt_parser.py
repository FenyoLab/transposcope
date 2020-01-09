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
import sys


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
                (meta_data[key][current_id]["Description"]) = description.group(1)
                number = re.search(r"Number=([^,]+)", value.strip("<>"))
            if number:
                meta_data[key][current_id]["Number"] = number.group(1)
            data_type = re.search(r"Type=([^,]+)", value.strip("<>"))
            if data_type:
                meta_data[key][current_id]["Type"] = data_type.group(1)
        else:
            meta_data[key] = value

    return meta_data, header


def parse_row(vcf_row, header):
    """Converts a row from the vcf file into a dictionary using the given
    header.

    @param row:  List of items from a row in the vcf file
    @type  row:  list(str)

    @param row:  List containing the column names from the vcf file
    @type  row:  list(str)

    @return:  Dictionary representing the row.
    @rtype :  dict

    @raise e:  Description
    """
    return dict(zip(header, vcf_row))


def parse_vcf_content(melt_file_handler, header):
    """return the contents of the melt vcf file as a list of loci

    @param melt_file_handler: Generator which returns single lines of the vcf
    file
    @type  melt_file_handler: Generator -> str

    @return: List of named tuples representing insertion sites
    @rtype : List(NamedTuple)

    @raise e:  None
    """
    contents = []
    for line in melt_file_handler:
        contents.append(parse_row(line.split(), header))
        contents[-1]["INFO"] = {
            x.split("=")[0]: x.split("=")[1] for x in contents[-1]["INFO"].split(";")
        }
    return contents


def _find_strand(row_info):
    name, start, end, polarity = row_info["MEINFO"].split(",")
    return name, start, end, polarity


def retrieve_required_data(extracted_vcf_data, target_width=1000):
    """Reformat the data from the vcf file into the format required by
    transposcope

    @param extracted_vcf_data:  The contents of the vcf file.
    @type  extracted_vcf_data:  list(dict(str))

    @param target_width:  The specified width of the target region.
    @type  target_width:  int

    @return:  Table containing the formated data
    @rtype :  list(list(values))

    @raise e:  Description
    """
    formated_table = []
    for row_data in extracted_vcf_data:
        # NOTE: The insertion starts at the base following POS
        name_me, start_me, end_me, strand_me = _find_strand(row_data["INFO"])
        start_me = int(start_me)
        end_me = int(end_me)

        TSD = row_data["INFO"]["TSD"]
        tsd_offset = 0
        if TSD[0] == "d":
            TSD = TSD[1:]
            tsd_offset = len(TSD)

        TSD_WIDTH = len(TSD) if TSD != "null" else 0

        asses = row_data["INFO"]["ASSESS"]

        # when undetermined the start is set to -1 which breaks offsets
        start_me = max(0, start_me)

        me_width = int(end_me) - int(start_me)

        regions = [
            {"name": "5P Insertion Site", "x": [target_width, 1], "color": "#0000FF"},
            {
                "name": "3P Insertion Site",
                "x": [target_width + me_width - 1, 1],
                "color": "#0000FF",
            },
        ]
        if TSD_WIDTH:
            regions.append(
                {
                    "name": "5P TSD",
                    "x": [target_width - TSD_WIDTH, TSD_WIDTH],
                    "color": "#48c2e0",
                }
            )
            regions.append(
                {
                    "name": "3P TSD",
                    "x": [target_width + me_width, TSD_WIDTH],
                    "color": "#48c2e0",
                },
            )
        if strand_me == "null":
            # TODO - write a better format string and use logger
            print("WARNING - strand is not specified:", row_data)
        else:
            result = [
                row_data["CHROM"],
                (
                    # tsd_offset ensures that the 5p target always ends with any TSDs
                    int(row_data["POS"]) - target_width + tsd_offset,  # 5' start
                    int(row_data["POS"]) + tsd_offset,
                ),  # 5' end
                (
                    int(row_data["POS"]) + tsd_offset,  # 3' start
                    int(row_data["POS"]) + target_width + tsd_offset,
                ),  # 3' end
                TSD_WIDTH,  # TSD
                strand_me,
                start_me,
                end_me,
                asses,
                regions,
                "melt",
                row_data["INFO"],
            ]
            formated_table.append(result)
    return formated_table


def main(filepath):
    """Convert MELT output into TranspoScope input.

    @param filepath:  Path to the MELT output file
    @type  param:  str

    @return:  None
    @rtype :  None
    """
    file_name = filepath.split("/")[-1].split(".")[0]
    file_handler = load_vcf(filepath)
    _, header = parse_meta_info(file_handler)
    insertions = parse_vcf_content(file_handler, header)
    parsed_table = retrieve_required_data(insertions)

    row_tuple = namedtuple(
        "insertion",
        [
            "chromosome",
            "target_5p",
            "target_3p",
            "window",
            "me_strand",
            "me_start",
            "me_end",
            "pred",
            "regions",
            "type",
            "info",
        ],
    )
    for row in parsed_table:
        yield row_tuple(*row)


if __name__ == "__main__":
    FILENAME = sys.argv[1] if len(sys.argv) > 1 else None
    if FILENAME:
        count = 0
        for i in main(FILENAME):
            print(i)
            count += 1
            if count == 9:
                break
