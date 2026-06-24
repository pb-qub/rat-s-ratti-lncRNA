import requests
import pandas as pd
import time
import re
import json

df = pd.read_csv('medium_keep.csv', encoding='utf-8-sig')
print(f"Processing {len(df)} papers...\n")

# ── Accession patterns to search for ────────────────────────────────────────
ACCESSION_PATTERNS = [
    r'GSE\d+',           # GEO Series
    r'GSM\d+',           # GEO Sample
    r'GDS\d+',           # GEO Dataset
    r'SRP\d+',           # SRA Project
    r'SRR\d+',           # SRA Run
    r'SRX\d+',           # SRA Experiment
    r'PRJNA\d+',         # BioProject
    r'PRJEB\d+',         # BioProject European
    r'E-MTAB-\d+',       # ArrayExpress
    r'E-GEOD-\d+',       # ArrayExpress (GEO mirror)
    r'ERP\d+',           # ENA Project
]

def find_accessions_regex(text):
    """Scan text for any known accession number patterns"""
    found = set()
    for pattern in ACCESSION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.update(matches)
    return list(found)

def get_pmid_from_doi(doi):
    """Convert DOI to PMID using NCBI API"""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": f"{doi}[DOI]",
        "retmode": "json"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except:
        return None

def search_geo_by_pmid(pmid):
    """Query GEO eSearch for datasets linked to a PMID"""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "gds",
        "term": f"{pmid}[PubMed]",
        "retmode": "json"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        
        # Fetch accession numbers for these GEO IDs
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            "db": "gds",
            "id": ",".join(ids),
            "retmode": "json"
        }
        sr = requests.get(summary_url, params=summary_params, timeout=10)
        sdata = sr.json()
        
        accessions = []
        for uid in ids:
            result = sdata.get("result", {}).get(uid, {})
            acc = result.get("accession", "")
            if acc:
                accessions.append(acc)
        return accessions
    except:
        return []

def get_fulltext_eupmc(doi):
    """Get full text from Europe PMC — all sections, higher limit"""
    search_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": f'DOI:"{doi}"',
        "resultType": "core",
        "pageSize": 1,
        "format": "json"
    }
    try:
        r = requests.get(search_url, params=params, timeout=15)
        data = r.json()
        results = data.get("resultList", {}).get("result", [])
        if not results:
            return ""
        
        record = results[0]
        pmcid = record.get("pmcid", None)
        
        if pmcid:
            ft_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
            ft_r = requests.get(ft_url, timeout=15)
            if ft_r.status_code == 200:
                # Strip XML tags and return full text — no truncation
                text = re.sub(r'<[^>]+>', ' ', ft_r.text)
                text = re.sub(r'\s+', ' ', text)
                return text
        
        # Fall back to abstract
        return record.get("abstractText", "")
    except:
        return ""

# ── Main loop ────────────────────────────────────────────────────────────────
results = []

for idx, row in df.iterrows():
    doi = str(row.get("doi", "")).strip()
    title = str(row.get("title", ""))
    print(f"[{idx+1}/{len(df)}] {title[:70]}...")
    
    all_accessions = set()
    methods = []
    
    # ── Method 1: GEO API via PMID ──────────────────────────────────────────
    if doi and doi != "nan":
        pmid = get_pmid_from_doi(doi)
        time.sleep(0.4)  # NCBI rate limit
        
        if pmid:
            geo_accessions = search_geo_by_pmid(pmid)
            time.sleep(0.4)
            if geo_accessions:
                all_accessions.update(geo_accessions)
                methods.append("GEO_API")
                print(f"  GEO API: {geo_accessions}")
    
    # ── Method 2: Full text regex scan ──────────────────────────────────────
    if doi and doi != "nan":
        text = get_fulltext_eupmc(doi)
        time.sleep(0.5)
        
        if text:
            regex_hits = find_accessions_regex(text)
            if regex_hits:
                all_accessions.update(regex_hits)
                methods.append("regex_fulltext")
                print(f"  Regex: {regex_hits}")
    
    if not all_accessions:
        print("  No accessions found")
    
    row_dict = row.to_dict()
    row_dict["accessions_found_v2"] = "; ".join(sorted(all_accessions))
    row_dict["detection_method"] = "; ".join(methods)
    results.append(row_dict)

# ── Save and summarise ───────────────────────────────────────────────────────
output = pd.DataFrame(results)
output.to_csv('medium_accessions_v2.csv', index=False, encoding='utf-8-sig')

hits = output[output['accessions_found_v2'].str.len() > 0]
print(f"\n{'='*60}")
print(f"Papers with accessions found: {len(hits)}/{len(output)}")
print(f"{'='*60}\n")
print(hits[['title','accessions_found_v2','detection_method']].to_string())