#!/bin/bash
#SBATCH --job-name=Dedup_lncRNA
#SBATCH --output=/mnt/scratch2/users/40500972/deduplication/dedup.log
#SBATCH --mail-user=pbrennan17@qub.ac.uk
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --partition=k2-lowpri
#SBATCH --chdir=/mnt/scratch2/users/40500972/deduplication/

/mnt/scratch2/users/40500972/cd-hit-v4.8.1-2019-0228/cd-hit-est \
    -i rat_lncRNA_master_database_clean.fasta \
    -o rat_lncRNA_master_database_dedup95.fasta \
    -c 0.95 \
    -n 8 \
    -T 8 \
    -M 64000 \
    -d 0 \
    -aS 0.80