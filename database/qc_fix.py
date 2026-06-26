#!/usr/bin/env python3
"""
qc_fix.py

Fixes quality issues in the rat lncRNA master FASTA database:
  1. Removes empty sequences
  2. Removes N-rich sequences (starting with 4+ consecutive Ns)
  3. Renames duplicate headers by appending _dup1, _dup2 etc.

Usage:
    python3 qc_fix.py <input.fasta> <output.fasta>

Example:
    python3 qc_fix.py rat_lncRNA_master_database_filtered.fasta \
                      rat_lncRNA_master_database_clean.fasta
"""

import sys

if len(sys.argv) != 3:
    print(f"Usage: python3 {sys.argv[0]} <input.fasta> <output.fasta>")
    sys.exit(1)

input_file  = sys.argv[1]
output_file = sys.argv[2]

# ── Pass 1: read all sequences into memory ────────────────────────────────────
sequences = []
with open(input_file) as fh:
    header = None
    seq_lines = []
    for line in fh:
        line = line.rstrip()
        if line.startswith(">"):
            if header is not None:
                sequences.append((header, "".join(seq_lines)))
            header = line
            seq_lines = []
        else:
            seq_lines.append(line)
    if header is not None:
        sequences.append((header, "".join(seq_lines)))

print(f"Total sequences read: {len(sequences):,}")

# ── Pass 2: apply fixes ───────────────────────────────────────────────────────
removed_empty   = 0
removed_nrich   = 0
renamed_dups    = 0

seen_headers = {}   # header -> count of times seen
kept = []

for header, seq in sequences:
    # Remove empty sequences
    if len(seq) == 0:
        removed_empty += 1
        continue

    # Remove N-rich sequences (starting with 4+ Ns)
    if seq.upper().startswith("NNNN"):
        removed_nrich += 1
        continue

    # Rename duplicate headers
    if header in seen_headers:
        seen_headers[header] += 1
        new_header = f"{header}_dup{seen_headers[header]}"
        renamed_dups += 1
    else:
        seen_headers[header] = 0
        new_header = header

    kept.append((new_header, seq))

# ── Write output ──────────────────────────────────────────────────────────────
with open(output_file, "w") as fh:
    for header, seq in kept:
        fh.write(header + "\n")
        fh.write(seq + "\n")

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"Removed empty sequences:  {removed_empty:,}")
print(f"Removed N-rich sequences: {removed_nrich:,}")
print(f"Duplicate headers renamed: {renamed_dups:,}")
print(f"Final sequence count:     {len(kept):,}")
print(f"Output written to:        {output_file}")