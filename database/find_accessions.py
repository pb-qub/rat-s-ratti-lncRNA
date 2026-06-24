import requests
import pandas as pd
import anthropic
import time
import os
import json
import re

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

df = pd.read_csv('medium_keep.csv', encoding='utf-8-sig')
print(f"Processing {len(df)} papers...\n")

def get_fulltext_eupmc(doi):
    """Try to get full text or extended abstract from Europe PMC via DOI"""
    # Search by DOI
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
            return None, None
        
        record = results[0]
        pmcid = record.get("pmcid", None)
        abstract = record.get("abstractText", "")
        
        # If we have a PMC ID, try to get full text sections
        if pmcid:
            ft_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
            ft_r = requests.get(ft_url, timeout=15)
            if ft_r.status_code == 200:
                # Extract text from XML - look for methods and data availability sections
                xml_text = ft_r.text
                # Simple extraction of text content
                text = re.sub(r'<[^>]+>', ' ', xml_text)
                text = re.sub(r'\s+', ' ', text)
                return text[:8000], pmcid  # Return first 8000 chars
        
        return abstract, pmcid
    except Exception as e:
        return None, None

def extract_accession_ai(title, text):
    """Use Claude to find GEO/ArrayExpress accession numbers in text"""
    prompt = f"""Find any GEO, ArrayExpress, SRA, or BioProject accession numbers in this text from a paper about rat lncRNAs.

Paper title: {title}

Text: {text}

Respond ONLY with a JSON object:
{{
    "accessions_found": ["list of accession numbers found, e.g. GSE12345, E-MTAB-1234, SRP123456, PRJNA123456"],
    "genome_assembly": "genome assembly version if mentioned e.g. Rnor_6.0, mRatBN7.2, rn6, else null",
    "data_available": true or false
}}

If no accession numbers are found, return empty list. Only include real accession numbers, not placeholder text.
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    response = message.content[0].text.strip()
    response = response.replace("```json", "").replace("```", "").strip()
    return json.loads(response)

results = []

for idx, row in df.iterrows():
    doi = str(row.get("doi", "")).strip()
    title = str(row.get("title", ""))
    
    print(f"[{idx+1}/{len(df)}] {title[:70]}...")
    
    if doi == "nan" or doi == "":
        print("  No DOI — skipping")
        result = {"accessions_found": [], "genome_assembly": None, "data_available": False, "source": "no_doi"}
    else:
        text, pmcid = get_fulltext_eupmc(doi)
        
        if text:
            source = "fulltext" if pmcid and len(text) > 1000 else "abstract"
            print(f"  Got text ({source}, {len(text)} chars)...")
            try:
                result = extract_accession_ai(title, text)
                result["source"] = source
            except Exception as e:
                print(f"  AI error: {e}")
                result = {"accessions_found": [], "genome_assembly": None, "data_available": False, "source": "error"}
        else:
            print("  No text retrieved")
            result = {"accessions_found": [], "genome_assembly": None, "data_available": False, "source": "no_text"}
    
    row_dict = row.to_dict()
    row_dict["accessions_found"] = "; ".join(result.get("accessions_found", []))
    row_dict["genome_assembly_found"] = result.get("genome_assembly", None)
    row_dict["data_available"] = result.get("data_available", False)
    row_dict["text_source"] = result.get("source", "unknown")
    results.append(row_dict)
    
    time.sleep(0.5)

output = pd.DataFrame(results)
output.to_csv('medium_accessions.csv', index=False, encoding='utf-8-sig')

# Print summary of hits
hits = output[output['accessions_found'].str.len() > 0]
print(f"\n{'='*60}")
print(f"Papers with accession numbers found: {len(hits)}/{len(output)}")
print(f"{'='*60}\n")
print(hits[['title','accessions_found','genome_assembly_found']].to_string())