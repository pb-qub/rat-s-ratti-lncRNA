#!/bin/bash
# qc_check.sh
#
# Performs quality checks on the rat lncRNA master FASTA database prior
# to deduplication. Checks include:
#   - Total sequence count
#   - Duplicate headers
#   - Empty sequences
#   - Invalid nucleotide characters (non A/C/G/T/N)
#   - Sequence length distribution (min, max)
#   - N-rich sequences (beginning with 4+ consecutive Ns)
#
# Usage:
#   bash qc_check.sh <input.fasta>
#
# Example:
#   bash qc_check.sh rat_lncRNA_master_database_filtered.fasta

set -euo pipefail

INPUT=${1:?Usage: $0 <input.fasta>}

echo "=== QC Check: $INPUT ==="
echo ""

# Total sequences
echo "--- Total sequences ---"
grep -c "^>" "$INPUT"

# Duplicate headers
echo ""
echo "--- Duplicate headers ---"
grep "^>" "$INPUT" | sort | uniq -d | wc -l

# Empty sequences (header followed immediately by another header or end of file)
echo ""
echo "--- Empty sequences ---"
awk '/^>/{if(seq=="") count++; seq=""} !/^>/{seq=seq$0} END{if(seq=="") count++; print count+0}' "$INPUT"

# Invalid nucleotide characters
echo ""
echo "--- Invalid nucleotide characters (non A/C/G/T/N) ---"
grep -v "^>" "$INPUT" | grep -P "[^ACGTNacgtn\n]" | wc -l

# Sequence length distribution
echo ""
echo "--- Sequence length distribution (min / max) ---"
awk '/^>/{if(seq!="") print length(seq); seq=""} !/^>/{seq=seq$0} END{if(seq!="") print length(seq)}' "$INPUT" | \
    awk 'BEGIN{min=999999999; max=0}
         {if($1<min) min=$1; if($1>max) max=$1}
         END{print "Min: "min"\nMax: "max}'

# N-rich sequences (starting with 4+ Ns)
echo ""
echo "--- N-rich sequences (starting with NNNN+) ---"
awk '/^>/{header=$0; next} /^NNNN/{print header}' "$INPUT" | wc -l

echo ""
echo "=== QC complete ==="
