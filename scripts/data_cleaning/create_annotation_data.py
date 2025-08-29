import pandas as pd
import os
import json
import sys
sys.path.append(os.getcwd())
from scripts import LANGUAGES

LANGUAGES = ["nds"]

original_dir = "data/selected_data/manually_checked_data"
input_file = "data/selected_data/gpt_4o_batch/translation_batch_output.jsonl"
output_dir = "data/selected_data/data_to_annotate"

# Construct the full file path
all_data = []
with open(input_file, "r", encoding="utf-8") as file:
    for line in file:
        data = json.loads(line)

        # Extracting fields
        id_value = data.get("id", "")
        custom_id = data.get("custom_id", "")
        response = data.get("response", {})

        # Extracting response details
        body = response.get("body", {})
        choices = body.get("choices", [])

        # Extracting assistant message content
        if choices:
            message = choices[0].get("message", {})
            assistant_content = message.get("content", "")
        else:
            assistant_content = ""

        language = custom_id.split("_")[0]
        df_id = custom_id.split("_")[1]
        # Storing the extracted fields
        all_data.append({
            # "id": id_value,
            "id": df_id,
            "language": language,
            #"status_code": status_code,
            #"request_id": request_id,
            #"model": model,
            "assistant_content": assistant_content
        })

    df = pd.DataFrame(all_data)


for language in LANGUAGES:
    # Load raw
    df_raw = pd.read_csv(os.path.join(original_dir, language + ".csv"))
    #df_raw["Filter"] = pd.to_numeric(df_raw["Filter"], errors='coerce').astype('Int64')

    #df_raw = df_raw[df_raw["Filter"] == 1]
    df_lang = df[df["language"] == language].copy()
    df_raw["id"] = df_raw["id"].astype(int) 
    df_lang["id"] = df_lang["id"].astype(int)

    df_save = pd.merge(df_raw, df_lang, on="id", how="inner")
    df_save["dialect"] = df_save["contents"]
    df_save.rename(columns={'assistant_content': 'translation'}, inplace=True)
    df_save = df_save[["id", "dialect", "translation"]]
    df_save["Correct"] = [None] * len(df_save)

    file_path = os.path.join(output_dir, language + ".csv")
    df_save = df_save.sample(frac=1, random_state=42).reset_index(drop=True)  

    df_save.to_csv(file_path)
