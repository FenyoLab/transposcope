"""
File: melt_parser.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/yourname
Description: Parser which extracts relavant data from MELT vcf files and
             outputs a tab delimited file usable by TranspoScope.
"""

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
            x.split("=")[0]: x.split("=")[1]
            for x in contents[-1]["INFO"].split(";")
        }
    return contents


def _find_strand(row_info):
    name, start, end, polarity = row_info["MEINFO"].split(",")
    return name, start, end, polarity


# TODO : rename this method
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
    formated_table = [
        [
            "chromosome",
            "target_start",
            "target_end",
            "clip_start",
            "clip_end",
            "strand",
            "pred",
            "three_prime_end",
            "enzyme_cut_sites",
            "me_start",
            "me_end",
        ]
    ]
    for row_data in extracted_vcf_data:
        name_me, start_me, end_me, strand_me = _find_strand(row_data["INFO"])
        if strand_me == "null":
            # TODO - write a better format string
            print("WARNING - strand is not specified:", row_data)
        else:
            result_1 = [
                row_data["CHROM"],
                int(row_data["POS"]) - target_width,
                int(row_data["POS"]),
                int(row_data["POS"]),
                int(row_data["POS"]),
                strand_me,
                1.0,
                strand_me == "-",
                "",
                int(start_me),
                int(end_me),
            ]
            formated_table.append(result_1)
            result_2 = [
                row_data["CHROM"],
                int(row_data["POS"]),
                int(row_data["POS"]) + target_width,
                int(row_data["POS"]),
                int(row_data["POS"]),
                strand_me,
                1.0,
                strand_me == "+",
                "",
                int(start_me),
                int(end_me),
            ]
            formated_table.append(result_2)
    return formated_table


def main(filepath):
    file_name = filepath.split("/")[-1].split(".")[0]
    file_handler = load_vcf(filepath)
    _, header = parse_meta_info(file_handler)
    insertions = parse_vcf_content(file_handler, header)
    parsed_table = retrieve_required_data(insertions)
    with open("output/insertion_tables/{}.tab".format(file_name), "w") as file:
        for row in parsed_table:
            file.write("\t".join([str(x) for x in list(row)]) + "\n")


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    if filename:
        main(filename)
