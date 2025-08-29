"""
Running this file obtains the words that distinguish a target group from the corresponding
unmarked ones.
Example usage: (To obtain the words that differentiate the 'Asian F' category)
python3 marked_words.py ../generated_personas.csv --target_val 'an Asian' F --target_col race gender --unmarked_val 'a White' M
"""

import pandas as pd
import numpy as np
from collections import Counter
import argparse
from collections import defaultdict
import math
import sys
import os


def get_log_odds(df1, df2, df0,verbose=False,lower=True):
    """Monroe et al. Fightin' Words method to identify top words in df1 and df2
    against df0 as the background corpus"""

    if lower:
        counts1 = defaultdict(int,[[i,j] for i,j in df1.str.lower().str.split(expand=True).stack().replace('[^a-zA-Z\s]','',regex=True).value_counts().items()])
        counts2 = defaultdict(int,[[i,j] for i,j in df2.str.lower().str.split(expand=True).stack().replace('[^a-zA-Z\s]','',regex=True).value_counts().items()])
        prior = defaultdict(int,[[i,j] for i,j in df0.str.lower().str.split(expand=True).stack().replace('[^a-zA-Z\s]','',regex=True).value_counts().items()])
    else:
        counts1 = defaultdict(int,[[i,j] for i,j in df1.str.split(expand=True).stack().replace('[^a-zA-Z\s]','',regex=True).value_counts().items()])
        counts2 = defaultdict(int,[[i,j] for i,j in df2.str.split(expand=True).stack().replace('[^a-zA-Z\s]','',regex=True).value_counts().items()])
        prior = defaultdict(int,[[i,j] for i,j in df0.str.split(expand=True).stack().replace('[^a-zA-Z\s]','',regex=True).value_counts().items()])
        

    sigmasquared = defaultdict(float)
    sigma = defaultdict(float)
    delta = defaultdict(float)

    for word in prior.keys():
        prior[word] = int(prior[word] + 0.5)

    for word in counts2.keys():
        counts1[word] = int(counts1[word] + 0.5)
        if prior[word] == 0:
            prior[word] = 1

    for word in counts1.keys():
        counts2[word] = int(counts2[word] + 0.5)
        if prior[word] == 0:
            prior[word] = 1

    n1 = sum(counts1.values())
    n2 = sum(counts2.values())
    nprior = sum(prior.values())
    
    for word in prior.keys():
        if prior[word] > 0:
        
            l1 = float(counts1[word] + prior[word]) / (( n1 + nprior ) - (counts1[word] + prior[word]))
            l2 = float(counts2[word] + prior[word]) / (( n2 + nprior ) - (counts2[word] + prior[word]))
            sigmasquared[word] =  1/(float(counts1[word]) + float(prior[word])) + 1/(float(counts2[word]) + float(prior[word]))
            sigma[word] =  math.sqrt(sigmasquared[word])
            delta[word] = ( math.log(l1) - math.log(l2) ) / sigma[word]

    if verbose:
        for word in sorted(delta, key=delta.get)[:10]:
            print("%s, %.3f" % (word, delta[word]))

        for word in sorted(delta, key=delta.get,reverse=True)[:10]:
            print("%s, %.3f" % (word, delta[word]))
    return delta




def marked_words_dialect(df_dimension, rest_texts,verbose=False):

    """Get words that distinguish the target group (which is defined as having 
    target_group_vals in the target_group_cols column of the dataframe) 
    from all unmarked_attrs (list of values that correspond to the categories 
    in unmarked_attrs)"""

    grams = dict()
    thr = 1.96 #z-score threshold

    for task in df_dimension.task.unique():

        subset = df_dimension[df_dimension['task'] == task]

        dialect_texts = pd.concat([subset[subset['writer_a'] == 'standard']['Story B'], subset[subset['writer_a'] != 'standard']['Story A']])
        standard_texts = pd.concat([subset[subset['writer_a'] == 'standard']['Story A'], subset[subset['writer_a'] != 'standard']['Story B']])
        

        delt = get_log_odds(dialect_texts, standard_texts, rest_texts, verbose) #first one is the positive-valued one

        c1 = []
        c2 = []
        for k,v in delt.items():
            if v > thr:
                c1.append([k,v])
            elif v < -thr:
                c2.append([k,v])
        

        if 'target' in grams:
            grams['target'].extend(c1)
        else:
            grams['target'] = c1
        if task in grams:
            grams[task].extend(c2)
        else:
            grams[task] = c2
    grams_refine = dict()
    

    for r in grams.keys():
        temp = []
        thr = len(df_dimension.task.unique()) 
        for k,v in Counter([word for word, z in grams[r]]).most_common():
            if v >= thr:
                z_score_sum = np.sum([z for word, z in grams[r] if word == k])
                temp.append([k, z_score_sum])

        grams_refine[r] = temp
    return grams_refine['target']

