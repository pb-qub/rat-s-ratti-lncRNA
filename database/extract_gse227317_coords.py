#!/usr/bin/env python3
"""
extract_gse227317_coords.py

Extracts genomic coordinates from GSE227317 lncRNA FASTA headers and
converts them to BED6 format for use with UCSC liftOver.

Input FASTA header format:
    >MSTRG.73161.1 13 112257614-112259301

Output BED6 format (tab-separated):
    chr13    112257614    112259301    MSTRG.73161.1    0    .

Usage:
    python3 extract_gse227317_coords.py \
        --input GSE227317_LncRNA.fa.gz \
        --output GSE227317_lncRNA.bed

Note:
    - Strand information is not present in FASTA headers; strand is set to '.' (unknown)
    - 'chr' prefix is added to chromosome identifiers for UCSC liftOver compatibility
    - Coordinates are assumed to be 1-based (as output by StringTie); converted to
      0-based half-open BED format by subtracting 1 from the start coordinate
"""

import argparse
import gzip
import re
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Convert GSE227317 FASTA headers to BED6 format")
    parser.add_argument("--input", required=True, help="Input FASTA file (gzipped or plain)")
    parser.add_argument("--output", required=True, help="Output BED6 file")
    return parser.parse_args()


def open_file(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "r")


def parse_header(line):
    """
    Parse a FASTA header line of the format:
        >MSTRG.73161.1 13 112257614-112259301
    Returns (name, chrom, start, end) or None if the line cannot be parsed.
    """
    line = line.strip().lstrip(">")
    parts = line.split()
    if len(parts) != 3:
        return None
    name = parts[0]
    chrom = "chr" + parts[1]
    coords = parts[2].split("-")
    if len(coords) != 2:
        return None
    try:
        start = int(coords[0]) - 1  # Convert to 0-based
        end = int(coords[1])
    except ValueError:
        return None
    return name, chrom, start, end


def main():
    args = parse_args()

    written = 0
    skipped = 0

    with open_file(args.input) as fh, open(args.output, "w") as out:
        for line in fh:
            if not line.startswith(">"):
                continue
            result = parse_header(line)
            if result is None:
                print(f"WARNING: Could not parse header: {line.strip()}", file=sys.stderr)
                skipped += 1
                continue
            name, chrom, start, end = result
            out.write(f"{chrom}\t{start}\t{end}\t{name}\t0\t.\n")
            written += 1

    print(f"Done. Written: {written} records, Skipped: {skipped} records.")


if __name__ == "__main__":
    main()