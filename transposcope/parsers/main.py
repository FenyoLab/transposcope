"""
File: main.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: File containing main entry point for running TranspoScope related
             scripts.
"""

import argparse
from transposcope.parsers import tipseqhunter_parser
from transposcope.parsers import melt_parser


def main(args):
    """Main entry point into TranspoScope scripts

    @param param:  Description
    @type  param:  Type

    @return:  Description
    @rtype :  Type

    @raise e:  Description
    """
    if args.type.lower() == "tipseqhunter":
        tipseqhunter_parser.main(args.path)
    elif args.type.lower() == "melt":
        melt_parser.main(args.path)
    else:
        print(
            "{} files cannot be processed. ".format(args.type)
            + "Only MELT and TIPseqHunter files can currently be parsed"
        )


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Parse TIPseqHunter or MELT output for visualization."
        + "The parsed file will have the same file name as the input file "
        + "with 'TS_' prepended to it."
    )
    # TODO read some other parsers help for pointers
    PARSER.add_argument("-s", "--source", help="The path to the source file")
    PARSER.add_argument(
        "-f", "--format", help="The input type [MELT, TIPseqHunter]"
    )
    ARGS = PARSER.parse_args()
