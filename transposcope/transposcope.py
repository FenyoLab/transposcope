"""
File: transposcope.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: Main entry point for generating files required by the
            visualization
"""

from functools import reduce
import json
import logging.config
import os
import shutil

from bam_handler import BamHandler
from fasta_handler import FastaHandler
from file_writer import FileWriter
from gene_handler import GeneHandler
from insertion import Insertion
from insertion_sites_reader import InsertionSiteReader
from read_classifier import ReadClassifier
from reads_dict import ReadsDict
from realigner import Realigner


def setup_logging(path=None, default_level=logging.INFO, env_key="LOG_CFG"):
    """Setup logging configuration

    """
    value = os.getenv(env_key, None)
    if value:
        path = value
    if not path:
        path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "config/logging.json"
        )
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = json.load(f)
        logging.config.dictConfig(config)

    else:
        logging.basicConfig(level=default_level)


def create_output_folder_structure(
    output_folder_path, group1, group2, sample_id
):

    reference_path = os.path.join(
        output_folder_path,
        "ref",
        "{}".format(group1),
        "{}".format(group2),
        "{}".format(sample_id),
    )

    track_path = os.path.join(
        "web",
        "track",
        "{}".format(group1),
        "{}".format(group2),
        "{}".format(sample_id),
    )

    transposcope_path = os.path.join(
        "web",
        "json",
        "{}".format(group1),
        "{}".format(group2),
        "{}".format(sample_id),
    )
    if os.path.exists(reference_path):
        shutil.rmtree(reference_path)
    if os.path.exists(transposcope_path):
        shutil.rmtree(transposcope_path)
    if os.path.exists(track_path):
        shutil.rmtree(track_path)

    web_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "viewer/web.zip"
    )
    shutil.unpack_archive(web_path)

    os.makedirs(reference_path)
    os.makedirs(transposcope_path)
    os.makedirs(track_path)
    os.mkdir(os.path.join(reference_path, "fasta"))
    os.mkdir(os.path.join(reference_path, "fastq"))
    os.mkdir(os.path.join(reference_path, "sam"))

    return reference_path, transposcope_path, track_path


def build_tree(path):
    dir_dict = {}
    rootdir = path.rstrip(os.sep)
    found_table_info = False
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict()
        if "table_info.json.gz.txt" in files:
            found_table_info = True
        parent = reduce(dict.get, folders[:-1], dir_dict)
        parent[folders[-1]] = subdir
    return dir_dict, found_table_info


def check_paths(
    line1_reference_path,
    reference_genome_folder_path,
    bam_file_location,
    insertion_sites_file_path,
    genes_path,
):
    if not os.path.exists(line1_reference_path):
        raise SystemExit(
            "\n\nERROR: Mobile Element FASTA file not found '{}'".format(
                line1_reference_path
            )
        )
    if not os.path.exists(reference_genome_folder_path):
        raise SystemExit(
            "\n\nERROR: Reference genome folder not found '{}'".format(
                reference_genome_folder_path
            )
        )
    if not os.path.exists(bam_file_location):
        raise SystemExit(
            "\n\nERROR: BAM file not found '{}'".format(bam_file_location)
        )
    if not os.path.exists(insertion_sites_file_path):
        raise SystemExit(
            "\n\nERROR: Insertion sites file path invalid: {}".format(
                insertion_sites_file_path
            )
        )

    if genes_path:
        if not os.path.exists(insertion_sites_file_path):
            raise SystemExit(
                "\n\nERROR: refFlat.txt path invalid: {}".format(
                    insertion_sites_file_path
                )
            )


