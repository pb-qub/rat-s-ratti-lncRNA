# rat-s-ratti-lncRNA

RNA-seq pipeline and scripts for detecting and differentially expressing rat (*Rattus norvegicus*) and *Strongyloides ratti* lncRNAs in gut immune tissues. MSc thesis project, Queen's University Belfast.

---

## Project Overview

This repository contains the bioinformatics scripts and workflows developed for an MSc thesis investigating long non-coding RNA (lncRNA) expression in rat gut immune tissues during *Strongyloides ratti* intestinal infection. RNA-seq data from intestinal mucosa and Peyer's patches (infected vs. uninfected rats) are analysed using a dual-mapping strategy to separate host and parasite transcripts.

**Thesis title:** *Differential Expression and Detection of Rat and Strongyloides ratti lncRNAs in Gut Immune Tissues*  
**Institution:** Queen's University Belfast  
**Assembly:** mRatBN7.2 (GCF_015227675.2)

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
Dual-mapping RNA-seq (HISAT2 → R. norvegicus + S. ratti)
        ↓
Transcript assembly (StringTie)
        ↓
Differential expression analysis (DESeq2/edgeR)
```

---

## Repository Structure

```
rat-s-ratti-lncRNA/
├── database/               # lncRNA reference database construction
│   ├── screen_abstracts.py
│   ├── combine_exports.py
│   ├── filter_fasta.py
│   └── ...
├── liftover/               # Coordinate liftover scripts
│   ├── liftover_pipeline.sh
│   ├── extract_gse227317_coords.py
│   └── ...
├── mapping/                # HISAT2 dual-mapping pipeline
├── differential_expression/ # DESeq2/edgeR scripts
└── utils/                  # Shared utility scripts
```

---

## Key Data Sources

| Source | Sequences | Assembly |
|--------|-----------|----------|
| RNACentral | 33,206 | mRatBN7.2 |
| Karri & Waxman 2020 (Dryad) | 107,209 lifted | rn6 → rn7 |
| E-MTAB-867 (ArrayExpress) | 40,667 lifted | rn4 → rn7 |
| GSE159668 (GEO) | 3,979 lifted | rn6 → rn7 |
| GSE227317 (GEO) | 22,410 lifted | rn6 → rn7 |
| **Total (post-QC)** | **176,183** | **mRatBN7.2** |

---

## Dependencies

- Python 3.11+ (BioPython, requests)
- Anthropic API (`claude-sonnet-4-6`) — abstract screening
- UCSC liftOver + chain files (rn4→rn6, rn6→rn7)
- bedtools v2.31.1
- cd-hit-est v4.8.1
- HISAT2
- StringTie
- R (DESeq2, edgeR)

---

## HPC

Scripts are written for the **Kelvin2 HPC cluster** (Queen's University Belfast) using the SLURM scheduler. Scratch space: `/mnt/scratch2/users/40500972/`.

---

## Notes

- All sequences are standardised to the **mRatBN7.2** rat genome assembly.
- The dual-mapping strategy maps reads to both *R. norvegicus* and *S. ratti* genomes to distinguish host from parasite transcripts.
- Abstract screening used the Anthropic API programmatically via a custom Python script.
