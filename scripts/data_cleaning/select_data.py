import pandas as pd
import os
import sys
sys.path.append(os.getcwd())
from scripts import LANGUAGES

input_dir = "data/wikidir"
output_dir = "data/selected_data"

dfs = []
for language in LANGUAGES:
    print(language)
    file = os.path.join(input_dir, "de." + language, "docs.jsonl")
    df = pd.read_json(file, lines=True)
    df["length"] = df["contents"].apply(lambda x: len(x))

    # print(df["length"].describe())  # Summary stats: count, mean, std, min, 25%, 50%, 75%, max

    df = df[(df["length"] > 300) & (df["length"] < 500)]
    df = df.sample(n=200, random_state=40)  # Set random_state for reproducibility

    file = os.path.join(output_dir, language + ".csv")
    df.to_csv(file)