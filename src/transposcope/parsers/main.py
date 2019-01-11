"""
File: main.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: File containing main entry point for running TranspoScope related
             scripts.
"""

import argparse


def main():
    """Main entry point into TranspoScope scripts

    @param param:  Description
    @type  param:  Type

    @return:  Description
    @rtype :  Type

    @raise e:  Description
    """


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Parse TIPseqHunter or MELT output for visualization"
    )
    # TODO read some other parsers help for pointers
    PARSER.add_argument("-s", "--source", help="The path to the source file")
    PARSER.add_argument(
        "-f", "--format", help="The input type [MELT, TIPseqHunter]"
    )
    ARGS = PARSER.parse_args()
