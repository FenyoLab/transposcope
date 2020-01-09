"""
Driver script for TranspoScope.

File: driver.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: Main entry point for generating files required by the
            visualization
"""


import json
import logging
import os

import shutil

from transposcope.bam_handler import BamHandler
from transposcope.fasta_handler import FastaHandler
from transposcope.file_writer import FileWriter
from transposcope.gene_handler import GeneHandler
from transposcope.initialize import (
    build_tree,
    check_paths,
    create_output_folder_structure,
    setup_logging,
)
from transposcope.insertion import Insertion

# from transposcope.insertion_sites_reader import InsertionSiteReader
from transposcope.parsers.melt_parser import main as melt_parser
from transposcope.parsers.tipseqhunter_parser import main as tipseq_parser

# from transposcope.read_classifier import ReadClassifier
from transposcope.reads_dict import ReadsDict
from transposcope.realigner import Realigner


FILE_WRITER = FileWriter()


def log_configuration(args, paths):
    logging.info("***  TranspoScope ***")
    logging.info("### Input ###")
    logging.info(" - Index File Path: %s", os.path.abspath(args.index))
    logging.info(" - BAM File Path: %s", os.path.abspath(args.bam))
    logging.info(
        " - Mobile Element Reference File Path: %s", os.path.abspath(args.me_reference),
    )
    logging.info(" - Host Genome Folder Path: %s", os.path.abspath(args.host_reference))
    logging.info(
        " - refFlat.txt Path: %s",
        os.path.abspath(args.genes) if args.genes else "undefined",
    )

    logging.info(" - Group 1: %s", args.group1)
    logging.info(" - Group 2: %s", args.group2)
    logging.info(" - Keep Intermediate Files: %s", args.keep_files)
    logging.info(" - Temp Output Directory: %s", paths.reference_path)
    logging.info(" - Visualization output directory: %s", paths.transposcope_path)


def process_bam(insertion_type, bam, index):

    if insertion_type.lower() == "melt":
        input_list = melt_parser(index)
    elif insertion_type.lower() == "tipseqhunter":
        input_list = tipseq_parser(index)
    else:
        raise TypeError(
            "{} is not recognized; Should be MELT or TIPseqHunter".format(
                insertion_type
            )
        )
    logging.info("### Processing BAM File ###")
    bam_handler = BamHandler(bam)
    insertions = []
    reads_dictionary = ReadsDict()
    logging.info(" - Finding Reads in Target Regions")
    for parsed_input in input_list:
        current_insertion = Insertion(parsed_input)
        reads_in_region = bam_handler.fetch_reads_in_region(current_insertion)
        reads_dictionary += reads_in_region
        current_insertion.read_keys_in_target_region = reads_in_region.keys()
        insertions.append(current_insertion)
    logging.info("    --- DONE ---")
    logging.info(" - Finding Paired Ends")
    longest_read = 0
    for read in bam_handler.all_reads():
        longest_read = max(read.query_length, longest_read)
        if read.query_name in reads_dictionary:
            reads_dictionary.insert(read)
    logging.info("    --- DONE ---")
    logging.info("### Processing Insertions ###")
    insertions.sort(key=lambda x: x.chromosome)
    return insertions, reads_dictionary, longest_read


