import gzip

xrefs_file = "id_mapping.tsv.gz"
urs_file = "urs_ids.txt"
output_file = "filtered_xrefs.tsv"

# Load URS IDs into a set (fast lookup, low memory)
with open(urs_file) as f:
    urs_set = set(line.strip() for line in f)

with gzip.open(xrefs_file, "rt") as infile, open(output_file, "w") as out:
    header = infile.readline()
    out.write(header)

    for line in infile:
        # rna_id is the first column
        rna_id = line.split("\t", 1)[0]
        if rna_id in urs_set:
            out.write(line)

print("Done. Filtered results written to", output_file)
