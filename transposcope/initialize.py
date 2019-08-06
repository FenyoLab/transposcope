"""
File: initialize.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: Setup logging and initialize folder structures for output
"""

from functools import reduce
import json
import logging.config
import os
import shutil


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
        with open(path, "rt") as file_handle:
            config = json.load(file_handle)
        logging.config.dictConfig(config)

    else:
        logging.basicConfig(level=default_level)
    return logging

def create_output_folder_structure(
    output_folder_path, group1, group2, sample_id
):
    """Creates the ouput folder structure for storing output and temporary files

    @param param:  output_folder_path
    @type  param:  path to the output folder

    @param param:  group1
    @type  param:  name of the sub group

    @param param:  group2
    @type  param:  name of the sub-sub group

    @param param:  sample_id
    @type  param:  name used to differentiate this sample from others

    @return:  reference_path, transposcope_path, track_path
    @rtype :  tuple of strings

    @raise e:  None
    """
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
        os.path.dirname(os.path.realpath(__file__)), "web/web.zip"
    )
    shutil.unpack_archive(web_path)

    os.makedirs(reference_path)
    os.makedirs(transposcope_path)
    os.makedirs(track_path)
    os.mkdir(os.path.join(reference_path, "fasta"))
    os.mkdir(os.path.join(reference_path, "fastq"))
    os.mkdir(os.path.join(reference_path, "sam"))

    return reference_path, transposcope_path, track_path


def build_tree(base_path):
    """Function to identify aligned samples for the viewer

    @param path:  path to the json output of the aligner
    @type  path:  string

    @return:  dictionary of directories and whether tables were found
    @rtype :  (dict, bool)

    @raise e:  None
    """
    dir_dict = {}
    rootdir = base_path.rstrip(os.sep)
    found_table_info = False
    start = rootdir.rfind(os.sep) + 1
    for path, _, files in os.walk(rootdir):
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
    """ Function which checks input file paths to ensure that they are correct

    @param line1_reference_path:  path to the line1 reference file
    @type  param:  string

    @param reference_genome_folder_path:  path to the reference genome file
    @type  param:  string

    @param bam_file_location:  path to the input bam file
    @type  param:  string

    @param insertion_sites_file_path:  path to the insertions file
    @type  param:  string

    @param genes_path:  path to the reflat genes list file
    @type  param:  string

    @return:  None
    @rtype :  None

    @raise SystemExit:  Stops execution of transposcope if any
    paths are incorrect
    """
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
