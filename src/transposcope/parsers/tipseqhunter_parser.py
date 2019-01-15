import sys

import pandas as pd


def calculate_orientation(
    index, clip_start, clip_end, target_start, target_end
):
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
    df_repred = pd.read_table(filepath)
    return df_repred


def validate_repred(repred_df: pd.DataFrame) -> bool:
    mismatches = repred_df[
        repred_df.apply(lambda x: x["H1_ClipChr"] != x["H5_TargChr"], axis=1)
    ].index.values
    index_offset = 2
    print(mismatches + index_offset)
    if len(mismatches) > 0:
        raise ValueError(
            "In row(s) {} the clipping chromosome does not "
            "match the target chromosome.".format(mismatches + 2)
        )
    return True
    # TODO - add tests to make sure that coordinates are numbers, etc


def add_orientation(df: pd.DataFrame) -> pd.DataFrame:
    df["strand"] = df.apply(
        lambda x: calculate_orientation(
            x.name, x.H2_ClipS, x.H3_ClipE, x.H6_TargS, x.H7_TargE
        ),
        axis=1,
    )
    return df


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
    # TODO : check that 160 is the correct distance for the primer
    transcposcope_df["me_start"] = 6064 - 160
    transcposcope_df["me_end"] = 6064
    return transcposcope_df


def main(filepath, only_gold_standard=False):
    file_name = filepath.split("/")[-1].split(".")[0]
    df = load_repred(filepath)
    if validate_repred(df):
        print("Repred is valid")
    df = convert_dataframe(df)
    df.to_csv(
        "output/insertion_tables/{}.tab".format(file_name),
        sep="\t",
        index=False,
    )


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    if filename:
        main(filename)
