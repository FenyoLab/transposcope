"""
File: tipseqhunter_parser.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: A parser which converts TIPseqHunter REPRED files into
            the tab delimited format required for TranspoScope
"""

import os
import sys

import pandas as pd


def calculate_orientation(
    index: int,
    clip_start: int,
    clip_end: int,
    target_start: int,
    target_end: int,
) -> str:
    """
    Calculate the orientation of the insertion. The clip start and end should
    be on either the left or the right of the target region depending on the
    strand.

    Ambiguous cases where the clipping center falls in the center of the target
    region are treated as being on the positive strand.


    :param index: The current row index
    :param clip_start: The potential start position of the insertion site
    :param clip_end: The potential end position of the insertion site
    :param target_start: The start position which matches the reference genome
    :param target_end: The end position which matches the reference genome
    :return:
    """
    clip_center = (clip_start + clip_end) / 2
    target_center = (target_start + target_end) / 2
    if clip_center <= target_center:
        return "+"
    if clip_center > target_center:
        return "-"
    raise ValueError(
        "Repred orientation cannot be determined in row {}".format(index)
    )


def load_repred(filepath: str) -> pd.DataFrame:
    """Load repred file into a pandas dataframe

    :param filepath:  Path to the .repred file
    :type  filepath:  str

    :return:  A dataframe of the .repred file
    :rtype :  pandas.DataFrame

    :raise e:  File not found exception
    """
    repred_df = pd.read_csv(filepath, sep="\t")
    return repred_df


def validate_repred(repred_df: pd.DataFrame) -> bool:
    """Simple validation of repred file
        Ensures that Clipping Chromosome Matches Target Chromosome

    :param repred_df:  Dataframe representation of a .repred file
    :type  repred_df:  Pandas.DataFrame

    :return:  Whether the tests pass
    :rtype :  bool
    """
    mismatches = repred_df[
        repred_df.apply(lambda x: x["H1_ClipChr"] != x["H5_TargChr"], axis=1)
    ].index.values
    if mismatches:
        raise ValueError(
            "In row(s) {} the clipping chromosome does not "
            "match the target chromosome.".format(mismatches + 2)
        )
    return True


def add_orientation(repred_df: pd.DataFrame) -> pd.DataFrame:
    """Add orientation to the table.
        Orientation is calculated by comparing where the clipping center
        (ClipS + ClipE)/2 lies relative to the Target center (TargS + TargE)/2

    :param repred_df:  Dataframe representation of a .repred file
    :type  repred_df:  Pandas.DataFrame

    :return:  Modified dataframe which includes the orientation
    :rtype :  Pandas.DataFrame
    """
    repred_df["strand"] = repred_df.apply(
        lambda x: calculate_orientation(
            x.name, x.H2_ClipS, x.H3_ClipE, x.H6_TargS, x.H7_TargE
        ),
        axis=1,
    )
    return repred_df


def convert_dataframe(repred_dataframe: pd.DataFrame) -> pd.DataFrame:
    """

    :type repred_dataframe: object
    """
    required_cols = [
        "H5_TargChr",
        "H6_TargS",
        "H7_TargE",
        "H2_ClipS",
        "H3_ClipE",
        "H18_EnzmCS",
        "H30_label",
        "H31_pred",
    ]
    transcposcope_df = repred_dataframe[required_cols].copy()
    del repred_dataframe
    transcposcope_df = add_orientation(transcposcope_df)
    transcposcope_df["3_prime_end"] = True
    transcposcope_df.columns = [
        "chromosome",
        "target_start",
        "target_end",
        "clip_start",
        "clip_end",
        "enzyme_cut_sites",
        "label",
        "pred",
        "strand",
        "three_prime_end",
    ]
    transcposcope_df = transcposcope_df[
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
        ]
    ]

    transcposcope_df["me_start"] = 6064 - 160
    transcposcope_df["me_end"] = 6064
    return transcposcope_df


def main(filepath: str):
    """Main method for TIPseqHunter parser

    :param filepath:  Path to the input .repred file
    :type  filepath:  str

    :param path:  output path
    :type  path:  str
    """

    file_name = filepath.split("/")[-1].split(".")[0]
    repred_df = load_repred(filepath)
    if validate_repred(repred_df):
        print("Repred is valid")

    repred_df = convert_dataframe(repred_df)
    repred_df.sort_values(by=["chromosome"]).to_csv(
        "TS_{}.tab".format(file_name), sep="\t", index=False
    )
    print("Created input file:\nTS_{}.tab".format(file_name))


if __name__ == "__main__":
    FILENAME = sys.argv[1] if len(sys.argv) in [2, 3] else None
    # path = sys.argv[2] if len(sys.argv) == 3 else os.getcwd()
    PATH = os.getcwd()

    if FILENAME:
        main(FILENAME, PATH)