def marked_words_standard(df_dimension, rest_texts,verbose=False):

    """Get words that distinguish the target group (which is defined as having 
    target_group_vals in the target_group_cols column of the dataframe) 
    from all unmarked_attrs (list of values that correspond to the categories 
    in unmarked_attrs)"""

    grams = dict()
    thr = 1.96 #z-score threshold

    for task in df_dimension.task.unique():

        subset = df_dimension[df_dimension['task'] == task]

        dialect_texts = pd.concat([subset[subset['writer_a'] == 'standard']['Story B'], subset[subset['writer_a'] != 'standard']['Story A']])
        standard_texts = pd.concat([subset[subset['writer_a'] == 'standard']['Story A'], subset[subset['writer_a'] != 'standard']['Story B']])
        

        delt = get_log_odds(standard_texts, dialect_texts, rest_texts, verbose) #first one is the positive-valued one

        c1 = []
        c2 = []
        for k,v in delt.items():
            if v > thr:
                c1.append([k,v])
            elif v < -thr:
                c2.append([k,v])
        

        if 'target' in grams:
            grams['target'].extend(c1)
        else:
            grams['target'] = c1
        if task in grams:
            grams[task].extend(c2)
        else:
            grams[task] = c2
    grams_refine = dict()
    

    for r in grams.keys():
        temp = []
        thr = len(df_dimension.task.unique()) 
        for k,v in Counter([word for word, z in grams[r]]).most_common():
            if v >= thr:
                z_score_sum = np.sum([z for word, z in grams[r] if word == k])
                temp.append([k, z_score_sum])

        grams_refine[r] = temp
    return grams_refine['target']


def main():
    parser = argparse.ArgumentParser(description="Just an example",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--decision_folder", default="output/decision_stories/", type=str, help="Generated personas file")
    parser.add_argument("--target_val",nargs="*", 
    type=str,
    default=[''], help="List of demographic attribute(s) for target group of interest")
    parser.add_argument("--target_col", nargs="*",
    type=str,
    default=[''],help="List of demographic categories that distinguish target group")
    parser.add_argument("--unmarked_val", nargs="*",
    type=str,
    default=[''],help="List of unmarked default values for relevant demographic categories")
    parser.add_argument("--per_lang", default=False, type=bool, help="Do generate per dialect")
    parser.add_argument("--verbose", action='store_true',help="If set to true, prints out top words calculated by Fightin' Words")

    args = parser.parse_args()

    rows = []
    for file in os.listdir(args.decision_folder):
        if file != 'eval':
            print('****************************')
            print(file)

            df = pd.read_csv(args.decision_folder + file)

            #Filter out empty cells for both dialect and standard
            df = df[(~df['Story A'].isnull()) & (~df['Story B'].isnull())]
            df = df[~df['dimension'].isnull()]

            if args.per_lang:
            
                for dialect in df.language.unique():
                    
                    subset_dialect = df[df['language'] == dialect]

                    for task in subset_dialect.task.unique():
                        print(task)
                        subset = subset_dialect[subset_dialect['task'] == task].copy()
                        rest_texts = pd.concat([subset_dialect['Story A'],subset_dialect['Story B']])
                    
                        top_words = marked_words_dialect(subset, rest_texts,verbose=args.verbose)
                        print("Top words:")
                        print(top_words)
                        for word, value in top_words:
                            rows.append(['dialect', file[:-4] , task, word, float(value), dialect])
                        
                        top_words = marked_words_standard(subset, rest_texts,verbose=args.verbose)
                        print("Top words:")
                        print(top_words)
                        for word, value in top_words:
                            rows.append(['standard', file[:-4] , task, word, float(value), dialect])
            
            else:

                for task in df.task.unique():
                    print(task)
                    subset = df[df['task'] == task].copy()
                    rest_texts = pd.concat([df['Story A'],df['Story B']])
                
                    top_words = marked_words_dialect(subset, rest_texts,verbose=args.verbose)
                    print("Top words:")
                    print(top_words)
                    for word, value in top_words:
                        rows.append(['dialect', file[:-4] , task, word, float(value)])
                    
                    top_words = marked_words_standard(subset, rest_texts,verbose=args.verbose)
                    print("Top words:")
                    print(top_words)
                    for word, value in top_words:
                        rows.append(['standard', file[:-4] , task, word, float(value)])

    if args.per_lang:
        df_results = pd.DataFrame(rows, columns=["Target Group", "Model" , "Task", "Word", "Value", "Dialect"])
    else:
        df_results = pd.DataFrame(rows, columns=["Target Group", "Model" , "Task", "Word", "Value"])
    os.makedirs(os.path.dirname(args.decision_folder + 'eval/'), exist_ok=True)
    df_results['Value'] = df_results['Value'].round(2)
    df_results = df_results.sort_values(by=['Target Group', 'Model','Task','Value'], ascending=False)
    df_results['Word+Value'] = df_results['Word'] + ' (' + df_results['Value'].astype(str) + '), '
    df_results.to_csv(args.decision_folder + 'eval/results.csv' , index=False)
    grouped = df_results.groupby(["Target Group", "Model" , "Task"])['Word+Value'].sum().reset_index()
    grouped.to_csv(args.decision_folder + 'eval/results_grouped.csv' , index=False)

if __name__ == '__main__':
    
    main()

