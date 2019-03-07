"""
File: transposcope.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: Main entry point for generating files required by the
            visualization
"""

import json
import logging.config
import os
import shutil

import sys

from transposcope.bam_handler import BamHandler
from transposcope.fasta_handler import FastaHandler
from transposcope.file_writer import FileWriter
from transposcope.gene_handler import GeneHandler
from transposcope.insertion import Insertion
from transposcope.insertion_sites_reader import InsertionSiteReader
from transposcope.read_classifier import ReadClassifier
from transposcope.reads_dict import ReadsDict
from transposcope.realigner import Realigner


# from memory_profiler import profile


# def get_config_from_file():
# with open("./config/config_hg19.json") as json_data_file:
# # with open('./config/config.json') as json_data_file:
# data = json.load(json_data_file)
# return data


def setup_logging(
    path="./config/logging.json",
    default_level=logging.INFO,
    env_key="LOG_CFG",
    logging_folder="./log/",
):
    """Setup logging configuration

    """
    if logging_folder == "./log/" and not os.path.exists("logs"):
        os.makedirs("logs")
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = json.load(f)
            (
                config["handlers"]["info_file_handler"]["filename"]
            ) = os.path.join(logging_folder, "info.log")
            (
                config["handlers"]["error_file_handler"]["filename"]
            ) = os.path.join(logging_folder, "error.log")
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

    transposcope_path = os.path.join(
        "web",
        "json",
        "{}".format(group1),
        "{}".format(group2),
        "{}".format(sample_id),
    )
    logs_path = os.path.join(
        output_folder_path,
        "logs",
        "{}".format(group1),
        "{}".format(group2),
        "{}".format(sample_id),
    )
    if os.path.exists(reference_path):
        shutil.rmtree(reference_path)
    if os.path.exists(logs_path):
        shutil.rmtree(logs_path)
    if os.path.exists(transposcope_path):
        shutil.rmtree(transposcope_path)

    web_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "viewer/web.zip"
    )
    shutil.unpack_archive(web_path)

    os.makedirs(reference_path)
    os.makedirs(logs_path)
    os.makedirs(transposcope_path)
    os.mkdir(os.path.join(reference_path, "fasta"))
    os.mkdir(os.path.join(reference_path, "fastq"))
    os.mkdir(os.path.join(reference_path, "sam"))
    os.mkdir(os.path.join(reference_path, "logs"))

    return reference_path, transposcope_path, logs_path


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
    print("starting")

    # config = get_config_from_file()
    # TODO - allow for multiple labels
    #  - eg : pos, unlabeled - pos - negative, pos
    # TODO - make the reference subdirectories using the writer class
    output_folder_path = os.path.join(os.getcwd(), "output")
    (
        reference_path,
        transposcope_path,
        logs_path,
    ) = create_output_folder_structure(
        output_folder_path,
        # reference_type,
        group1,
        group2,
        sample_id,
    )

    setup_logging(logging_folder=logs_path)
    logging.info("--TranspoScope--")

    # (
    #     repred_path,
    #     bam_path
    # ) = find_files(
    #     file_id,
    #     anatomy,
    #     reference_type,
    #     config
    # )
    # bam_folder = os.path.expanduser(config["input"]["bam"])
    # bam_path = os.path.join(bam_folder, bam_name)
    # insertion_list_folder = os.path.expanduser(
    #     config["input"]["insertion_table_dir"]
    # )
    # insertion_list_path = os.path.join(insertion_list_folder, insertion_list)

    logging.info(bam_path)
    insertion_sites_reader = InsertionSiteReader(insertion_list_path)
    logging.info("loading bam")
    bam_handler = BamHandler(bam_path)
    fasta_handler = FastaHandler(me_ref_path, host_ref_path)
    insertions = []
    reads_dictionary = {True: ReadsDict(), False: ReadsDict()}
    logging.info("finding target regions")
    for insertion_stats in insertion_sites_reader.read_lines():
        temp_insertion = Insertion(named_tuple=insertion_stats)
        reads_in_region = bam_handler.fetch_reads_in_region(temp_insertion)
        reads_dictionary[temp_insertion.THREE_PRIME] += reads_in_region
        temp_insertion.read_keys_in_target_region = reads_in_region.keys()
        insertions.append(temp_insertion)
    logging.info("finding pairs")
    for read in bam_handler.all_reads():
        if read.query_name in reads_dictionary[True]:
            reads_dictionary[True].insert(read)

        if read.query_name in reads_dictionary[False]:
            reads_dictionary[False].insert(read)

    logging.info("Processing insertions")
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
            gene_info = ("Normal", "rgb(3, 119, 190)")

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
                "Percentage of insertions processed: {:.2%}.".format(
                    next_log / len(insertions)
                )
            )
            next_log += ten_percent
    #     TODO - write out bedfile
    #     TODO - write out index file
    #     TODO - delete local realignment files (test this)
    #     TODO - add fastq to removal
    if not keep_files:
        if os.path.exists(fasta_path):
            shutil.rmtree(os.path.dirname(fasta_path))
        if os.path.exists(sorted_bam_path):
            shutil.rmtree(os.path.dirname(sorted_bam_path))

    file_writer.write_json(
        os.path.join(transposcope_path, "table_info.json.gz.txt"),
        heading_table,
    )
