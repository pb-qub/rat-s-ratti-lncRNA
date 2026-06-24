# Save as filter_fasta.py
with open("rat_lncRNA_master_database.fasta") as fin, \
     open("rat_lncRNA_master_database_50kb.fasta", "w") as fout:
    
    header = None
    seq = []
    kept = 0
    removed = 0
    
    for line in fin:
        line = line.rstrip()
        if line.startswith(">"):
            if header and seq:
                sequence = "".join(seq)
                if len(sequence) <= 50000:
                    fout.write(header + "\n")
                    fout.write(sequence + "\n")
                    kept += 1
                else:
                    removed += 1
            header = line
            seq = []
        else:
            seq.append(line)
    
    # Don't forget last sequence
    if header and seq:
        sequence = "".join(seq)
        if len(sequence) <= 50000:
            fout.write(header + "\n")
            fout.write(sequence + "\n")
            kept += 1
        else:
            removed += 1

print(f"Kept: {kept}")
print(f"Removed: {removed}")
print(f"Total processed: {kept + removed}")