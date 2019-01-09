import base64
import gzip
import json

# TODO - write tests for this
import os


class FileWriter:
    @staticmethod
    def write_json(file_path, data):
        with open(file_path, 'wb+') as json_out_fp:
            json_from_dict = json.dumps(data)
            gz = gzip.compress(str.encode(json_from_dict))
            b64 = base64.standard_b64encode(gz)
            json_out_fp.write(b64)

    @staticmethod
    def write_fasta(file_path, file_name, fasta_string, fasta_header):
        fasta_path = os.path.join(file_path, 'fasta', file_name + '.fasta')
        fa = open(fasta_path, 'w')
        fa.write(fasta_header)
        fa.write(fasta_string)
        fa.close()
        return fasta_path

    # TODO - Make a single reverse complement function (fasta_handler)
    @staticmethod
    def reverse_complement(sequence):
        reverse_sequence = sequence[::-1]
        complement_sequence = ''.join(
            {
                'A': 'T',
                'C': 'G',
                'G': 'C',
                'T': 'A',
                'N': 'N'
            }[x] for x in reverse_sequence
        )
        return complement_sequence

    def write_fastq(
            self,
            file_path,
            reads_dictionary,
            file_name,
            keys_of_reads_in_target_region
    ):
        fastq1_path = os.path.join(file_path, 'fastq', file_name + '.R1.fastq')
        fastq2_path = os.path.join(file_path, 'fastq', file_name + '.R2.fastq')
        fastq_read1 = open(fastq1_path, 'w')
        fastq_read2 = open(fastq2_path, 'w')
        for read_key in keys_of_reads_in_target_region:
            read_pair = reads_dictionary[read_key]
            fastq_read1.write(
                "@{query_name} 1:N:0:1\n{query_sequence}\n+"
                "\n{query_quality}\n".format(
                    query_name=read_pair[0].query_name,
                    query_sequence=read_pair[0].query_sequence if
                    not read_pair[
                        0].is_reverse else self.reverse_complement(
                        read_pair[0].query_sequence),
                    query_quality=''.join(chr(x + 33) for x
                                          in read_pair[0].query_qualities)
                ))
            fastq_read2.write(
                "@{query_name} 2:N:0:1\n{query_sequence}\n+"
                "\n{query_quality}\n".format(
                    query_name=read_pair[1].query_name,
                    query_sequence=read_pair[1].query_sequence if
                    not read_pair[
                        1].is_reverse else self.reverse_complement(
                        read_pair[1].query_sequence),
                    query_quality=''.join(chr(x + 33) for x
                                          in read_pair[1].query_qualities)
                ))
        fastq_read1.close()
        fastq_read2.close()
        return fastq1_path, fastq2_path
