#!/bin/bash
# rename_chromosomes.sh
#
# Standardises chromosome naming in lifted BED files from UCSC-style
# (chr1, chr2, ...) to NCBI-style (NC_051336.1, NC_051337.1, ...)
# using a custom mapping table, required for compatibility with the
# mRatBN7.2 reference genome FASTA downloaded from NCBI (GCF_015227675.2).
#
# The mapping table (chr_name_mapping.txt) is a two-column tab-separated
# file with UCSC names in column 1 and NCBI accessions in column 2,
# generated from the mRatBN7.2 FASTA headers.
#
# Usage:
#   bash rename_chromosomes.sh <mapping_file> <input.bed> <output.bed>
#
# Example (single file):
#   bash rename_chromosomes.sh chr_name_mapping.txt Karri_Waxman_rn7.bed Karri_Waxman_rn7_ncbi.bed
#
# To process all lifted BED files at once:
#   for bedfile in transcripts_bg200.rat.rn7.bed GSE159668_lncRNA_rn7.bed Karri_Waxman_rn7.bed GSE227317_lncRNA_rn7.bed; do
#       outfile="${bedfile%.bed}_ncbi.bed"
#       bash rename_chromosomes.sh chr_name_mapping.txt "$bedfile" "$outfile"
#   done

set -euo pipefail

MAPPING=${1:?Usage: $0 <mapping_file> <input.bed> <output.bed>}
INPUT=${2:?Usage: $0 <mapping_file> <input.bed> <output.bed>}
OUTPUT=${3:?Usage: $0 <mapping_file> <input.bed> <output.bed>}

echo "Mapping file: $MAPPING"
echo "Input:  $INPUT ($(wc -l < "$INPUT") records)"

awk 'NR==FNR{map[$1]=$2; next} {if($1 in map) $1=map[$1]; print}' \
    OFS="\t" "$MAPPING" "$INPUT" > "$OUTPUT"

echo "Output: $OUTPUT ($(wc -l < "$OUTPUT") records)"
echo "=== Done ==="
