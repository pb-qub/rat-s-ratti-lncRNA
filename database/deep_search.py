import requests
import pandas as pd
import time
import re

df = pd.read_csv('medium_accessions_v2.csv', encoding='utf-8-sig')

# Target only these specific records with no accession found
target_indices = [0, 2, 9, 10, 16, 33]
target_df = df.iloc[target_indices].copy()

print(f"Running deep text search on {len(target_df)} priority papers...\n")

ACCESSION_PATTERNS = [
    r'GSE\d+',
    r'GSM\d+',
    r'GDS\d+',
    r'SRP\d+',
    r'SRR\d+',
    r'SRX\d+',
    r'PRJNA\d+',
    r'PRJEB\d+',
    r'E-MTAB-\d+',
    r'E-GEOD-\d+',
    r'ERP\d+',
]

def find_accessions_regex(text):
    found = set()
    for pattern in ACCESSION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.update(matches)
    return list(found)

def get_fulltext_eupmc_deep(doi, char_limit=30000):
    """Get full text from Europe PMC with higher character limit"""
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
            return "", None

        record = results[0]
        pmcid = record.get("pmcid", None)

        if pmcid:
            ft_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
            ft_r = requests.get(ft_url, timeout=15)
            if ft_r.status_code == 200:
                text = re.sub(r'<[^>]+>', ' ', ft_r.text)
                text = re.sub(r'\s+', ' ', text)
                return text[:char_limit], pmcid

        return record.get("abstractText", ""), None
    except:
        return "", None

results = []

for idx, row in target_df.iterrows():
    doi = str(row.get("doi", "")).strip()
    title = str(row.get("title", ""))
    print(f"[{idx+1}] {title[:70]}...")

    if doi == "nan" or doi == "":
        print("  No DOI — skipping")
        row_dict = row.to_dict()
        row_dict["accessions_deep"] = ""
        row_dict["chars_searched"] = 0
        results.append(row_dict)
        continue

    text, pmcid = get_fulltext_eupmc_deep(doi, char_limit=30000)
    time.sleep(0.5)

    accessions = find_accessions_regex(text)

    print(f"  PMC ID: {pmcid}")
    print(f"  Characters searched: {len(text)}")
    print(f"  Accessions found: {accessions if accessions else 'None'}")

    row_dict = row.to_dict()
    row_dict["accessions_deep"] = "; ".join(sorted(accessions))
    row_dict["chars_searched"] = len(text)
    results.append(row_dict)

output = pd.DataFrame(results)
output.to_csv('priority_deep_search.csv', index=False, encoding='utf-8-sig')

print(f"\n{'='*60}")
print("Summary:")
hits = output[output['accessions_deep'].str.len() > 0]
print(f"New accessions found: {len(hits)}/{len(output)}")
print()
print(hits[['title','accessions_deep','chars_searched']].to_string())