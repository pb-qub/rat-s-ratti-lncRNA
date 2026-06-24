#!/bin/bash
# liftover_rn6_rn7.sh
#
# Performs a single-hop coordinate liftover from Rnor_6.0 (rn6) to
# mRatBN7.2 (rn7) using the UCSC liftOver tool.
#
# Used for: Karri & Waxman 2020, GSE159668, GSE227317 BED files
#
# Requirements:
#   - liftOver binary in the same directory or on PATH
#   - rn6ToRn7.over.chain.gz
#
# Usage:
#   bash liftover_rn6_rn7.sh <input_rn6.bed> <output_rn7.bed>
#
# Example:
#   bash liftover_rn6_rn7.sh Karri_Waxman_rn6.bed Karri_Waxman_rn7.bed

set -euo pipefail

INPUT=${1:?Usage: $0 <input_rn6.bed> <output_rn7.bed>}
OUTPUT=${2:?Usage: $0 <input_rn6.bed> <output_rn7.bed>}

LIFTOVER=./liftOver
CHAIN_RN6_RN7=rn6ToRn7.over.chain.gz
UNMAPPED="${INPUT%.bed}_unmapped.bed"

echo "Input:  $INPUT ($(wc -l < "$INPUT") records)"

$LIFTOVER \
    "$INPUT" \
    "$CHAIN_RN6_RN7" \
    "$OUTPUT" \
    "$UNMAPPED"

echo "Lifted: $(wc -l < "$OUTPUT") records"
echo "Lost:   $(grep -v '^#' "$UNMAPPED" | wc -l) records"
echo "=== Done. Output: $OUTPUT ==="
