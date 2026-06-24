#!/bin/bash
# liftover_rn4_rn6_rn7.sh
#
# Performs a two-hop coordinate liftover from rn4 to mRatBN7.2 (rn7)
# via an intermediate rn6 step, as no direct rn4->rn7 chain file is available.
#
# Used for: E-MTAB-867 BED file (rn4 assembly)
#
# Requirements:
#   - liftOver binary in the same directory or on PATH
#   - rn4ToRn6.over.chain.gz
#   - rn6ToRn7.over.chain.gz
#
# Usage:
#   bash liftover_rn4_rn6_rn7.sh <input.bed> <output_rn7.bed>
#
# Example:
#   bash liftover_rn4_rn6_rn7.sh transcripts_bg200.rat.rn4.bed transcripts_bg200.rat.rn7.bed

set -euo pipefail

INPUT=${1:?Usage: $0 <input_rn4.bed> <output_rn7.bed>}
OUTPUT=${2:?Usage: $0 <input_rn4.bed> <output_rn7.bed>}

LIFTOVER=./liftOver
CHAIN_RN4_RN6=rn4ToRn6.over.chain.gz
CHAIN_RN6_RN7=rn6ToRn7.over.chain.gz

TMP_RN6="${INPUT%.bed}_rn6.bed"
TMP_RN4_UNMAPPED="${INPUT%.bed}_rn4_unmapped.bed"
TMP_RN6_UNMAPPED="${INPUT%.bed}_rn6_unmapped.bed"

echo "=== Hop 1: rn4 -> rn6 ==="
$LIFTOVER \
    "$INPUT" \
    "$CHAIN_RN4_RN6" \
    "$TMP_RN6" \
    "$TMP_RN4_UNMAPPED"

echo "Lifted to rn6: $(wc -l < "$TMP_RN6")"
echo "Lost at rn4->rn6: $(grep -v '^#' "$TMP_RN4_UNMAPPED" | wc -l)"

echo "=== Hop 2: rn6 -> rn7 ==="
$LIFTOVER \
    "$TMP_RN6" \
    "$CHAIN_RN6_RN7" \
    "$OUTPUT" \
    "$TMP_RN6_UNMAPPED"

echo "Lifted to rn7: $(wc -l < "$OUTPUT")"
echo "Lost at rn6->rn7: $(grep -v '^#' "$TMP_RN6_UNMAPPED" | wc -l)"
echo "=== Done. Final output: $OUTPUT ==="
