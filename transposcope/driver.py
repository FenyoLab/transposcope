"""
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
from transposcope.insertion_sites_reader import InsertionSiteReader
from transposcope.parsers.melt_parser import main as melt_parser
from transposcope.read_classifier import ReadClassifier
from transposcope.reads_dict import ReadsDict
from transposcope.realigner import Realigner


def setup():
    pass


def main(args):
    """Main script which drives the alignment process

    @param args:  list of command line argumnets provided when the script was 
    called
    @type  args:  tuple

    @return:  None
    @rtype :  None

    @raise e:  None
    """

    group1 = args.group1
    group2 = args.group2
    sample_id = args.sample_id
    bam_path = args.bam
    insertions_file = args.index
    me_ref_path = args.me_reference
    host_ref_path = args.host_reference
    genes_file_path = args.genes
    keep_files = args.keep_files

    # # config = get_config_from_file()
    # # TODO - allow for multiple labels
    # #  - eg : pos, unlabeled - pos - negative, pos
    # # TODO - make the reference subdirectories using the writer class
    check_paths(
        me_ref_path, host_ref_path, bam_path, insertions_file, genes_file_path
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
        " - Index File Path: {}".format(os.path.abspath(insertions_file))
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

    input_list = melt_parser(insertions_file)
    # insertion_sites_reader = InsertionSiteReader(insertion_list_path)
    logging.info("### Processing BAM File ###")
    bam_handler = BamHandler(bam_path)
    fasta_handler = FastaHandler(me_ref_path, host_ref_path)
    insertions = []
    reads_dictionary = ReadsDict()
    logging.info(" - Finding Reads in Target Regions")
    for parsed_input in input_list:
        current_insertion = Insertion(parsed_input)
        reads_in_region = bam_handler.fetch_reads_in_region(current_insertion)

        reads_dictionary += reads_in_region
        current_insertion.read_keys_in_target_region = reads_in_region.keys()
        insertions.append(current_insertion)
        print(current_insertion)
    logging.info("    --- DONE ---")
    logging.info(" - Finding Paired Ends")
    for read in bam_handler.all_reads():
        if read.query_name in reads_dictionary:
            reads_dictionary.insert(read)

    logging.info("    --- DONE ---")
    logging.info("### Processing Insertions ###")
    file_writer = FileWriter()
    realigner = Realigner(reference_path)
    # classifier = ReadClassifier(transposcope_path)
    if genes_file_path:
        gene_handler = GeneHandler(genes_file_path)
    insertions.sort(key=lambda x: x.chromosome)
    heading_table = {"Heading": ("ID", "Gene", "Probability"), "data": []}

    ten_percent = len(insertions) / 10
    next_log = ten_percent
    completed = 0
    for insertion in insertions:
        file_name = "{i.chromosome}_{i.insertion_site}".format(i=insertion)
        insertion.fasta_string = fasta_handler.generate_fasta_sequence(
            insertion
        )

        fasta_path = file_writer.write_fasta(
            reference_path,
            file_name,
            insertion.fasta_string,
            ">{i.chromosome}_{i.insertion_site}\n".format(i=insertion),
        )
        fastq1_path, fastq2_path = file_writer.write_fastq(
            reference_path,
            reads_dictionary,
            file_name,
            insertion.read_keys_in_target_region,
        )
        sorted_bam_path = realigner.realign(
            fasta_path, fastq1_path, fastq2_path, file_name
        )

        #     # TODO - add the option to not add gene information
        if genes_file_path:
            gene_info = gene_handler.find_nearest_gene(
                insertion.chromosome, insertion.insertion_site
            )
        else:
            gene_info = ("undefined", "rgb(3, 119, 190)")

    #     # heading_table['Data']\
    #     if insertion.THREE_PRIME:
    #         end = "3"
    #     else:
    #         end = "5"
    #     heading_table["data"].append(
    #         [
    #             "{}-{}({})".format(
    #                 insertion.CHROMOSOME, insertion.CLIP_START, end
    #             ),
    #             gene_info,
    #             "{:.2f}".format(insertion.PRED),
    #         ]
    #     )
    #     classifier.classify_insertion(insertion, sorted_bam_path)

    #     completed += 1
    #     if completed > next_log:
    #         logging.info(
    #             " - Percentage of insertions processed: {:.2%}.".format(
    #                 completed / len(insertions)
    #             )
    #         )
    #         next_log += ten_percent
    # #     TODO - write out index file
    # logging.info("    --- DONE ---")
    # if not keep_files:
    #     logging.info("### Cleanup ###")
    #     logging.info(
    #         "Cleaning up generated files in {}".format(reference_path)
    #     )
    #     if os.path.exists(reference_path):
    #         shutil.rmtree(os.path.dirname(reference_path))
    #     logging.info("    --- DONE ---")

    # logging.info("### Building Bed File ###")
    # with open(os.path.join(track_path, "{}.bb".format(sample_id)), "w") as fh:
    #     for insertion in insertions:
    #         fh.write(
    #             "{}\t{}\t{}\n".format(
    #                 insertion.CHROMOSOME,
    #                 insertion.CLIP_START,
    #                 insertion.CLIP_END,
    #             )
    #         )
    # logging.info("    --- DONE ---")
    # logging.info("### Building Website ###")

    # web_dir = os.path.join(os.getcwd(), "web")

    # logging.info(" The website is being built into: {}".format(web_dir))

    # file_writer.write_json(
    #     os.path.join(transposcope_path, "table_info.json.gz.txt"),
    #     heading_table,
    # )

    # tree, found_table = build_tree(os.path.join(web_dir, "json"))

    # with open(os.path.join(web_dir, "manifest.json"), "w") as json_file:
    #     json.dump(tree["json"], json_file)
    # logging.info("    --- DONE ---")

    # logging.info(
    #     " to view the generated files in your browser run:\n\t\t'transposcope view {}'".format(
    #         web_dir
    #     )
    # )
