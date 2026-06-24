import requests
import pandas as pd
import anthropic
import time
import re
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

df = pd.read_csv('medium_accessions_v2.csv', encoding='utf-8-sig')

# Same 6 priority papers
target_indices = [0, 2, 9, 10, 16, 33]
target_df = df.iloc[target_indices].copy()

print(f"Deep screening {len(target_df)} papers for data availability...\n")

def get_fulltext_eupmc(doi, char_limit=30000):
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

def screen_data_availability(title, text):
    prompt = f"""You are checking whether a published paper has made its RNA-seq data publicly available.

Paper title: {title}

Full text excerpt:
{text}

Look carefully for:
1. Any data availability statement
2. GEO, SRA, ArrayExpress, BioProject accession numbers
3. Chinese repositories: CNSA, NGDC, OMIX, GSA, NODE, CNCB
4. Supplementary files containing sequences or GTF/BED files
5. "Available upon request" statements
6. Any URL linking to deposited data

Respond ONLY with JSON:
{{
    "data_available": true or false,
    "availability_type": "GEO" or "ArrayExpress" or "Chinese_repo" or "Supplementary" or "On_request" or "URL" or "None",
    "accession_or_link": "the specific accession number, URL, or repository name if found, else null",
    "data_availability_statement": "copy the exact data availability statement if found, else null",
    "notes": "any other relevant details about data access"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    response = message.content[0].text.strip()
    response = response.replace("```json", "").replace("```", "").strip()
    import json
    return json.loads(response)

results = []

for idx, row in target_df.iterrows():
    doi = str(row.get("doi", "")).strip()
    title = str(row.get("title", ""))
    print(f"[{idx+1}] {title[:70]}...")

    text, pmcid = get_fulltext_eupmc(doi, char_limit=30000)
    time.sleep(0.5)

    if not text:
        print("  No text retrieved")
        result = {
            "data_available": False,
            "availability_type": "None",
            "accession_or_link": None,
            "data_availability_statement": None,
            "notes": "No full text retrieved"
        }
    else:
        print(f"  Got {len(text)} chars (PMC: {pmcid})")
        try:
            result = screen_data_availability(title, text)
            print(f"  Data available: {result['data_available']}")
            print(f"  Type: {result['availability_type']}")
            print(f"  Accession/Link: {result['accession_or_link']}")
        except Exception as e:
            print(f"  Error: {e}")
            result = {
                "data_available": False,
                "availability_type": "Error",
                "accession_or_link": None,
                "data_availability_statement": None,
                "notes": str(e)
            }

    row_dict = row.to_dict()
    row_dict.update(result)
    results.append(row_dict)
    time.sleep(0.5)

output = pd.DataFrame(results)
output.to_csv('priority_data_availability.csv', index=False, encoding='utf-8-sig')

print(f"\n{'='*60}")
print("Summary:")
print(output[['title','data_available','availability_type',
              'accession_or_link','notes']].to_string())