import pandas as pd
import argparse
import os
import matplotlib.pyplot as plt
from collections import Counter
import scipy.stats as stats
import numpy as np
import sys
sys.path.append(os.getcwd())
from scripts import MODELS, DECISIONS
from scripts.eval_implicit import check_parsing, eval_bias_statistics, compute_bias, init_count


DIMENSIONS = list(DECISIONS.keys())


def parse_pair(pair, pos_adjectives, neg_adjectives, writer_a):
    pair = pair.lower()

    splitted = pair.split(":")

    if len(splitted) == 1:
        return None, None

    concept = splitted[1].strip().lower()
    writer_raw = splitted[0].strip().lower().replace("writer ", "")

    # Get writer
    writer = "dialect"
    if writer_a == "standard":
        if writer_raw == "a":
            writer = "standard"
    elif writer_a == "dialect":
        if writer_raw == "b":
            writer = "standard"

    # Classifiy positive, or negative
    category = None
    if concept in pos_adjectives:
        category = "pos"
    elif concept in neg_adjectives:
        category = "neg"

    if category == None:
        print(concept)
    return category, writer


def main(input_folder, output_folder, verbose=1):

    final_df = {
        "bias": [],
        "model_name": [],
        "dimension": [],
        "nones": [],
        "concepts": [],
        "language": []
    }

    for file, model_name in MODELS.items():
        input_file = os.path.join(input_folder, file)
        if not os.path.exists(input_file):
            continue
        input_file = input_file.replace(".csv", ".pkl")    
        df = pd.read_pickle(input_file)

        for dimension in DIMENSIONS:
            
            df_dimension = df[df["task"] == dimension].copy()

            counts = init_count()
            biases = []
            nones = []
            print("------{} ({})-----".format(model_name, dimension))
            print(df_dimension)
            df_dimension["answer"] = df_dimension.apply(lambda row: row["answer"][0].split('\n'), axis=1)

            pos_adjectives = [adj.lower() for adj in DECISIONS[dimension][0]]
            neg_adjectives = [adj.lower() for adj in DECISIONS[dimension][1]]

            for index, row in df_dimension.iterrows():
                bias_counts = init_count()
                bias = None

                for pair in row["answer"]:
                    category, writer = parse_pair(pair, pos_adjectives, neg_adjectives, row["writer_a"])
                    if category is not None:
                        counts[writer][category] += 1
                        bias_counts[writer][category] += 1
                    else:
                        bias_counts["None"] = 1
                        break

                if bias_counts["None"] == 0:
                    bias = compute_bias(bias_counts, "standard", "dialect", "pos", "neg")
                else:
                    bias_counts["None"] = 1

                biases.append(bias)
                nones.append(bias_counts["None"])

            final_df["bias"] += biases
            final_df["nones"] += nones
            final_df["model_name"] += [model_name] * len(biases)
            final_df["dimension"] += [dimension] * len(biases)
            final_df["concepts"] += list(df_dimension["concepts"])
            final_df["language"] += list(df_dimension["language"])
            print("Final Result for {} ({})".format(model_name, dimension))
            print(counts)
            #mean_bias, std_bias, t_stat, p_value = eval_bias_statistics(biases)
            #print("Bias Mean: {}. Bias std: {}. Bias Significance: {} (p={}).".format(mean_bias, std_bias, t_stat, p_value))

    final_df = pd.DataFrame(final_df)
    final_df.to_csv(os.path.join(output_folder, "final.csv"))

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run inference on a dataset and save the results.")
    parser.add_argument("--input_folder", type=str,
                        default="output/decision_extracted/", help="Path to the input CSV file.")
    args = parser.parse_args()

    output_folder = args.input_folder + 'eval/'

    os.makedirs(os.path.dirname(output_folder), exist_ok=True)

    main(args.input_folder, output_folder)
