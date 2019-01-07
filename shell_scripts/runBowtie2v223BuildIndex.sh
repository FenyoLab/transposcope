#!/bin/bash
#$ -S /bin/bash
# bash runBowtie2v223BuildIndex.sh ./FAST/ovariant/918/918_T/fasta/chr5_41600126-41600121.fasta ./FAST/ovariant/918/918_T/fasta/chr5_41600126-41600121.indexed.fasta
# TODO - add check for path, throw error if not found
#bowtie2path=/Users/markgrivainis/Documents/NYU_Lab/tipseq_hunter/include/bowtie2-2.2.7
bowtie2path=/home/mark/miniconda3/envs/transposcope/bin/
infasta=$1
outfasta=$2
echo "infasta=$infasta"
echo "outfasta=$outfasta"
$bowtie2path/bowtie2-build $infasta $outfasta
#ls
#$bowtie2path/bowtie2-build ./fasta/chr1_41674114-41674119.fasta ./fasta/chr1_41674114-41674119.indexed.fasta