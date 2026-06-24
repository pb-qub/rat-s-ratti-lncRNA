import requests
import csv
import time

# Initial URL
url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
params = {
    "query": '("Rattus norvegicus") AND ("long non-coding RNA" OR "lncRNA" OR "lincRNA") AND ("RNA-seq" OR "transcriptome" OR "de novo assembly") AND ("novel" OR "unannotated" OR "newly identified") AND ("GEO" OR "GSE" OR "ArrayExpress" OR "BioProject" OR "deposited") AND (HAS_FT:Y)',
    "resultType": "core",
    "pageSize": 100,
    "format": "json",
    "cursorMark": "*"
}

all_results = []

while True:
    print(f"Fetching page... (collected {len(all_results)} so far)")
    response = requests.get(url, params=params)
    data = response.json()
    
    results = data.get("resultList", {}).get("result", [])
    all_results.extend(results)
    
    # Check if there are more pages
    next_cursor = data.get("nextCursorMark")
    current_cursor = params.get("cursorMark")
    
    if not next_cursor or next_cursor == current_cursor:
        break
    
    params["cursorMark"] = next_cursor
    time.sleep(1)  # polite delay

print(f"Total records fetched: {len(all_results)}")

# Write to CSV
output_file = "eupmc_rat_lncrna.csv"
fields = ["pmid", "pmcid", "doi", "title", "authorString", "pubYear", 
          "journalTitle", "abstractText", "keywordList"]

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    
    for record in all_results:
        # Flatten keywords if present
        keywords = record.get("keywordList", {})
        if isinstance(keywords, dict):
            kw_list = keywords.get("keyword", [])
            record["keywordList"] = "; ".join(kw_list) if isinstance(kw_list, list) else str(kw_list)
        
        # Handle missing abstractText
        if "abstractText" not in record:
            record["abstractText"] = ""
            
        writer.writerow(record)

print(f"Saved to {output_file}")