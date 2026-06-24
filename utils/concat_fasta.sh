#!/bin/bash
# concat_fasta.sh
#
# Concatenates the RNACentral lncRNA FASTA with the four bedtools getfasta-extracted
# sequence files into a single master database FASTA file.
# All sequences are on the mRatBN7.2 coordinate system at this stage.
#
# Input files:
#   - lncRNA_data_cleaned.fasta         (RNACentral, mRatBN7.2 native)
#   - transcripts_bg200.rat.rn7_sequences.fasta  (E-MTAB-867, rn4 -> rn7)
#   - GSE159668_lncRNA_rn7_sequences.fasta       (GSE159668, rn6 -> rn7)
#   - Karri_Waxman_rn7_sequences.fasta           (Karri & Waxman 2020, rn6 -> rn7)
#   - GSE227317_lncRNA_rn7_sequences.fasta       (GSE227317, rn6 -> rn7)
#
# Output:
#   rat_lncRNA_master_database.fasta
#
# Usage:
#   bash concat_fasta.sh

set -euo pipefail

OUTPUT=rat_lncRNA_master_database.fasta

cat \
    lncRNA_data_cleaned.fasta \
    transcripts_bg200.rat.rn7_sequences.fasta \
    GSE159668_lncRNA_rn7_sequences.fasta \
    Karri_Waxman_rn7_sequences.fasta \
    GSE227317_lncRNA_rn7_sequences.fasta \
    > "$OUTPUT"

echo "Done. Total sequences: $(grep -c '^>' "$OUTPUT")"
echo "Output: $OUTPUT"