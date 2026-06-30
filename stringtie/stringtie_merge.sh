#!/bin/bash
#SBATCH --job-name=stringtie_merge
#SBATCH --output=/mnt/scratch2/users/40500972/mapping/stringtie/stringtie_merge.log
#SBATCH --error=/mnt/scratch2/users/40500972/mapping/stringtie/stringtie_merge.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8G
#SBATCH --partition=k2-medpri
#SBATCH --mail-user=pbrennan17@qub.ac.uk
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --chdir=/mnt/scratch2/users/40500972/mapping/stringtie

module load stringtie/1.3.6

OUT=/mnt/scratch2/users/40500972/mapping/stringtie

stringtie --merge \
    -o $OUT/consensus_annotation.gtf \
    $OUT/PN0616_0001_S11_L001.gtf \
    $OUT/PN0616_0002_S12_L001.gtf \
    $OUT/PN0616_0003_S13_L001.gtf \
    $OUT/PN0616_0004_S14_L001.gtf \
    $OUT/PN0647_007_S1_L001.gtf \
    $OUT/PN0647_008_S2_L001.gtf \
    $OUT/PN0647_009_S3_L001.gtf \
    $OUT/PN0647_010_S4_L001.gtf \
    $OUT/PN0647_011_S5_L001.gtf \
    $OUT/PN0647_012_S6_L001.gtf \
    $OUT/PN0647_013_S7_L001.gtf \
    $OUT/PN0647_014_S8_L001.gtf

echo "Merge complete. Transcripts in consensus GTF:"
grep -c $'\ttranscript\t' $OUT/consensus_annotation.gtf