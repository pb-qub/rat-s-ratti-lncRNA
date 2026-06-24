#!/bin/bash
#SBATCH --job-name=HISAT2_build
#SBATCH --output=/mnt/scratch2/users/40500972/deduplication/HiSatBuild.log
#SBATCH --mail-user=pbrennan17@qub.ac.uk
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8G
#SBATCH --partition=k2-lowpri
#SBATCH --chdir=/mnt/scratch2/users/40500972/deduplication/

module load hisat2/2.2.1
module load python3/3.8.20/gcc-9.3.0

hisat2-build \
    -p 4 \
    rat_lncRNA_master_database_dedup95.fasta \
    RatlncRNA.hs2