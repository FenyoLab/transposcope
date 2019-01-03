import json
import logging.config
import os
import shutil

from src.transposcope.bam_handler import BamHandler
from src.transposcope.constants import LABEL
from src.transposcope.fasta_handler import FastaHandler
from src.transposcope.file_writer import FileWriter
from src.transposcope.gene_handler import GeneHandler
from src.transposcope.insertion import Insertion
from src.transposcope.read_classifier import ReadClassifier
from src.transposcope.reads_dict import ReadsDict
from src.transposcope.realigner import Realigner
from src.transposcope.repred_reader import RepredReader


# from memory_profiler import profile


def get_config_from_file():
    with open('./config/config.json') as json_data_file:
        data = json.load(json_data_file)
    return data


def setup_logging(
        path='./config/logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG',
        logging_folder="./log/"
):
    """Setup logging configuration

    """
    if not os.path.exists('log'):
        os.makedirs('log')
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
            config["handlers"]["info_file_handler"]["filename"] = os.path.join(logging_folder, 'info.log')
            config["handlers"]["error_file_handler"]["filename"] = os.path.join(logging_folder, 'error.log')
        logging.config.dictConfig(config)

    else:
        logging.basicConfig(level=default_level)


def create_output_folder_structure(output_folder_path, reference_type, label, anatomy, sample_type, patient_id):
    reference_path = os.path.join(output_folder_path, 'ref', reference_type, anatomy, patient_id,
                                  label + '-' + patient_id + '-' + sample_type)
    transposcope_path = os.path.join(output_folder_path, 'json', anatomy + '_' + reference_type, patient_id,
                                     label + '-' + patient_id + '-' + sample_type)
    logs_path = os.path.join(output_folder_path, 'logs', reference_type, label + '-' + patient_id + '-' + sample_type)
    if os.path.exists(reference_path):
        shutil.rmtree(reference_path)
    if os.path.exists(logs_path):
        shutil.rmtree(logs_path)
    if os.path.exists(transposcope_path):
        shutil.rmtree(transposcope_path)
    os.makedirs(reference_path)
    os.makedirs(logs_path)
    os.makedirs(transposcope_path)
    os.mkdir(os.path.join(reference_path, 'fasta'))
    os.mkdir(os.path.join(reference_path, 'fastq'))
    os.mkdir(os.path.join(reference_path, 'sam'))
    os.mkdir(os.path.join(reference_path, 'logs'))
    return reference_path, transposcope_path, logs_path


def find_files(file_id, anatomy, reference_type, config):
    repred_folder = os.listdir(os.path.expanduser(config['input']['repred']) + '/' + anatomy)
    repred_file_path = None
    for each_file in repred_folder:
        if file_id in each_file and reference_type.lower() in each_file.lower() and each_file.endswith('.repred'):
            repred_file_path = os.path.abspath(
                os.path.expanduser(config['input']['repred']) + '/' + anatomy + '/' + each_file)

    bam_folder = os.listdir(os.path.expanduser(config['input']['bam']))
    bam_file_path = None
    for each_file in bam_folder:
        if file_id in each_file and each_file.endswith('.bam'):
            bam_file_path = os.path.abspath(os.path.expanduser(config['input']['bam']) + '/' + each_file)

    return repred_file_path, bam_file_path


def main(reference_type, anatomy, sample_type, patient_id, file_id):
    print('starting')

    config = get_config_from_file()
    # TODO - allow for multiple labels - eg : pos, unlabeled - pos - negative, pos
    label = config['input']['label']
    # TODO - make the reference subdirectories using the writer class
    output_folder_path = os.path.realpath(config['output']['root'])
    reference_path, transposcope_path, logs_path = create_output_folder_structure(output_folder_path, reference_type,
                                                                                  label, anatomy, sample_type,
                                                                                  patient_id)
    setup_logging(logging_folder=logs_path)
    logging.info('welcome to TranspoScope')

    repred_path, bam_path = find_files(file_id, anatomy, reference_type, config)
    logging.info(bam_path)
    repred_reader = RepredReader(repred_path)
    logging.info('loading bam')
    bam_handler = BamHandler(bam_path)
    fasta_handler = FastaHandler(os.path.expanduser(config['line1']['fasta']),
                                 os.path.expanduser(config['reference']['hg']), config['line1']['start'],
                                 config['line1']['end'])
    insertions = []
    reads_dictionary = ReadsDict()
    logging.info('finding target regions')
    for insertion_stats in repred_reader.read_lines():
        if insertion_stats.H30_label == LABEL[label]:
            temp_insertion = Insertion(named_tuple=insertion_stats)
            reads_in_region = bam_handler.fetch_reads_in_region(temp_insertion)
            reads_dictionary += reads_in_region
            temp_insertion.keys_of_reads_in_target_region = reads_in_region.keys()
            insertions.append(temp_insertion)
            # logging.info(fasta_handler.generate_fasta_sequence(temp_insertion))
    logging.info('finding pairs')
    for read in bam_handler.all_reads():
        if read.query_name in reads_dictionary:
            reads_dictionary.insert(read)
    logging.info("Processing insertions")
    file_writer = FileWriter()
    realigner = Realigner(reference_path, config['bowtie']['fastaIndexed'], config['bowtie']['realign'])
    classifier = ReadClassifier(int(config['line1']['start']),
                                int(config['line1']['end']), transposcope_path)
    gene_handler = GeneHandler(config['reference']['refFlat'])
    insertions.sort(key=lambda x: x.CHROMOSOME)
    heading_table = {'Heading': ["ID", "Gene",
                                 "Probability"], 'Data': []}
    for insertion in insertions:
        file_name = "{i.CHROMOSOME}_{i.START}-{i.END}".format(i=insertion)
        insertion.fasta_string = fasta_handler.generate_fasta_sequence(insertion)
        fasta_path = file_writer.write_fasta(reference_path, file_name, insertion.fasta_string,
                                             ">{i.CHROMOSOME}_{i.START}-{i.END}\n".format(i=insertion))
        logging.info(file_name)
        fastq1_path, fastq2_path = file_writer.write_fastq(reference_path, reads_dictionary, file_name,
                                                           insertion.keys_of_reads_in_target_region)
        sorted_bam_path = realigner.realign(fasta_path, fastq1_path, fastq2_path, file_name)
        gene_info = gene_handler.find_nearest_gene(insertion.CHROMOSOME, insertion.INSERTION_SITE)
        # TODO - use a format string for this
        heading_table['Data'].append([
            str(insertion.CHROMOSOME) + '-' + str(insertion.CLIP_START) + '(' + str(
                insertion.CLIP_END - insertion.CLIP_START) + ')',
            gene_info,
            str(round(insertion.PRED, 2))
        ])
        #     TODO - use realignment files to create JSON
        classifier.classify_insertion(insertion, sorted_bam_path)
        #     TODO - write out bedfile
        #     TODO - delete local realignment files (test this)
        if config['output']['removeAlignmentFiles'] is 'Y':
            if os.path.exists(fasta_path):
                shutil.rmtree(fasta_path)
            if os.path.exists(sorted_bam_path):
                shutil.rmtree(sorted_bam_path)
    file_writer.write_json(os.path.join(transposcope_path, 'table_info.json.gz.txt'), heading_table)


if __name__ in '__main__':
    main('fp', 'pancreatic', 'normal', 'A152', 's5_9_SL31275')
    # reference_type, anatomy, sample_type, patient_id
