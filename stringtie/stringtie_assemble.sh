#!/bin/bash
#SBATCH --job-name=stringtie_assemble
#SBATCH --output=/mnt/scratch2/users/40500972/mapping/stringtie/stringtie_assemble.log
#SBATCH --error=/mnt/scratch2/users/40500972/mapping/stringtie/stringtie_assemble.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --partition=k2-medpri
#SBATCH --mail-user=pbrennan17@qub.ac.uk
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --chdir=/mnt/scratch2/users/40500972/mapping/stringtie

module load stringtie/1.3.6

BAM=/mnt/scratch2/users/40500972/mapping/bam
OUT=/mnt/scratch2/users/40500972/mapping/stringtie
THREADS=8

SAMPLES=(
    PN0616_0001_S11_L001
    PN0616_0002_S12_L001
    PN0616_0003_S13_L001
    PN0616_0004_S14_L001
    PN0647_007_S1_L001
    PN0647_008_S2_L001
    PN0647_009_S3_L001
    PN0647_010_S4_L001
    PN0647_011_S5_L001
    PN0647_012_S6_L001
    PN0647_013_S7_L001
    PN0647_014_S8_L001
)

echo "=== StringTie per-sample assembly started: $(date) ==="

for SAMPLE in "${SAMPLES[@]}"; do
    echo "--- Assembling $SAMPLE: $(date) ---"

    stringtie \
        $BAM/${SAMPLE}.sorted.bam \
        -p $THREADS \
        -o $OUT/${SAMPLE}.gtf \
        -l ${SAMPLE}

    echo "Done: $SAMPLE"
done

echo "=== All per-sample assembly complete: $(date) ==="