def main(args):
    group1 = args.group1
    group2 = args.group2
    sample_id = args.sample_id
    bam_path = args.bam
    insertion_list_path = args.index
    me_ref_path = args.me_reference
    host_ref_path = args.host_reference
    genes_file_path = args.genes
    keep_files = args.keep_files

    # config = get_config_from_file()
    # TODO - allow for multiple labels
    #  - eg : pos, unlabeled - pos - negative, pos
    # TODO - make the reference subdirectories using the writer class
    check_paths(
        me_ref_path,
        host_ref_path,
        bam_path,
        insertion_list_path,
        genes_file_path,
    )
    output_folder_path = os.path.join(os.getcwd(), "output")
    (
        reference_path,
        transposcope_path,
        track_path,
    ) = create_output_folder_structure(
        output_folder_path, group1, group2, sample_id
    )

    setup_logging()
    logging.info("***  TranspoScope ***")
    logging.info("### Input ###")
    logging.info(
        " - Index File Path: {}".format(os.path.abspath(insertion_list_path))
    )
    logging.info(" - BAM File Path: {}".format(os.path.abspath(bam_path)))
    logging.info(
        " - Mobile Element Reference File Path: {}".format(
            os.path.abspath(me_ref_path)
        )
    )
    logging.info(
        " - Host Genome Folder Path: {}".format(os.path.abspath(host_ref_path))
    )
    logging.info(
        " - refFlat.txt Path: {}".format(
            os.path.abspath(genes_file_path)
            if genes_file_path
            else "undefined"
        )
    )

    logging.info(" - Group 1: {}".format(group1))
    logging.info(" - Group 2: {}".format(group2))
    logging.info(" - Keep Intermediate Files: {}".format(keep_files))

    insertion_sites_reader = InsertionSiteReader(insertion_list_path)
    logging.info("### Processing BAM File ###")
    bam_handler = BamHandler(bam_path)
    fasta_handler = FastaHandler(me_ref_path, host_ref_path)
    insertions = []
    reads_dictionary = {True: ReadsDict(), False: ReadsDict()}
    logging.info(" - Finding Reads in Target Regions")
    for insertion_stats in insertion_sites_reader.read_lines():
        temp_insertion = Insertion(named_tuple=insertion_stats)
        reads_in_region = bam_handler.fetch_reads_in_region(temp_insertion)
        reads_dictionary[temp_insertion.THREE_PRIME] += reads_in_region
        temp_insertion.read_keys_in_target_region = reads_in_region.keys()
        insertions.append(temp_insertion)
    logging.info("    --- DONE ---")
    logging.info(" - Finding Paired Ends")
    for read in bam_handler.all_reads():
        if read.query_name in reads_dictionary[True]:
            reads_dictionary[True].insert(read)

        if read.query_name in reads_dictionary[False]:
            reads_dictionary[False].insert(read)
    logging.info("    --- DONE ---")
    logging.info("### Processing Insertions ###")
    file_writer = FileWriter()
    realigner = Realigner(reference_path)
    classifier = ReadClassifier(transposcope_path)
    if genes_file_path:
        gene_handler = GeneHandler(genes_file_path)
    insertions.sort(key=lambda x: x.CHROMOSOME)
    heading_table = {"Heading": ("ID", "Gene", "Probability"), "data": []}

    ten_percent = len(insertions) / 10
    next_log = ten_percent
    completed = 0
    for insertion in insertions:
        file_name = "{i.CHROMOSOME}_{i.START}-{i.END}".format(i=insertion)
        insertion.fasta_string = fasta_handler.generate_fasta_sequence(
            insertion
        )

        fasta_path = file_writer.write_fasta(
            reference_path,
            file_name,
            insertion.fasta_string,
            ">{i.CHROMOSOME}_{i.START}-{i.END}\n".format(i=insertion),
        )
        fastq1_path, fastq2_path = file_writer.write_fastq(
            reference_path,
            reads_dictionary[insertion.THREE_PRIME],
            file_name,
            insertion.read_keys_in_target_region,
        )
        sorted_bam_path = realigner.realign(
            fasta_path, fastq1_path, fastq2_path, file_name
        )

        # TODO - add the option to not add gene information
        if genes_file_path:
            gene_info = gene_handler.find_nearest_gene(
                insertion.CHROMOSOME, insertion.INSERTION_SITE
            )
        else:
            gene_info = ("undefined", "rgb(3, 119, 190)")

        # heading_table['Data']\
        if insertion.THREE_PRIME:
            end = "3"
        else:
            end = "5"
        heading_table["data"].append(
            [
                "{}-{}({})".format(
                    insertion.CHROMOSOME, insertion.CLIP_START, end
                ),
                gene_info,
                "{:.2f}".format(insertion.PRED),
            ]
        )
        classifier.classify_insertion(insertion, sorted_bam_path)

        completed += 1
        if completed > next_log:
            logging.info(
                " - Percentage of insertions processed: {:.2%}.".format(
                    completed / len(insertions)
                )
            )
            next_log += ten_percent
    #     TODO - write out index file
    logging.info("    --- DONE ---")
    if not keep_files:
        logging.info("### Cleanup ###")
        logging.info(
            "Cleaning up generated files in {}".format(reference_path)
        )
        if os.path.exists(reference_path):
            shutil.rmtree(os.path.dirname(reference_path))
        logging.info("    --- DONE ---")

    logging.info("### Building Bed File ###")
    with open(os.path.join(track_path, "{}.bb".format(sample_id)), "w") as fh:
        for insertion in insertions:
            fh.write(
                "{}\t{}\t{}\n".format(
                    insertion.CHROMOSOME,
                    insertion.CLIP_START,
                    insertion.CLIP_END,
                )
            )
    logging.info("    --- DONE ---")
    logging.info("### Building Website ###")

    web_dir = os.path.join(os.getcwd(), "web")

    logging.info(" The website is being built into: {}".format(web_dir))

    file_writer.write_json(
        os.path.join(transposcope_path, "table_info.json.gz.txt"),
        heading_table,
    )

    tree, found_table = build_tree(os.path.join(web_dir, "json"))

    with open(os.path.join(web_dir, "manifest.json"), "w") as json_file:
        json.dump(tree["json"], json_file)
    logging.info("    --- DONE ---")

    logging.info(
        " to view the generated files in your browser run:\n\t\t'transposcope view {}'".format(
            web_dir
        )
    )
