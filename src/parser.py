"""
File: transposcope_parser.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: Command line parser which runs relative TranspoScope
    functions
"""

import argparse
import transposcope.transposcope as ts
import transposcope.viewer.server as server


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
    # TODO - add help for transposcope
    # TODO - set default for transposcope parser
    subparsers = parser.add_subparsers(help="ADD HELP")
    transposcope_parser = subparsers.add_parser(
        "align", help="transposcope help"
    )
    transposcope_parser.add_argument(
        "index", type=str, help="path to index file"
    )
    transposcope_parser.add_argument("bam", type=str, help="path to bam file")
    transposcope_parser.add_argument(
        "me_reference", type=str, help="path to the mobile element FASTA file"
    )
    transposcope_parser.add_argument(
        "host_reference",
        type=str,
        help="path to a folder containing all of the chromosome fasta files for the host genome",
    )
    transposcope_parser.add_argument(
        "sample_id", type=str, help="Unique name to for the given experiment"
    )
    transposcope_parser.add_argument(
        "--genes", type=str, help="path to genes file"
    )
    transposcope_parser.add_argument(
        "--group1",
        type=str,
        help="First level group tag (default: %(default)s)",
        default="ungrouped",
    )
    transposcope_parser.add_argument(
        "--group2",
        type=str,
        help="Second level group tag (default: %(default)s)",
        default="ungrouped",
    )

    transposcope_parser.add_argument(
        "--keep_files",
        type=bool,
        help="Flag which determines whether intermediate bam files and fasta files are deleted",
        default=False,
    )

    transposcope_parser.set_defaults(func=ts.main)

    viewer_parser = subparsers.add_parser("view", help="viewer help")
    viewer_parser.set_defaults(func=server.main)

    args = parser.parse_args()


if __name__ == "__main__":
    transposcope_entry()
