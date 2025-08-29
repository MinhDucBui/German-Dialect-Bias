import pandas as pd
import argparse
import os
import matplotlib.pyplot as plt
from collections import Counter
import scipy.stats as stats
import numpy as np
import sys
sys.path.append(os.getcwd())
from scripts import MODELS, ADJECTIVES

N_ADJECTIVES = 10

DIMENSIONS = list(ADJECTIVES.keys())


def check_parsing(pair, writer_raw, word, pos_adjectives, neg_adjectives):
    # Check if the writer_raw is neither "a" nor "b"
    if writer_raw != "a" and writer_raw != "b":
        print(f"Expected 'a' or 'b' but got '{writer_raw}'. Raw Pair: {pair}")
        return False

    # Check if the word is neither in pos_adjectives nor neg_adjectives
    if word not in pos_adjectives and word not in neg_adjectives:
        print(f"Word '{word}' in pair {pair} is not in any of the predefined positive or negative adjectives lists.")
        return False

    # Return None (implicitly)
    return True


def parse_pair(pair, pos_adjectives, neg_adjectives, writer_a):
    pair = pair.lower().replace('human:', '')
    splitted = pair.split(":")
    word = splitted[0].strip().lower()
    if len(splitted) > 1:
        if word not in pos_adjectives and word not in neg_adjectives:
            word = splitted[1].strip().lower()
            writer_raw = splitted[0].strip().lower()
        else:
            writer_raw = ":".join(splitted[1:])
        writer_raw = writer_raw.replace("writer", "").replace("write", "").strip()
        writer_raw = writer_raw.replace(":", "").strip().lower().split(" ")[0]
    else:
        writer_raw = "wrong"


    # Check correct parsing
    correct_parsed = check_parsing(pair, writer_raw, word, pos_adjectives, neg_adjectives)
    if correct_parsed is False:
        return None, None

    # Get writer
    writer = "dialect"
    if writer_a == "standard":
        if writer_raw == "a":
            writer = "standard"
    elif writer_a == "dialect":
        if writer_raw == "b":
            writer = "standard"

    # Classifiy positive, or negative
    if word in pos_adjectives:
        category = "pos"
    elif word in neg_adjectives:
        category = "neg"

    return category, writer


def eval_bias_statistics(biases):
    t_stat, p_value = stats.ttest_1samp(biases, 0)
    mean_bias = np.mean(biases)
    std_bias = np.std(biases)#, ddof=1)
    # Compute the 95% confidence interval
    n = len(biases)
    se = std_bias / np.sqrt(n)  # Standard error
    confidence = 0.95
    t_score = stats.t.ppf((1 + confidence) / 2, df=n-1)  # t-score for 95% confidence interval
    margin_of_error = t_score * se
    confidence_interval = (mean_bias - margin_of_error, mean_bias + margin_of_error)
    print(confidence_interval)
    return mean_bias, std_bias, t_stat, p_value 


def compute_bias(value_dictionary, sa, sb, xa, xb):
    """
    Computes the bias based on the given formula.
    
    Parameters:
    N (function): A function that takes two arguments (s, X) and returns a count.
    sa, sb: Categories or labels.
    Xa, Xb: Groups or datasets.
    
    Returns:
    float: Computed bias value.
    """

    sa_xa = value_dictionary[sa][xa]
    sa_xb = value_dictionary[sa][xb]
    sb_xa = value_dictionary[sb][xa]
    sb_xb = value_dictionary[sb][xb]
    if (sa_xa + sa_xb) == 0 or (sb_xa + sb_xb) == 0:
        #das
        return 0

    term1 = sa_xa / (sa_xa + sa_xb)
    term2 = sb_xb / (sb_xa + sb_xb)
    return term1 + term2 - 1


def init_count():
    counts = {
        "standard": {
            "pos": 0,
            "neg": 0
        },
        "dialect": {
            "pos": 0,
            "neg": 0
        },
        "None": 0
    }
    return counts


def main(input_folder, output_folder, verbose=1):

    final_df = {
        "bias": [],
        "model_name": [],
        "dimension": [],
        "nones": [],
        "language": []
    }

    for file, model_name in MODELS.items():
        print(model_name)
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
            df_dimension["answer"] = df_dimension.apply(lambda row: row["answer"][0].split('\n'), axis=1)
            pos_adjectives = ADJECTIVES[dimension][0]
            neg_adjectives = ADJECTIVES[dimension][1]
            print(pos_adjectives)
            print(neg_adjectives)
            for index, row in df_dimension.iterrows():
                bias_counts = init_count()
                bias = None
                if len(row["answer"]) == N_ADJECTIVES:

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
                    #das
                # Collect Data
                biases.append(bias)
                nones.append(bias_counts["None"])

            final_df["bias"] += biases
            final_df["nones"] += nones
            final_df["model_name"] += [model_name] * len(biases)
            final_df["dimension"] += [dimension] * len(biases)
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
                        default="output/implicit/", help="Path to the input CSV file.")

    args = parser.parse_args()

    output_folder = args.input_folder + 'eval/'

    os.makedirs(os.path.dirname(output_folder), exist_ok=True)

    main(args.input_folder, output_folder)
