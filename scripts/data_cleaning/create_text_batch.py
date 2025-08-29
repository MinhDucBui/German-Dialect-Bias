import pandas as pd
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import sys
sys.path.append(os.getcwd())
from scripts.inference import load_model, tokenize_data, batch_inference, save_data
from scripts import LANGUAGES
import json

LANGUAGES = ["nds"]

input_dir = "data/selected_data/manually_checked_data"
output_dir = "data/selected_data/gpt_4o_batch"

dialect_mapping = {
    "als": "Alemannic",
    "bar": "Bavarian",
    "frr": "North Frisian",
    "ksh": "Ripuarian",
    "nds": "Low German",
    "pfl": "Rhine Franconian",
    "stq": "Saterfrisian"
}
prompt_raw = "Translate the following German dialect (<DIALECT>) text into standard German while preserving the semantics, wording, and sentence structure as closely as possible: '<TEXT>'. Only answer with the standard German version:"


def fill_prompt(prompt_raw, contents, language):
    prompt_raw = prompt_raw.replace("<TEXT>", contents)
    prompt_raw = prompt_raw.replace("<DIALECT>", language)
    return prompt_raw
    

# Save the data
files = []
json_lines = []

for language in LANGUAGES:
    file = os.path.join(input_dir, language + ".csv")
    df = pd.read_csv(file)
    #df["Filter"] = pd.to_numeric(df["Filter"], errors='coerce').astype('Int64')
    #df = df[df["Filter"] == 1]

    df["prompts"] = df.apply(lambda row: fill_prompt(prompt_raw, row["contents"], dialect_mapping[language]), axis=1)
    for index, row in df.iterrows():
 
        base_line = {"custom_id": "", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-2024-08-06", "messages": "", "max_tokens": 400, "temperature": 0,}}
        base_line["body"]["messages"] = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": row["prompts"]}]
        base_line["custom_id"] = language + "_" + str(row["id"])
        json_lines.append(base_line)

file = os.path.join(output_dir, "translation_batch.jsonl")
# Write each dictionary as a JSON line in the file
with open(file, 'w', encoding='utf-8') as f:
    for item in json_lines:
        json.dump(item, f)
        f.write('\n')  # Write a newline to separate JSON lines
