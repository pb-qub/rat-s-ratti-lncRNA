import anthropic
import pandas as pd
import time
import os
import json

# ── 1. Setup ─────────────────────────────────────────────────────────────────

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

input_file = "combined_rat_lncRNA_lit.csv"
output_file = "screened_results.csv"
progress_file = "screening_progress.json"

df = pd.read_csv(input_file, encoding="utf-8-sig")

# ── 2. Load progress if script was interrupted ────────────────────────────────

if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        progress = json.load(f)
    print(f"Resuming from record {len(progress['completed'])}...")
else:
    progress = {"completed": {}}

# ── 3. Screening function ─────────────────────────────────────────────────────

def screen_abstract(title, abstract):
    prompt = f"""You are screening academic papers for a master's thesis project on rat lncRNAs.

The project goal is to find papers that have identified novel rat (Rattus norvegicus) lncRNA sequences 
and deposited data publicly — either raw RNA-seq data (GEO/ArrayExpress accession) or supplementary 
lncRNA sequence files.

Evaluate this paper and respond ONLY with a JSON object, no other text:

Title: {title}
Abstract: {abstract}

Respond with exactly this JSON structure:
{{
    "relevance": "High" or "Medium" or "Low",
    "novel_lncrna": true or false,
    "accession_mentioned": true or false,
    "accession_number": "the accession number if mentioned, else null",
    "tissue_type": "tissue type if mentioned, else null",
    "genome_assembly": "genome assembly if mentioned e.g. mRatBN7.2, Rnor_6.0, else null",
    "reason": "one sentence explaining the relevance score"
}}

Scoring guide:
- High: clearly identifies novel rat lncRNAs AND mentions data deposition
- Medium: identifies rat lncRNAs but deposition unclear, OR relevant methods but rat focus unclear
- Low: mentions lncRNAs or rat incidentally, not the focus, or no data deposition
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = message.content[0].text.strip()
    # Strip markdown code fences if present
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    return json.loads(response_text)

# ── 4. Run screener ───────────────────────────────────────────────────────────

results = []

for idx, row in df.iterrows():
    record_id = str(idx)
    
    # Skip if already processed
    if record_id in progress["completed"]:
        results.append(progress["completed"][record_id])
        continue
    
    title = str(row.get("title", ""))
    abstract = str(row.get("abstract", ""))
    
    # Skip if no abstract
    if abstract.strip() == "" or abstract.strip().lower() == "nan":
        screening = {
            "relevance": "Low",
            "novel_lncrna": False,
            "accession_mentioned": False,
            "accession_number": None,
            "tissue_type": None,
            "genome_assembly": None,
            "reason": "No abstract available for screening"
        }
    else:
        try:
            print(f"[{idx+1}/{len(df)}] Screening: {title[:80]}...")
            screening = screen_abstract(title, abstract)
            time.sleep(0.5)  # polite delay
        except Exception as e:
            print(f"  ERROR on record {idx}: {e}")
            screening = {
                "relevance": "Error",
                "novel_lncrna": False,
                "accession_mentioned": False,
                "accession_number": None,
                "tissue_type": None,
                "genome_assembly": None,
                "reason": f"Screening error: {str(e)}"
            }
    
    # Combine original row with screening results
    combined_row = row.to_dict()
    combined_row.update(screening)
    results.append(combined_row)
    
    # Save progress
    progress["completed"][record_id] = combined_row
    with open(progress_file, "w") as f:
        json.dump(progress, f)

# ── 5. Save final output ──────────────────────────────────────────────────────

output_df = pd.DataFrame(results)

# Sort by relevance: High first, then Medium, then Low
relevance_order = {"High": 0, "Medium": 1, "Low": 2, "Error": 3}
output_df["relevance_rank"] = output_df["relevance"].map(relevance_order)
output_df = output_df.sort_values("relevance_rank").drop(columns=["relevance_rank"])

output_df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\nDone! Saved to {output_file}")

# ── 6. Print summary ──────────────────────────────────────────────────────────

print("\n── Summary ──────────────────────────────────────────")
print(output_df["relevance"].value_counts().to_string())
print(f"\nAccession numbers found: {output_df['accession_mentioned'].sum()}")