"""
File: parser.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: Command line parser which runs relative TranspoScope
    functions
"""

import argparse
import src.transposcope.transposcope as ts


def transposcope_entry():
    """Description

    @param param:  Description
    @type  param:  Type

    @return:  Description
    @rtype :  Type

    @raise e:  Description
    """
    parser = argparse.ArgumentParser(
        prog="TranspoScope",
        description="A tool for visualizing mobile elements supporting"
        + "read coverage within a genome",
    )
    parser.add_argument("index", type=str, help="path to index file")
    parser.add_argument("bam", type=str, help="path to bam file")
    parser.add_argument(
        "me_reference", type=str, help="path to the mobile element FASTA file"
    )
    parser.add_argument(
        "host_reference",
        type=str,
        help="path to a folder containing all of the chromosome fasta files for the host genome",
    )
    parser.add_argument(
        "sample_id", type=str, help="Unique name to for the given experiment"
    )
    parser.add_argument("--genes", type=str, help="path to genes file")
    parser.add_argument(
        "--group1",
        type=str,
        help="First level group tag (default: %(default)s)",
        default="ungrouped",
    )
    parser.add_argument(
        "--group2",
        type=str,
        help="Second level group tag (default: %(default)s)",
        default="ungrouped",
    )

    parser.add_argument(
        "--keep_files",
        type=bool,
        help="Flag which determines whether intermediate bam files and fasta files are deleted"
        default=False
        )

    args = parser.parse_args()
    print(args)
    #    group1,
    # group2,
    # sample_id,
    # bam_path,
    # insertion_list_path,
    # me_ref_path,
    # host_ref_path,
    ts.main(
        args.group1,
        args.group2,
        args.sample_id,
        args.bam,
        args.index,
        args.me_reference,
        args.host_reference,
        args.genes,
    )


if __name__ == "__main__":
    transposcope_entry()
