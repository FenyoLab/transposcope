#!/bin/bash
#$ -S /bin/bash
# bash runBowtie2v223PE.sh ./FAST/ovariant/918/918_T/fasta/chr5_41600126-41600121.indexed.fasta ./FAST/ovariant/918/918_T/fastq/chr5_41600126-41600121.R1.fastq ./FAST/ovariant/918/918_T/fastq/chr5_41600126-41600121.R2.fastq ./FAST/ovariant/918/918_T/sam/chr5_41600126-41600121.sam 2 1000 FALSE
# TODO - add check for path, throw error if not found
#bowtie2path=/Users/markgrivainis/Documents/NYU_Lab/tipseq_hunter/include/bowtie2-2.2.7
bowtie2path=/ifs/home/grivam01/tipseq_hunter/include/bowtie2-2.2.7
refindex=$1
read1fastq=$2
read2fastq=$3
outsam=$4
kvalue=$5
Xvalue=$6
ifkvalue=$7
echo "refindex=$refindex"
echo "read1fastq=$read1fastq"
echo "read2fastq=$read2fastq"
echo "outsam=$outsam"
echo "kvalue=$kvalue"
echo "Xvalue=$Xvalue"
echo "ifkvalue=$ifkvalue"
ifkvalueT=TRUE
ifkvalueF=FALSE
if [ $ifkvalue == $ifkvalueT ]; then
	$bowtie2path/bowtie2 -k $kvalue -X $Xvalue --local --phred33 --sensitive -p $NSLOTS -x $refindex -1 $read1fastq -2 $read2fastq -S $outsam
elif [ $ifkvalue == $ifkvalueF ]; then
	$bowtie2path/bowtie2 -X $Xvalue --local --phred33 --sensitive -p 6 -x $refindex -1 $read1fastq -2 $read2fastq -S $outsam
	# $bowtie2path/bowtie2 -X $Xvalue --local --phred33 --sensitive -p $NSLOTS -x $refindex -1 $read1fastq -2 $read2fastq -S $outsam
else
	echo "Your ifkvalue-key is not correct. It should be \"TRUE\" or \"FALSE\"." 1>&2;
	echo "Usage: runBowtie2v223PEShell.sh ref-genome-index in-fastq-path out-alignment-path k-value(1) X-value(800) if-k-value(TRUE/FALSE)" 1>&2;
	exit 2;
fi