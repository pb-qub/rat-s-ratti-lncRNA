#!/bin/bash
# getfasta.sh
#
# Extracts lncRNA sequences from the mRatBN7.2 reference genome FASTA
# using bedtools getfasta, for all four lifted and chromosome-renamed BED files.
# Strand-aware extraction (-s flag) ensures correct orientation of
# reverse-strand transcripts.
#
# Requirements:
#   - bedtools v2.31.1
#   - mRatBN7.2 reference genome FASTA (GCF_015227675.2_mRatBN7.2_genomic.fna)
#   - NCBI-named BED files (output of rename_chromosomes.sh)
#
# Usage:
#   bash getfasta.sh
#
# Output:
#   One FASTA file per BED file, named <dataset>_sequences.fasta

set -euo pipefail

GENOME=GCF_015227675.2_mRatBN7.2_genomic.fna

for bedfile in \
    transcripts_bg200.rat.rn7_ncbi.bed \
    GSE159668_lncRNA_rn7_ncbi.bed \
    Karri_Waxman_rn7_ncbi.bed \
    GSE227317_lncRNA_rn7_ncbi.bed; do

    outfile="${bedfile%_ncbi.bed}_sequences.fasta"
    echo "Processing $bedfile..."

    bedtools getfasta \
        -fi "$GENOME" \
        -bed "$bedfile" \
        -name \
        -s \
        -fo "$outfile"

    echo "Done -> $outfile"
    echo "Sequences extracted: $(grep -c '>' "$outfile")"
    echo "---"
done

echo "=== All sequences extracted ==="
