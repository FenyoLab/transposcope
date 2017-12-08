import os

from transposcope.fasta_handler import FastaHandler
from transposcope.file_writer import FileWriter
from transposcope.gene_handler import GeneHandler
from transposcope.insertion import Insertion
from transposcope.read_classifier import ReadClassifier

transposcope_path = os.path.join('output', 'json', 'wgs_five_prime', 'NA12878',
                                 'positive-NA12878-normal')

fasta_handler = FastaHandler(
    os.path.expanduser("~/PycharmProjects/transposcope_backend/reference/line1Fa/Homo_sapiens_L1.L1HS.fa"),
    os.path.expanduser("~/PycharmProjects/transposcope_backend/reference/chromFa/"),
    0, 160)
file_writer = FileWriter()
gene_handler = GeneHandler(os.path.expanduser("~/PycharmProjects/transposcope_backend/reference/refFlat.txt"))

insertion = Insertion(chromosome="chr1", target_start=86392750 - 1900, target_end=86392750, clip_start=86392750,
                      clip_end=86392750, pred=-1, clip_sc=-1, line1_end="start")
fasta_handler.generate_fasta_sequence(insertion, "start")
heading_table = {'Heading': ["ID", "Gene",
                             "Probability"], 'Data': []}
gene_info = gene_handler.find_nearest_gene(insertion.CHROMOSOME, insertion.INSERTION_SITE)
heading_table['Data'].append([
    str(insertion.CHROMOSOME) + '-' + str(insertion.CLIP_START) + '(' + str(
        insertion.CLIP_END - insertion.CLIP_START) + ')',
    gene_info,
    str(round(insertion.PRED, 2))
])
classifier = ReadClassifier(0,
                            160, transposcope_path)
classifier.classify_insertion(insertion, "./input/bam_sorted/chr1_86390849-86392749.sort.bam")
file_writer.write_json(os.path.join(transposcope_path, 'table_info.json.gz.txt'), heading_table)
