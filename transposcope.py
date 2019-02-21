import json
import logging.config
import os
import shutil
import sys

from src.transposcope.bam_handler import BamHandler
from src.transposcope.constants import LABEL
from src.transposcope.fasta_handler import FastaHandler
from src.transposcope.file_writer import FileWriter
from src.transposcope.gene_handler import GeneHandler
from src.transposcope.insertion import Insertion
from src.transposcope.insertion_sites_reader import InsertionSiteReader
from src.transposcope.read_classifier import ReadClassifier
from src.transposcope.reads_dict import ReadsDict
from src.transposcope.realigner import Realigner


# from memory_profiler import profile


def get_config_from_file():
    with open('./config/config_hg19.json') as json_data_file:
    # with open('./config/config.json') as json_data_file:
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
            (
                config
                ["handlers"]
                ["info_file_handler"]
                ["filename"]
            ) = os.path.join(logging_folder, 'info.log')
            (
                config
                ["handlers"]
                ["error_file_handler"]
                ["filename"]
            ) = os.path.join(logging_folder, 'error.log')
        logging.config.dictConfig(config)

    else:
        logging.basicConfig(level=default_level)


def create_output_folder_structure(
        output_folder_path,
        reference_type,
        label,
        anatomy,
        sample_type,
        patient_id
):
    reference_path = os.path.join(
        output_folder_path,
        'ref',
        reference_type,
        anatomy,
        patient_id,
        '{}-{}-{}'.format(
            label,
            patient_id,
            sample_type
        )
    )
    transposcope_path = os.path.join(
        output_folder_path,
        'json',
        '{}_{}'.format(
            anatomy,
            reference_type
        ),
        patient_id,
        '{}-{}-{}'.format(
            label,
            patient_id,
            sample_type
        )
    )
    logs_path = os.path.join(
        output_folder_path,
        'logs',
        reference_type,
        '{}-{}-{}'.format(
            label,
            patient_id,
            sample_type
        )
    )
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