def process_insertions(args, paths, insertions, reads_dictionary, longest_read):
    fasta_handler = FastaHandler(args.me_reference, args.host_reference)
    realigner = Realigner(paths.reference_path, paths.transposcope_path)
    if args.genes:
        gene_handler = GeneHandler(args.genes)
    # TODO make a separate script for handling the table of insertions
    # TODO: Add link to UCSC
    ranking = "Assess" if args.index_type.lower() == "melt" else "Pr"
    if args.genes:
        insertion_site_table = {
            "heading": ("ID", "Gene", ranking),
            "data": [],
        }
    else:
        insertion_site_table = {
            "heading": ("ID", ranking),
            "data": [],
        }

    ten_percent = len(insertions) / 10
    next_log = ten_percent
    completed = 0
    for insertion in insertions:
        file_name = "{i.chromosome}_{i.insertion_site}".format(i=insertion)
        insertion.all_info["read_length"] = longest_read
        # TODO: Write out the length of the longest read
        FILE_WRITER.write_json(
            os.path.join(paths.transposcope_path, "meta", file_name), insertion.all_info
        )

        insertion.fasta_string = fasta_handler.generate_fasta_sequence(insertion)

        fasta_path = FILE_WRITER.write_fasta(
            paths.transposcope_path,
            file_name,
            insertion.fasta_string,
            ">{i.chromosome}_{i.insertion_site}\n".format(i=insertion),
        )
        fastq1_path, fastq2_path = FILE_WRITER.write_fastq(
            paths.reference_path,
            reads_dictionary,
            file_name,
            insertion.read_keys_in_target_region,
        )
        realigner.realign(fasta_path, fastq1_path, fastq2_path, file_name)

        if args.genes:
            gene_info = gene_handler.find_nearest_gene(
                insertion.chromosome, insertion.insertion_site
            )

            insertion_site_table["data"].append(
                [
                    "{}:{}".format(insertion.chromosome, insertion.insertion_site),
                    gene_info,
                    "{:.2f}".format(float(insertion.pred)),
                ]
            )
        else:
            insertion_site_table["data"].append(
                [
                    "{}:{}".format(insertion.chromosome, insertion.insertion_site),
                    "{:.2f}".format(float(insertion.pred)),
                ]
            )

        completed += 1
        if completed > next_log:
            logging.info(
                " ├ Percentage of insertions processed: {:.2%}.".format(
                    completed / len(insertions)
                )
            )
            next_log += ten_percent
    return insertion_site_table


def main(args):
    """
    Main script which drives the alignment process.

    @param args:  list of command line argumnents provided when the script was
    called
    @type  args:  tuple

    @return:  None
    @rtype :  None

    @raise e:  None
    """
    # # TODO - allow for multiple labels
    # #  - eg : pos, unlabeled - pos - negative, pos
    # # TODO - make the reference subdirectories using the writer class

    check_paths(args)
    output_folder_path = os.path.join(os.getcwd(), "output")
    paths = create_output_folder_structure(output_folder_path, args)

    setup_logging()
    log_configuration(args, paths)

    insertions, reads_dictionary, longest_read = process_bam(
        args.index_type, args.bam, args.index
    )

    insertion_site_table = process_insertions(
        args, paths, insertions, reads_dictionary, longest_read
    )

    #     TODO - write out index file
    logging.info("    --- DONE ---")
    if not args.keep_files:
        logging.info("### Cleanup ###")
        logging.info("Cleaning up generated files in %s", paths.reference_path)
        if os.path.exists(paths.reference_path):
            shutil.rmtree(paths.reference_path)
        logging.info("    --- DONE ---")

    # TODO: Currently these bed files would need to be converted into a bigbed file to work correctly
    # TODO: Figure out how to load these files from github or a private server (this will mostly be front end code)
    # logging.info("### Building Bed File ###")
    # with open(
    #     os.path.join(paths.track_path, "{}.bb".format(args.sample_id)), "w"
    # ) as file_handle:
    #     for insertion in insertions:
    #         file_handle.write(
    #             "{}\t{}\t{}\n".format(
    #                 insertion.chromosome,
    #                 insertion.five_prime_target,
    #                 insertion.three_prime_target,
    #             )
    #         )
    # logging.info("    --- DONE ---")
    logging.info("### Building Website ###")

    web_dir = os.path.join(os.getcwd(), "web")

    logging.info("### The website is being built into: %s", web_dir)

    FILE_WRITER.write_json(
        os.path.join(paths.transposcope_path, "table_info"), insertion_site_table,
    )

    tree, found_table = build_tree(os.path.join(web_dir, "data"))

    with open(os.path.join(web_dir, "manifest.json"), "w") as json_file:
        json.dump(tree["data"], json_file)
    logging.info("    --- DONE ---")

    logging.info(
        " to view the generated files in your browser run:\n\t\t'transposcope view %s'",
        web_dir,
    )
