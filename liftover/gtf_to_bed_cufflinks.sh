#!/bin/bash
# gtf_to_bed_cufflinks.sh
#
# Converts a Cufflinks-format GTF (exon lines only, no transcript lines)
# to BED6 format by collapsing exons per transcript_id.
# Transcript coordinates are derived by taking the min start and max end
# across all exons belonging to each transcript.
#
# Used for: Karri & Waxman 2020 GTF (Rnor_6.0)
#
# Usage:
#   bash gtf_to_bed_cufflinks.sh <input.gtf> <output.bed>
#
# Example:
#   bash gtf_to_bed_cufflinks.sh Rat_lncRNA_GTF_Karri_Waxman_ToxSci_2020.gtf Karri_Waxman_rn6.bed

set -euo pipefail

INPUT=${1:?Usage: $0 <input.gtf> <output.bed>}
OUTPUT=${2:?Usage: $0 <input.gtf> <output.bed>}

echo "Input: $INPUT"
echo "Output: $OUTPUT"

awk '$3=="exon"' "$INPUT" | \
awk '{
    for(i=1; i<=NF; i++) {
        if($i=="transcript_id") t=$(i+1)
    }
    gsub(/;/, "", t)
    gsub(/"/, "", t)
    if(!(t in start) || $4-1 < start[t]) start[t]=$4-1
    if(!(t in end) || $5 > end[t]) end[t]=$5
    chrom[t]=$1
    strand[t]=$7
}
END {
    for(t in start) print chrom[t]"\t"start[t]"\t"end[t]"\t"t"\t0\t"strand[t]
}' > "$OUTPUT"

echo "Done. Transcripts written: $(wc -l < "$OUTPUT")"
