# rat-s-ratti-lncRNA

RNA-seq pipeline and scripts for detecting and differentially expressing rat (*Rattus norvegicus*) and *Strongyloides ratti* lncRNAs in gut immune tissues. MSc thesis project, Queen's University Belfast.

---

## Project Overview

This repository contains the bioinformatics scripts and workflows developed for an MSc thesis investigating long non-coding RNA (lncRNA) expression in rat gut immune tissues during *Strongyloides ratti* intestinal infection. RNA-seq data from intestinal mucosa and Peyer's patches (infected vs. uninfected rats) are analysed using a dual-mapping strategy to separate host and parasite transcripts.

**Thesis title:** *Differential Expression and Detection of Rat and Strongyloides ratti lncRNAs in Gut Immune Tissues*  
**Institution:** Queen's University Belfast  
**Assembly:** mRatBN7.2 (GCF_015227675.2)

---

## Data

The rat lncRNA reference database constructed in this project is deposited on Zenodo:

> **A Non-Redundant Rat (*Rattus norvegicus*) lncRNA Reference Database Mapped to mRatBN7.2**  
> DOI: [10.5281/zenodo.20829381](https://doi.org/10.5281/zenodo.20829381)

The deposit includes:
- `rat_lncRNA_master_database_dedup95.fasta.gz` — 75,022 non-redundant lncRNA sequences on mRatBN7.2
- `rat_lncRNA_master_database_dedup95.fasta.clstr.gz` — CD-HIT-EST cluster membership file
- `rat_lncRNA_master_database_clean.fasta.gz` — pre-deduplication database (176,183 sequences)
- `chr_name_mapping.txt` — chromosome name mapping table (UCSC ↔ NCBI naming)

---

## Pipeline Overview

```
Literature search & abstract screening (Anthropic API)
        ↓
lncRNA database construction (5 sources → master FASTA)
        ↓
Coordinate liftover to mRatBN7.2 (UCSC liftOver)
        ↓
Filtering, QC & deduplication (cd-hit-est, 95% identity)
        ↓
Dual-mapping RNA-seq (HISAT2 → lncRNA index; STAR → R. norvegicus + S. ratti)
        ↓
Transcript assembly (StringTie)
        ↓
Differential expression analysis (DESeq2/edgeR)
```

> **Status:** Database construction and HISAT2 indexing complete. Mapping and downstream stages in progress.

---

## Repository Structure

```
rat-s-ratti-lncRNA/
├── database/                   # lncRNA reference database construction
│   ├── fetch_eupmc.py
│   ├── combine_exports.py
│   ├── screen_abstracts.py
│   ├── second_screen.py
│   ├── find_accessions.py
│   ├── find_accessions_v2.py
│   ├── deep_search.py
│   ├── data_availability_check.py
│   ├── filter_xrefs_streaming.py
│   ├── filter_fasta.py
│   ├── qc_check.sh
│   ├── dedup_cdhit95.sh
│   └── hisat2_build_lncRNA_index.sh
├── liftover/                   # Coordinate liftover to mRatBN7.2
│   ├── gtf_to_bed_cufflinks.sh
│   ├── gtf_to_bed_standard.sh
│   ├── extract_gse227317_coords.py
│   ├── liftover_rn4_rn6_rn7.sh
│   ├── liftover_rn6_rn7.sh
│   ├── rename_chromosomes.sh
│   └── getfasta.sh
├── mapping/                    # HISAT2/STAR read mapping (in progress)
│   └── hisat2_map_lncRNA.sh
├── differential_expression/    # StringTie, DESeq2/edgeR (planned)
└── utils/                      # Shared utility scripts
```

---

## Key Data Sources

| Source | Sequences | Assembly |
|--------|-----------|----------|
| RNACentral | 33,206 | mRatBN7.2 (native) |
| Karri & Waxman 2020 (Dryad) | 107,209 | rn6 → rn7 |
| E-MTAB-867 (ArrayExpress) | 40,667 | rn4 → rn7 |
| GSE159668 (GEO) | 3,979 | rn6 → rn7 |
| GSE227317 (GEO) | 22,410 | rn6 → rn7 |
| **Total (post-deduplication)** | **75,022** | **mRatBN7.2** |

---

## Dependencies

- Python 3.11+
- Anthropic API (`claude-sonnet-4-6`) — abstract screening
- UCSC liftOver + chain files (rn4→rn6, rn6→rn7)
- bedtools v2.31.1
- cd-hit-est v4.8.1
- HISAT2 v2.2.1
- STAR
- StringTie
- samtools v1.17
- R (DESeq2, edgeR)

---

## HPC

Scripts are written for the **Kelvin2 HPC cluster** (Queen's University Belfast) using the SLURM scheduler. Partition: `k2-lowpri` / `k2-hipri`. Scratch space: `/mnt/scratch2/users/40500972/`.

---

## Citation

If you use the rat lncRNA reference database, please cite the Zenodo deposit:

> Brennan, P. (2026). *A Non-Redundant Rat (Rattus norvegicus) lncRNA Reference Database Mapped to mRatBN7.2*. Zenodo. https://doi.org/10.5281/zenodo.20829381
