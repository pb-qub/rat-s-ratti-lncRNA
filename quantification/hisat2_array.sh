#!/bin/bash
#SBATCH --job-name=hisat2_array
#SBATCH --array=1-12
#SBATCH --output=/mnt/scratch2/users/40500972/mapping/bam/hisat2_array_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --partition=k2-hipri
#SBATCH --mail-user=pbrennan17@qub.ac.uk
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --chdir=/mnt/scratch2/users/40500972/mapping/bam

# Load the required modules
module load hisat2/2.2.1
module load python3/3.8.20/gcc-9.3.0
module load apps/samtools/1.17/gcc-14.1.0
module load stringtie/1.3.6

# Specify the path to the samples.txt config file
samples=/mnt/scratch2/users/40500972/mapping/samples.txt

# Extract the sample name corresponding to the current SLURM_ARRAY_TASK_ID
SampleName=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $2}' $samples)

# Specify paths
FASTQ=/mnt/scratch2/users/40500972/mapping/fastq
INDEX=/mnt/scratch2/users/40500972/deduplication/RatlncRNA_v2.hs2
CONSENSUS=/mnt/scratch2/users/40500972/mapping/stringtie/consensus_annotation.gtf
STRINGTIE_OUT=/mnt/scratch2/users/40500972/mapping/stringtie/quantification

# Run HISAT2 for the current sample, pipe output through samtools to produce sorted BAM
hisat2 -x $INDEX \
    -1 $FASTQ/${SampleName}_R1_001.fastq.gz \
    -2 $FASTQ/${SampleName}_R2_001.fastq.gz \
    -p 8 \
    --dta \
    2> ${SampleName}.hisat2.log \
| samtools sort -@ 8 -o ${SampleName}.sorted.bam

# Index the sorted BAM file
samtools index ${SampleName}.sorted.bam

# Run StringTie with -G to quantify expression against the consensus annotation
# -e restricts output to only transcripts in the reference GTF
# -B outputs Ballgown formatted files for downstream DESeq2 analysis
# -A outputs a gene-level abundance table per sample
stringtie ${SampleName}.sorted.bam \
    -G $CONSENSUS \
    -e \
    -B \
    -p 8 \
    -o $STRINGTIE_OUT/${SampleName}/${SampleName}.gtf \
    -A $STRINGTIE_OUT/${SampleName}/${SampleName}_gene_abund.tab