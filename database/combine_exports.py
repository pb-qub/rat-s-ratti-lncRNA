import pandas as pd

# ── 1. Load each source ──────────────────────────────────────────────────────

wos = pd.read_csv("WOS_rat_lncRAN_MASTER.csv", encoding="utf-8-sig")
scopus = pd.read_csv("SCOPUS_rat_lncRNA_MASTER.csv", encoding="utf-8-sig")
eupmc = pd.read_csv("EUPMC_rat_lncrna.csv", encoding="utf-8-sig")

# ── 2. Standardise columns ───────────────────────────────────────────────────

wos_clean = pd.DataFrame({
    "title":    wos["Article Title"],
    "abstract": wos["Abstract"],
    "authors":  wos["Authors"],
    "year":     wos["Publication Year"],
    "doi":      wos["DOI"],
    "source":   "WOS"
})

scopus_clean = pd.DataFrame({
    "title":    scopus["Title"],
    "abstract": scopus["Abstract"],
    "authors":  scopus["Authors"],
    "year":     scopus["Year"],
    "doi":      scopus["DOI"],
    "source":   "Scopus"
})

eupmc_clean = pd.DataFrame({
    "title":    eupmc["title"],
    "abstract": eupmc["abstractText"],
    "authors":  eupmc["authorString"],
    "year":     eupmc["pubYear"],
    "doi":      eupmc["doi"],
    "source":   "EuropePMC"
})

# ── 3. Combine ───────────────────────────────────────────────────────────────

combined = pd.concat([wos_clean, scopus_clean, eupmc_clean], ignore_index=True)
print(f"Total records before deduplication: {len(combined)}")

# ── 4. Deduplicate by DOI ────────────────────────────────────────────────────

# Normalise DOIs: lowercase and strip whitespace
combined["doi_norm"] = combined["doi"].str.lower().str.strip()

# Keep first occurrence, drop duplicates
combined_deduped = combined.drop_duplicates(subset="doi_norm", keep="first")

# Drop the normalised helper column
combined_deduped = combined_deduped.drop(columns=["doi_norm"])

print(f"Total records after deduplication: {len(combined_deduped)}")

# ── 5. Save ──────────────────────────────────────────────────────────────────

combined_deduped.to_csv("combined_results.csv", index=False, encoding="utf-8-sig")
print("Saved to combined_results.csv")