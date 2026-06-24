import anthropic
import pandas as pd
import time
import os
import json

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

df = pd.read_csv('screened_results.csv', encoding='utf-8-sig')
medium = df[df['relevance']=='Medium'].copy()
print(f"Screening {len(medium)} Medium relevance papers...")

def second_screen(title, abstract, first_reason):
    prompt = f"""You are doing a second-pass screen of academic papers for a master's thesis on rat lncRNAs.

This paper was flagged as Medium relevance in a first pass. Your job is to make a final call:
is there actually useful novel rat lncRNA sequence data or a GEO/ArrayExpress accession 
containing rat RNA-seq data in this paper?

Title: {title}
Abstract: {abstract}
First pass reason: {first_reason}

Respond ONLY with a JSON object:
{{
    "final_call": "Keep" or "Discard",
    "accession_number": "specific accession if found, else null",
    "novel_sequences": true or false,
    "assembly": "genome assembly if mentioned, else null",
    "one_line": "one sentence explaining your decision"
}}

Be strict — only Keep if there is clear evidence of novel rat lncRNA data deposition.
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
for idx, row in medium.iterrows():
    title = str(row.get("title", ""))
    abstract = str(row.get("abstract", ""))
    first_reason = str(row.get("reason", ""))
    
    if abstract.strip() == "" or abstract.strip().lower() == "nan":
        result = {"final_call": "Discard", "accession_number": None,
                  "novel_sequences": False, "assembly": None,
                  "one_line": "No abstract available"}
    else:
        try:
            print(f"Screening: {title[:80]}...")
            result = second_screen(title, abstract, first_reason)
            time.sleep(0.5)
        except Exception as e:
            print(f"ERROR: {e}")
            result = {"final_call": "Error", "accession_number": None,
                      "novel_sequences": False, "assembly": None,
                      "one_line": str(e)}
    
    row_dict = row.to_dict()
    row_dict.update(result)
    results.append(row_dict)

output = pd.DataFrame(results)
keep = output[output['final_call']=='Keep']
output.to_csv('medium_second_screen.csv', index=False, encoding='utf-8-sig')
keep.to_csv('medium_keep.csv', index=False, encoding='utf-8-sig')

print(f"\nDone!")
print(f"Keep: {len(keep)}")
print(f"Discard: {len(output[output['final_call']=='Discard'])}")
print("\nPapers to Keep:")
print(keep[['title','accession_number','assembly','one_line']].to_string())