#!/bin/bash
# gtf_to_bed_standard.sh
#
# Converts a standard GTF file (containing transcript lines) to BED6 format.
# Adds 'chr' prefix to chromosome identifiers if not already present,
# which is required for UCSC liftOver compatibility.
#
# Used for: GSE159668 GTF (Rnor_6.0)
#
# Usage:
#   bash gtf_to_bed_standard.sh <input.gtf> <output.bed>
#
# Example:
#   bash gtf_to_bed_standard.sh GSE159668_lncRNA.gtf GSE159668_lncRNA_rn6.bed

set -euo pipefail

INPUT=${1:?Usage: $0 <input.gtf> <output.bed>}
OUTPUT=${2:?Usage: $0 <input.gtf> <output.bed>}

echo "Input: $INPUT"
echo "Output: $OUTPUT"

# Add chr prefix to chromosome names if not already present
TMP_GTF="${INPUT%.gtf}_chr.gtf"
awk '{if($0 !~ /^#/) $1="chr"$1; print}' OFS="\t" "$INPUT" > "$TMP_GTF"
echo "chr prefix added -> $TMP_GTF"

# Extract transcript lines and convert to BED6
awk '$3=="transcript"' "$TMP_GTF" | \
awk '{
    # Extract transcript_id
    for(i=1; i<=NF; i++) {
        if($i=="transcript_id") t=$(i+1)
    }
    gsub(/;/, "", t)
    gsub(/"/, "", t)
    print $1"\t"$4-1"\t"$5"\t"t"\t0\t"$7
}' > "$OUTPUT"

echo "Done. Transcripts written: $(wc -l < "$OUTPUT")"