def main(reference_type,
         anatomy,
         sample_type,
         patient_id,
         file_id,
         bam_name,
         insertion_list
         ):
    print('starting')

    config = get_config_from_file()
    # TODO - allow for multiple labels
    #  - eg : pos, unlabeled - pos - negative, pos
    label = (
        config
        ['input']
        ['label']
    )
    # TODO - make the reference subdirectories using the writer class
    output_folder_path = os.path.realpath(config['output']['root'])
    (
        reference_path,
        transposcope_path,
        logs_path
    ) = create_output_folder_structure(
        output_folder_path,
        reference_type,
        label,
        anatomy,
        sample_type,
        patient_id
    )
    setup_logging(logging_folder=logs_path)
    logging.info('--TranspoScope--')

    # (
    #     repred_path,
    #     bam_path
    # ) = find_files(
    #     file_id,
    #     anatomy,
    #     reference_type,
    #     config
    # )
    bam_folder = os.path.expanduser(
        config['input']['bam']
    )
    bam_path = os.path.join(
        bam_folder,
        bam_name
    )
    insertion_list_folder = os.path.expanduser(
        config['input']['insertion_table_dir']
    )
    insertion_list_path = os.path.join(
        insertion_list_folder,
        insertion_list
    )
    logging.info(bam_path)
    print('ilp', insertion_list_path)
    insertion_sites_reader = InsertionSiteReader(
        insertion_list_path
    )
    logging.info('loading bam')
    bam_handler = BamHandler(bam_path)
    fasta_handler = FastaHandler(
        os.path.expanduser(
            config['line1']['fasta']
        ),
        os.path.expanduser(
            config['reference']['hg']
        )
    )
    insertions = []

    reads_dictionary = {True: ReadsDict(),
                        False: ReadsDict()
                        }
    logging.info('finding target regions')
    for insertion_stats in insertion_sites_reader.read_lines():
        temp_insertion = Insertion(
            named_tuple=insertion_stats
        )
        reads_in_region = bam_handler.fetch_reads_in_region(
            temp_insertion
        )
        reads_dictionary[
            temp_insertion.THREE_PRIME
        ] += reads_in_region
        temp_insertion.read_keys_in_target_region = reads_in_region.keys()
        insertions.append(temp_insertion)
    logging.info('finding pairs')
    for read in bam_handler.all_reads():
        if read.query_name in reads_dictionary[True]:
            reads_dictionary[True].insert(read)

        if read.query_name in reads_dictionary[False]:
            reads_dictionary[False].insert(read)

    logging.info("Processing insertions")
    file_writer = FileWriter()
    realigner = Realigner(
        reference_path,
        config['bowtie']['fastaIndexed'],
        config['bowtie']['realign']
    )
    classifier = ReadClassifier(transposcope_path)
    gene_handler = GeneHandler(config['reference']['refFlat'])
    insertions.sort(key=lambda x: x.CHROMOSOME)
    heading_table = {
        'Heading': ("ID", "Gene", "Probability"),
        'data': []}

    for insertion in insertions:
        file_name = "{i.CHROMOSOME}_{i.START}-{i.END}".format(i=insertion)
        insertion.fasta_string = fasta_handler.generate_fasta_sequence(
            insertion
        )

        fasta_path = file_writer.write_fasta(
            reference_path,
            file_name,
            insertion.fasta_string,
            ">{i.CHROMOSOME}_{i.START}-{i.END}\n".format(i=insertion))
        logging.info(file_name)

        fastq1_path, fastq2_path = file_writer.write_fastq(
            reference_path,
            reads_dictionary[insertion.THREE_PRIME],
            file_name,
            insertion.read_keys_in_target_region
        )
        sorted_bam_path = realigner.realign(
            fasta_path,
            fastq1_path,
            fastq2_path,
            file_name
        )

        # TODO - add the option to not add gene information
        gene_info = gene_handler.find_nearest_gene(
            insertion.CHROMOSOME,
            insertion.INSERTION_SITE
        )

        # heading_table['Data']\
        if insertion.THREE_PRIME:
            end = '3'
        else:
            end = '5'
        heading_table['data'].append(
            [
                '{}-{}({})'.format(
                    insertion.CHROMOSOME,
                    insertion.CLIP_START,
                    end
                ),
                gene_info,
                "{:.2f}".format(insertion.PRED)
            ]
        )
        classifier.classify_insertion(
            insertion,
            sorted_bam_path
        )
    #     TODO - write out bedfile
    #     TODO - write out index file
    #     TODO - delete local realignment files (test this)
    #     TODO - add fastq to removal
    if config['output']['removeAlignmentFiles'] is 'Y':
        if os.path.exists(fasta_path):
            shutil.rmtree(os.path.dirname(fasta_path))
        if os.path.exists(sorted_bam_path):
            shutil.rmtree(os.path.dirname(sorted_bam_path))

    file_writer.write_json(
        os.path.join(
            transposcope_path,
            'table_info.json.gz.txt'
        ),
        heading_table
    )


if __name__ in '__main__':
    main('fp',
         'Ovarian',
         'test_normal_vs_tumor', '918', 'CTTGTA',
         'CTTGTA.fastq.cleaned.fastq.pcsort.bam',
         'CTTGTA.tab')
# main('fp',
#      'test_anatomy',
#      'test_type', 'test_patient_name', 'test_patient_id',
#      'A-Normal_GTCGTAGA_L003001.fastq.gz.cleaned.fastq.pcsort.bam',
#      'A-Normal_GTCGTAGA_L003001_all.tab')
    # main('fp',
    #      'test_anatomy',
    #      'test_melt', 'test_patient_name', 'test_patient_id',
    #      'NA19240.bam',
    #      'LINE1.tab')
    # reference_type, anatomy, sample_type, patient_id
