#!/bin/bash
#SBATCH --job-name=hisat2_mapping
#SBATCH --output=/mnt/scratch2/users/40500972/mapping/hisat2_mapping.log
#SBATCH --error=/mnt/scratch2/users/40500972/mapping/hisat2_mapping.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --partition=k2-hipri
#SBATCH --mail-user=pbrennan17@qub.ac.uk
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --chdir=/mnt/scratch2/users/40500972/mapping

# Modules
module load hisat2/2.2.1
module load python3/3.8.20/gcc-9.3.0
module load apps/samtools/1.17/gcc-14.1.0

# Paths
INDEX=/mnt/scratch2/users/40500972/deduplication/RatlncRNA.hs2
FASTQ=/mnt/scratch2/users/40500972/mapping/fastq
BAM=/mnt/scratch2/users/40500972/mapping/bam
THREADS=8

# R1 files — R2 is derived by swapping _R1_ for _R2_ in the filename
R1_FILES=(
    PN0616_0001_S11_L001_R1_001.fastq.gz
    PN0616_0002_S12_L001_R1_001.fastq.gz
    PN0616_0003_S13_L001_R1_001.fastq.gz
    PN0616_0004_S14_L001_R1_001.fastq.gz
    PN0647_007_S1_L001_R1_001.fastq.gz
    PN0647_008_S2_L001_R1_001.fastq.gz
    PN0647_009_S3_L001_R1_001.fastq.gz
    PN0647_010_S4_L001_R1_001.fastq.gz
    PN0647_011_S5_L001_R1_001.fastq.gz
    PN0647_012_S6_L001_R1_001.fastq.gz
    PN0647_013_S7_L001_R1_001.fastq.gz
    PN0647_014_S8_L001_R1_001.fastq.gz
)

echo "=== HISAT2 mapping started: $(date) ==="

for R1 in "${R1_FILES[@]}"; do
    R2="${R1/_R1_/_R2_}"
    SAMPLE="${R1%%_R1*}"

    echo "--- Mapping $SAMPLE: $(date) ---"

    hisat2 \
        -x $INDEX \
        -1 $FASTQ/$R1 \
        -2 $FASTQ/$R2 \
        -p $THREADS \
        --dta \
        2> $BAM/${SAMPLE}.hisat2.log \
    | samtools sort -@ $THREADS -o $BAM/${SAMPLE}.sorted.bam

    samtools index $BAM/${SAMPLE}.sorted.bam

    echo "Done: $SAMPLE"
done

echo "=== All mapping complete: $(date) ==="