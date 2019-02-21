"""
File: read_classifier.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: Classify reads by how they are oriented with regards to the
             insertion site.
"""

# TODO - Refactor this file

import base64
import copy
import gzip
import json
import logging
import os

import pysam


class ReadClassifier:
    """Docstring for ReadClassifier. """

    # TODO: Write docstring
    READ_BINS = [
        ["", ""],
        ["g_gn", ""],
        ["", "l_ln"],
        ["g_jn", "l_jn"],
        ["g_gn", ""],
        ["g_gg", ""],
        ["g_gl", "l_gl"],
        ["g_jg", "l_jg"],
        ["", "l_ln"],
        ["g_gl", "l_gl"],
        ["", "l_ll"],
        ["g_jl", "l_jl"],
        ["g_jn", "l_jn"],
        ["g_jg", "l_jg"],
        ["g_jl", "l_jl"],
        ["g_jj", "l_jj"],
        ["g_rj", "l_rj"],
    ]

    def __init__(self, output_dir):
        self._wd = output_dir
        self._heading = [
            "chr#",
            "clipS",
            "count",
            "-/-",
            "g/-",
            "l1/-",
            "j/-",
            "-/g",
            "g/g",
            "l1/g",
            "j/g",
            "-/l1",
            "g/l1",
            "l1/l1",
            "j/l1",
            "-/j",
            "g/j",
            "l1/j",
            "j/j",
            "sum",
            "junction",
        ]
        self._heading_len = [len(s) for s in self._heading]

    # TODO - REFACTOR THIS METHOD
    def classify_insertion(self, insertion, bamfile):
        # min_l1 = self.L1_REF_SEQ_START
        # max_l1 = self.L1_REF_SEQ_END
        min_l1 = insertion.LINE1_START
        max_l1 = insertion.LINE1_END
        min_g = insertion.START
        max_g = insertion.END
        complement = 0
        if (insertion.THREE_PRIME and insertion.ME_IS_COMPLEMENT) or (
                not insertion.THREE_PRIME and not insertion.ME_IS_COMPLEMENT
        ):
            complement = 1
            zero = insertion.CLIP_START
            zero_ = insertion.CLIP_END
            j_start = zero - min_g + 1
            j_end = zero_ - min_g
            max_g = zero_ - 1
        else:
            zero = insertion.CLIP_END
            zero_ = insertion.CLIP_START
            j_start = insertion.LINE1_END - insertion.LINE1_START
            j_end = j_start + (zero - zero_) - 1
            min_g = zero_
        json_data = {"info": insertion.ALL_COLUMNS, "bins": {}}

        if complement:
            l_offset = 0
            l_zero = [
                {
                    "x": i + l_offset,
                    "y": 0,
                    "A": 0,
                    "C": 0,
                    "G": 0,
                    "T": 0,
                    "N": 0,
                    "X": 0,
                }
                for i in range(0, max_l1 - min_l1 + 1)
            ]
            g_zero = [
                {
                    "x": i,
                    "y": 0,
                    "A": 0,
                    "C": 0,
                    "G": 0,
                    "T": 0,
                    "N": 0,
                    "X": 0,
                    "pos": 0,
                }
                for i in range(-(max_g + 1 - min_g), 0)
            ]
            letter_g = [
                {
                    "x": i,
                    "X": 0,
                    "bp": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
                    "c": "-",
                    "s": "-",
                }
                for i in range(-(max_g + 1 - min_g), 0)
            ]
            letter_l = [
                {
                    "x": i + l_offset,
                    "X": 0,
                    "bp": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
                    "c": "-",
                    "s": "-",
                }
                for i in range(0, max_l1 - min_l1 + 1)
            ]
            g_letter_offset = 0
            l_letter_offset = 0
        else:
            l_offset = 0
            l_zero = [
                {
                    "x": i + l_offset,
                    "y": 0,
                    "A": 0,
                    "C": 0,
                    "G": 0,
                    "T": 0,
                    "N": 0,
                    "X": 0,
                }
                for i in range(-(max_l1 - min_l1), 0)
            ]
            g_zero = [
                {
                    "x": i,
                    "y": 0,
                    "A": 0,
                    "C": 0,
                    "G": 0,
                    "T": 0,
                    "N": 0,
                    "X": 0,
                    "pos": 0,
                }
                for i in range(0, max_g - min_g + 1)
            ]
            letter_g = [
                {
                    "x": i,
                    "X": 0,
                    "bp": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
                    "c": "-",
                    "s": "-",
                }
                for i in range(0, max_g - min_g + 1)
            ]
            letter_l = [
                {
                    "x": i + l_offset,
                    "X": 0,
                    "bp": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
                    "c": "-",
                    "s": "-",
                }
                for i in range(-(max_l1 - min_l1), 0)
            ]
            g_letter_offset = 0
            l_letter_offset = 0

        temp_g = {
            "xmin": min_g,
            "xmax": max_g,
            "ymin": 0,
            "ymax": 0,
            "length": max_g - min_g + 1,
            "coverage": copy.deepcopy(g_zero),
        }
        temp_l = {
            "xmin": min_l1,
            "xmax": max_l1,
            "ymin": 0,
            "ymax": 0,
            "length": max_l1 - min_l1 + 1,
            "coverage": copy.deepcopy(l_zero),
        }
        for bn in self.READ_BINS:
            if bn[0] != "":
                json_data["bins"][bn[0]] = copy.deepcopy(temp_g)
            if bn[1] != "":
                json_data["bins"][bn[1]] = copy.deepcopy(temp_l)

        json_data["bins"]["g_rj"]["reads"] = []
        json_data["bins"]["l_rj"]["reads"] = []

        json_data["stats"] = {
            "chromosome": insertion.CHROMOSOME,
            "bp_min": min_g,
            "bp_max": max_g,
            "l1_min": min_l1,
            "l1_max": max_l1,
            "complement": complement,
            "zero_offset": zero_ - zero,
        }
        json_data["stats"]["sequence_g"] = letter_g
        json_data["stats"]["sequence_l"] = letter_l
        if complement:
            json_data["stats"]["ClipS"] = insertion.CLIP_START - max_g
            json_data["stats"]["ClipE"] = insertion.CLIP_END - max_g
            (json_data["stats"]["ClipWidth"]) = (
                    insertion.CLIP_END - insertion.CLIP_START
            )
            json_data["stats"]["start"] = min_g - max_g - 1
            json_data["stats"]["end"] = (
                                                insertion.LINE1_END - insertion.LINE1_START - 1
                                        ) + l_offset
        else:
            json_data["stats"]["ClipS"] = zero_ - min_g
            json_data["stats"]["ClipE"] = zero - min_g
            json_data["stats"]["ClipWidth"] = (
                    json_data["stats"]["ClipE"] - json_data["stats"]["ClipS"]
            )
            json_data["stats"]["start"] = (
                    -(insertion.LINE1_END - insertion.LINE1_START) + l_offset - 1
            )
            json_data["stats"]["end"] = max_g - min_g + 1
        read_type_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        mins = [min_g, min_l1]

        bam = pysam.AlignmentFile(bamfile, "rb")
        bam_reads = iter(bam.fetch())
        read_dict = {}
        for read in bam_reads:
            if read.query_name in read_dict:
                read_dict[read.query_name].append(read)
            else:
                read_dict[read.query_name] = [read]

        for (k, v) in read_dict.items():
            boolean_which_reads = [False, False, False, False]
            j_boolean_which_reads = [False, False, False, False]

            queries = ["", "", "", ""]
            junction_queries = [None, None, None, None]

            if v[0].is_unmapped:
                boolean_which_reads[0] = boolean_which_reads[1] = False
            elif (v[0].reference_start + 1 >= j_end and not complement) or (
                    v[0].reference_end <= j_start and complement
            ):
                boolean_which_reads[0] = True
                queries[0] = v[0]
            elif (v[0].reference_end <= j_start and not complement) or (
                    v[0].reference_start + 1 >= j_end and complement
            ):
                boolean_which_reads[1] = True
                queries[1] = v[0]
            # TODO - change this expression to a function
            elif (
                    v[0].reference_start + 1 < j_end
                    and v[0].reference_end > j_start
            ):
                boolean_which_reads[0] = boolean_which_reads[1] = True
                queries[0] = queries[1] = v[0]
                junction_queries[0] = junction_queries[1] = v[0]
                j_boolean_which_reads[0] = j_boolean_which_reads[1] = True

            if v[1].is_unmapped:
                boolean_which_reads[2] = boolean_which_reads[3] = False
            elif (v[1].reference_start + 1 >= j_end and not complement) or (
                    v[1].reference_end <= j_start and complement
            ):
                boolean_which_reads[2] = True
                queries[2] = v[1]
            elif (v[1].reference_end <= j_start and not complement) or (
                    v[1].reference_start + 1 >= j_end and complement
            ):
                boolean_which_reads[3] = True
                queries[3] = v[1]
            elif (
                    v[1].reference_start + 1 < j_end
                    and v[1].reference_end > j_start
            ):
                boolean_which_reads[2] = boolean_which_reads[3] = True
                queries[2] = queries[3] = v[1]
                junction_queries[2] = junction_queries[3] = v[1]
                j_boolean_which_reads[2] = j_boolean_which_reads[3] = True

            read_type = (
                    (int(boolean_which_reads[0]) << 0)
                    + (int(boolean_which_reads[1]) << 1)
                    + (int(boolean_which_reads[2]) << 2)
                    + (int(boolean_which_reads[3]) << 3)
            )

            read_type_counts[read_type] += 1
            self.increment(
                read_type,
                boolean_which_reads,
                json_data,
                mins,
                queries,
                complement,
                len(l_zero),
                insertion.LINE1_START,
                insertion.LINE1_END,
            )

            if read_type in [3, 7, 11, 12, 13, 14, 15]:
                self.increment(
                    16,
                    j_boolean_which_reads,
                    json_data,
                    mins,
                    junction_queries,
                    complement,
                    len(l_zero),
                    insertion.LINE1_START,
                    insertion.LINE1_END,
                )
                for v_read in [junction_queries[0], junction_queries[2]]:
                    if v_read is not None:
                        col_string = self.colorize_g(
                            v_read.seq, v_read.cigartuples, 0
                        )
                        if complement:
                            json_data["bins"]["g_rj"]["reads"].append(
                                {
                                    # TODO - make sure that the parenthesis
                                    #  does not break the functionality
                                    "x": (
                                        json_data["bins"]["g_rj"]["coverage"][
                                            v_read.reference_start - 1
                                            ]["x"]
                                    ),
                                    "X": v_read.reference_start,
                                    "seq": v_read.seq,
                                    "cig": col_string[1],
                                }
                            )
                        else:
                            json_data["bins"]["g_rj"]["reads"].append(
                                {
                                    "x": v_read.reference_start
                                         - (
                                                 insertion.LINE1_END
                                                 - insertion.LINE1_START
                                         ),
                                    "X": v_read.reference_start,
                                    "seq": v_read.seq,
                                    "cig": col_string[1],
                                }
                            )
        fa_g_seq = insertion.GENOME_SEQUENCE
        fa_l_seq = insertion.LINE1_SEQUENCE
        for bn in json_data["bins"]:
            if "g_" in bn:
                for (i, each) in enumerate(json_data["bins"][bn]["coverage"]):
                    letter_g[i + g_letter_offset]["bp"]["A"] += each["A"]
                    letter_g[i + g_letter_offset]["bp"]["G"] += each["G"]
                    letter_g[i + g_letter_offset]["bp"]["C"] += each["C"]
                    letter_g[i + g_letter_offset]["bp"]["T"] += each["T"]
                    letter_g[i + g_letter_offset]["bp"]["N"] += each["N"]
                    letter_g[i + g_letter_offset]["bp"]["X"] += each["X"]
            if "l_" in bn:
                for (i, each) in enumerate(json_data["bins"][bn]["coverage"]):
                    l_offset = i #+ 1 if not complement else i
                    letter_l[l_offset]["bp"]["A"] += each["A"]
                    letter_l[l_offset]["bp"]["G"] += each["G"]
                    letter_l[l_offset]["bp"]["C"] += each["C"]
                    letter_l[l_offset]["bp"]["T"] += each["T"]
                    letter_l[l_offset]["bp"]["N"] += each["N"]
                    letter_l[l_offset]["bp"]["X"] += each["X"]
        offset = fa_g_seq.count("X")
        for (i, item) in enumerate(letter_g):
            if (
                    item["bp"]["A"]
                    + item["bp"]["G"]
                    + item["bp"]["C"]
                    + item["bp"]["T"]
                    + item["bp"]["N"]
                    != 0
            ):
                letter_g[i]["c"] = max(
                    item["bp"].keys(), key=lambda key: item["bp"][key]
                )
            else:
                letter_g[i]["c"] = "-"
            if g_letter_offset <= i < g_letter_offset + len(fa_g_seq):
                letter_g[i - offset]["s"] = fa_g_seq[i - g_letter_offset]

        for (i, item) in enumerate(letter_l):
            if (
                    item["bp"]["A"]
                    + item["bp"]["G"]
                    + item["bp"]["C"]
                    + item["bp"]["T"]
                    + item["bp"]["N"]
                    != 0
            ):
                letter_l[i]["c"] = max(
                    item["bp"].keys(), key=lambda key: item["bp"][key]
                )
            else:
                letter_l[i]["c"] = "-"
            if l_letter_offset <= i < l_letter_offset + len(fa_l_seq):
                letter_l[i]["s"] = fa_l_seq[i]

        output_directory = self._wd

        clip_id = insertion.CLIP_START
        # clip_flank = insertion.CLIP_END - insertion.CLIP_START

        if insertion.THREE_PRIME:
            # TODO: Change this back to 3 for normal use
            end = "N"
        else:
            end = "5"
        # TODO - change to use a format string
        with open(
                os.path.join(
                    output_directory,
                    insertion.CHROMOSOME
                    + "-"
                    + str(clip_id)
                    + "("
                    + end
                    + ").json.gz.txt",
                ),
                "wb+",
        ) as outfile:
            json_out = json.dumps(json_data)
            gz = gzip.compress(str.encode(json_out))
            b64 = base64.standard_b64encode(gz)
            outfile.write(b64)

        values = [
            insertion.CHROMOSOME,
            str(insertion.CLIP_START),
            str(len(read_dict)),
            # '\t'.join(str(x) for x in read_type_counts),
            str(sum(read_type_counts)),
            str(
                read_type_counts[3]
                + read_type_counts[7]
                + read_type_counts[11]
                + read_type_counts[12]
                + read_type_counts[13]
                + read_type_counts[14]
                + read_type_counts[15]
            ),
        ]

        values[3:3] = [str(x) for x in read_type_counts]

        widths = [
            max(self._heading_len[i] + 2, len(values[i]) + 2)
            for i, item in enumerate(values)
        ]
        # TODO - make a function to draw the boxes
        h = (
                "|"
                + "|".join(
            [s.ljust(widths[i], " ") for i, s in enumerate(self._heading)]
        )
                + "|"
        )
        v = (
                "|"
                + "|".join([s.ljust(widths[i], " ") for i, s in enumerate(values)])
                + "|"
        )

        logging.info("-" * len(h))
        logging.info(h)
        logging.info("-" * len(h))
        logging.info(v)
        logging.info("-" * len(h))
        # self._totals = [x + y for (x + y) in zip(self._totals,
        #                                         read_type_counts)]

    def increment(
            self,
            read_type,
            boolean_which_reads,
            json_data,
            mins,
            queries,
            complement,
            me_width,
            me_start,
            me_end,
    ):
        bins = self.READ_BINS[read_type]
        if complement:
            min_g = mins[0]
            mins[0] = 1
            mins[1] = len(json_data["bins"]["g_gg"]["coverage"]) + 1
            ofs = 1
        else:
            min_g = mins[0]
            mins[0] = me_width + 1
            mins[1] = 1
            ofs = me_width
        if bins[0] != "" or bins[1] != "":
            if boolean_which_reads[0]:
                s_query = self.add_deletions(
                    queries[0].query_sequence, queries[0].cigartuples
                )
                qs_start = queries[0].reference_start + 1
                blocks = queries[0].get_blocks()
                for i in range(len(blocks) - 1):
                    for j in range(blocks[i][1], blocks[i + 1][0] + 1):
                        if j < mins[1]:
                            json_data["bins"][bins[0]]["coverage"][
                                j - mins[0]
                                ]["X"] += 1
                for block in blocks:
                    if complement:
                        b_start = block[0] + 1
                        b_end = (
                            block[1] + 1 if block[1] + 1 < mins[1] else mins[1]
                        )
                    else:
                        # TODO - make a variable for the ref length
                        b_start = (
                            block[0] + 1
                            if block[0] + 1 >= me_width + 1
                            else me_width + 1
                        )
                        b_end = block[1] + 1
                    for i in range(b_start, b_end):
                        json_data["bins"][bins[0]]["coverage"][i - mins[0]][
                            s_query[i - qs_start]
                        ] += 1
                        json_data["bins"][bins[0]]["coverage"][i - mins[0]][
                            "y"
                        ] += 1
                        json_data["bins"][bins[0]]["coverage"][i - mins[0]][
                            "pos"
                        ] = (i + min_g - ofs)
            if boolean_which_reads[1]:
                s_query = self.add_deletions(
                    queries[1].query_sequence, queries[1].cigartuples
                )
                qs_start = queries[1].reference_start + 1
                blocks = queries[1].get_blocks()
                for block in blocks:
                    if complement:
                        b_start = (
                            block[0] + 1
                            if block[0] + 1 >= mins[1]
                            else mins[1]
                        )
                        b_end = block[1] + 1
                    else:
                        b_start = block[0] + 1
                        b_end = (
                            block[1] + 1
                            if block[1] + 1 <= me_width + 1
                            else me_width + 1
                        )
                    try:
                        for i in range(len(blocks) - 1):
                            for j in range(blocks[i][1], blocks[i + 1][0] + 1):
                                if j < mins[0]:
                                    json_data["bins"][bins[1]]["coverage"][
                                        j - mins[1]
                                        ]["X"] += 1
                        for i in range(b_start, b_end):
                            json_data["bins"][bins[1]]["coverage"][
                                i - mins[1]
                                ][s_query[i - qs_start]] += 1
                            json_data["bins"][bins[1]]["coverage"][
                                i - mins[1]
                                ]["y"] += 1
                            json_data["bins"][bins[1]]["coverage"][
                                i - mins[1]
                                ]["pos"] = (
                                i + me_start
                                if not complement
                                else me_end - (i - mins[1])
                            )
                    except IndexError:
                        logging.error("error 1")
            if boolean_which_reads[2]:
                s_query = self.add_deletions(
                    queries[2].query_sequence, queries[2].cigartuples
                )
                qs_start = queries[2].reference_start + 1
                blocks = queries[2].get_blocks()
                for block in blocks:
                    if complement:
                        b_start = block[0] + 1
                        b_end = (
                            block[1] + 1 if block[1] + 1 < mins[1] else mins[1]
                        )
                    else:
                        b_start = (
                            block[0] + 1
                            if block[0] + 1 >= me_width + 1
                            else me_width + 1
                        )
                        b_end = block[1] + 1
                    for i in range(len(blocks) - 1):
                        for j in range(blocks[i][1], blocks[i + 1][0] + 1):
                            if j < mins[1]:
                                json_data["bins"][bins[0]]["coverage"][
                                    j - mins[0]
                                    ]["X"] += 1
                    for i in range(b_start, b_end):
                        json_data["bins"][bins[0]]["coverage"][i - mins[0]][
                            s_query[i - qs_start]
                        ] += 1
                        json_data["bins"][bins[0]]["coverage"][i - mins[0]][
                            "y"
                        ] += 1
                        json_data["bins"][bins[0]]["coverage"][i - mins[0]][
                            "pos"
                        ] = (i + min_g - ofs)
            if boolean_which_reads[3]:
                s_query = self.add_deletions(
                    queries[3].query_sequence, queries[3].cigartuples
                )
                qs_start = queries[3].reference_start + 1
                blocks = queries[3].get_blocks()
                for block in blocks:
                    if complement:
                        b_start = (
                            block[0] + 1
                            if block[0] + 1 >= mins[1]
                            else mins[1]
                        )
                        b_end = block[1] + 1
                    else:
                        b_start = block[0] + 1
                        b_end = (
                            block[1] + 1
                            if block[1] + 1 <= me_width + 1
                            else me_width + 1
                        )
                    for i in range(len(blocks) - 1):
                        for j in range(blocks[i][1], blocks[i + 1][0] + 1):
                            if j < mins[0]:
                                json_data["bins"][bins[1]]["coverage"][
                                    j - mins[1]
                                    ]["X"] += 1
                    for i in range(b_start, b_end):
                        json_data["bins"][bins[1]]["coverage"][i - mins[1]][
                            s_query[i - qs_start]
                        ] += 1

                        json_data["bins"][bins[1]]["coverage"][i - mins[1]][
                            "y"
                        ] += 1
                        json_data["bins"][bins[1]]["coverage"][i - mins[1]][
                            "pos"
                        ] = (
                            i + me_start
                            if not complement
                            else me_end - (i - mins[1])
                        )

        mins[0] = min_g

    @staticmethod
    def colorize_g(seq, cigar, leng):
        s = seq
        ret_string = ""
        ret_array = []
        leng_string = ""
        # colors = []
        for c in cigar:
            if c[0] == 3 or c[0] > 4:
                print("cigar : ", c[0])
            if c[0] == 0:
                ret_string += s[: c[1]]  # colored(s[:c[1]], 'green')
                ret_array.append((s[: c[1]], "green"))
                leng_string += s[: c[1]]
                s = s[c[1]:]
            elif c[0] == 1:
                ret_string += s[: c[1]]  # colored(s[:c[1]], 'magenta')
                ret_array.append((ret_array[-1][0][-1], "magenta"))
                ret_array[-2] = (ret_array[-2][0][:-1], ret_array[-2][1])
                leng_string += s[: c[1]]
                s = s[c[1]:]
            elif c[0] == 2:
                ret_string += "-" * c[1]  # colored('X'*c[1], 'blue')
                ret_array.append(("-" * c[1], "black"))
                leng_string += "-" * c[1]
            # s = s[c[1]:]
            elif c[0] == 4:
                ret_string += s[: c[1]]  # colored(s[:c[1]], 'red')
                ret_array.append((s[: c[1]], "red"))
                leng_string += s[: c[1]]
                s = s[c[1]:]

        ret_string = (
                " " * leng + ret_string + " " * (200 - len(leng_string) - leng)
        )
        return ret_string, ret_array

    @staticmethod
    def add_deletions(sequence, cigar):
        seq_string = ""
        seq_orig = sequence
        for action in cigar:
            if action[0] == 0:  # match
                seq_string += seq_orig[: action[1]]
                seq_orig = seq_orig[action[1]:]
            elif action[0] == 1:  # insertion
                # seq_string += seq_orig[:action[1]]
                seq_orig = seq_orig[action[1]:]
            elif action[0] == 2:  # deletion
                seq_string += "X" * action[1]
            elif action[0] == 3:  # BAM_CREF_SKIP
                logging.error("BAM_CREF_SKIP")
            elif action[0] == 4:  # soft clipping
                # seq_string += seq_orig[:action[1]]
                seq_orig = seq_orig[action[1]:]
            elif action[0] == 5:  # hard clip
                logging.error("hc")
            elif action[0] == 6:  # CPAD
                logging.error("cpad")
            elif action[0] == 7:  # equal
                logging.error("equal")
            elif action[0] == 8:  # diff
                logging.error("diff")
        return seq_string
