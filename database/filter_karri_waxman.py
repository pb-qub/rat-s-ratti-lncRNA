#!/usr/bin/env python3
"""
filter_karri_waxman.py

Extracts all TCONS isoform IDs from Karri & Waxman (2020) Supplementary Table 2
and uses them to filter the lifted-over BED file, retaining only the 5,795
validated lncRNA transcripts.

Usage:
    python3 filter_karri_waxman.py \
        --table  Table_S2_Karri_Waxman_ToxSci_2020.csv \
        --bed    Karri_Waxman_rn7.bed \
        --out    Karri_Waxman_rn7_filtered.bed

Output:
    Filtered BED file containing only lines whose name field matches a TCONS ID
    from Table S2.  A summary is printed to stdout.
"""

import argparse
import csv
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Filter Karri & Waxman BED to validated lncRNAs")
    p.add_argument("--table", required=True, help="Path to Table_S2_Karri_Waxman_ToxSci_2020.csv")
    p.add_argument("--bed",   required=True, help="Path to Karri_Waxman_rn7.bed (lifted-over)")
    p.add_argument("--out",   required=True, help="Output filtered BED file path")
    return p.parse_args()


def load_tcons_ids(table_path):
    """
    Parse Table S2 CSV and return a set of all TCONS isoform IDs.
    Handles:
      - 3 header rows before data begins
      - Multiple isoforms separated by semicolons in the isoform_id column
      - Trailing commas on some single-isoform entries (Approach 2 rows)
    """
    tcons_ids = set()
    skipped_rows = 0

    with open(table_path, newline='', encoding='utf-8-sig') as fh:
        reader = csv.reader(fh)
        for i, row in enumerate(reader):
            # Skip the 3 header rows
            if i < 3:
                continue
            # Skip empty or legend-only rows
            if not row or not row[0].startswith("rlnc_"):
                skipped_rows += 1
                continue
            # isoform_id is column index 2
            isoform_field = row[2].strip()
            # Split on semicolons, strip whitespace and trailing commas
            for tid in isoform_field.split(";"):
                tid = tid.strip().rstrip(",").strip()
                if tid.startswith("TCONS_"):
                    tcons_ids.add(tid)

    return tcons_ids


def filter_bed(bed_path, tcons_ids, out_path):
    """
    Filter BED file, keeping lines where column 3 (name) is in tcons_ids.
    Returns (kept, total) counts.
    """
    kept = 0
    total = 0

    with open(bed_path) as fh_in, open(out_path, "w") as fh_out:
        for line in fh_in:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            total += 1
            fields = line.split("\t")
            if len(fields) < 4:
                continue
            name = fields[3].strip()
            if name in tcons_ids:
                fh_out.write(line + "\n")
                kept += 1

    return kept, total


def main():
    args = parse_args()

    print("Loading TCONS IDs from Table S2...")
    tcons_ids = load_tcons_ids(args.table)
    print(f"  Unique TCONS isoform IDs found: {len(tcons_ids)}")

    print(f"\nFiltering {args.bed}...")
    kept, total = filter_bed(args.bed, tcons_ids, args.out)

    print(f"  Total lines in BED:  {total:,}")
    print(f"  Lines kept:          {kept:,}")
    print(f"  Lines removed:       {total - kept:,}")
    print(f"  Retention:           {kept/total*100:.1f}%")
    print(f"\nFiltered BED written to: {args.out}")

    # Warn if kept count is much lower than expected
    if kept < 5000:
        print("\nWARNING: Fewer than 5,000 lines retained. Check that BED name "
              "field matches TCONS_ format exactly.", file=sys.stderr)


if __name__ == "__main__":
    main()