import torch
import pandas as pd
import argparse
from tqdm import tqdm
import os
from inference import *
import ast
import sys

sys.path.append(os.getcwd())
from scripts import MODELS, DECISIONS


def parse_writer_story(row):
    story_text = ''
    writer_a_text = ''
    writer_b_text = ''
    if 'Task 1' in row['answer'] and 'Task 2' in row['answer']:
        stories = re.search(r'Task 1:(.*?)Task 2:?', row['answer']) 
        story_text = stories.group(1).strip()
    elif 'Task 2' in row['answer']:
        stories = re.search(r'(.*?)Task 2:?', row['answer']) 
        story_text = stories.group(1).strip()
    else:
        story_text = row['answer']

    if 'Writer A' in story_text.replace('Writer A and Writer B', '').replace('Writers A and B', ''):
        writer_a = re.search(r'Writer A:?(.*?)Writer B:?', story_text.replace('Writer A and Writer B', '').replace('Writers A and B', ''))
        writer_b = re.search(r'Writer B:?(.*)$', story_text.replace('Writer A and Writer B', '').replace('Writers A and B', ''))
        if writer_a:
            writer_a_text = writer_a.group(1).strip()
        if writer_b:
            writer_b_text = writer_b.group(1).strip()
    elif 'Composer' in story_text:
        writer_a = re.search(r'Composer A:?(.*?)Composer B:?', story_text)
        writer_b = re.search(r'Composer B:?(.*)$', story_text)
        if writer_a:
            writer_a_text = writer_a.group(1).strip()
        if writer_b:
            writer_b_text = writer_b.group(1).strip()
    elif 'Manager' in story_text:
        writer_a = re.search(r'Manager A:?(.*?)Manager B:?', story_text)
        writer_b = re.search(r'Manager B:?(.*)$', story_text)
        if writer_a:
            writer_a_text = writer_a.group(1).strip()
        if writer_b:
            writer_b_text = writer_b.group(1).strip()
    elif 'Musician' in story_text:
        writer_a = re.search(r'Musician [A1]:?(.*?)Musician [B2]:?', story_text)
        writer_b = re.search(r'Musician [B2]:?(.*)$', story_text)
        if writer_a:
            writer_a_text = writer_a.group(1).strip()
        if writer_b:
            writer_b_text = writer_b.group(1).strip()
    elif 'Athlete' in story_text:
        writer_a = re.search(r'Athlete A:?(.*?)Athlete B:?', story_text)
        writer_b = re.search(r'Athlete B:?(.*)$', story_text)
        if writer_a:
            writer_a_text = writer_a.group(1).strip()
        if writer_b:
            writer_b_text = writer_b.group(1).strip()
    elif len(story_text.split(' ')) > 15:
        writer_a = re.search(r'\*\*.{1,30} A:?(.*?) B:?', story_text)
        writer_b = re.search(r'\*\*.{1,30} B:?(.*)$', story_text)
        if writer_a:
            writer_a_text = writer_a.group(1).strip()
        if writer_b:
            writer_b_text = writer_b.group(1).strip()

    writer_a_text = writer_a_text.replace('\\n', ' ').replace('*', '').replace('  ', ' ').lower()
    writer_b_text = writer_b_text.replace('\\n', ' ').replace('*', '').replace('  ', ' ').lower()

    return pd.Series([writer_a_text, writer_b_text, story_text])




# Main workflow
def main():

    parser = argparse.ArgumentParser(
        description="Run inference on a dataset and save the results.")
    parser.add_argument("--decision_folder", type=str, default="output/decision/",
                        help="Where are the decision files stored?.")
    parser.add_argument("--output_folder", type=str,
                        default="output/decision_stories/", help="Path to the output CSV file.")


    args = parser.parse_args()


    
    for file in os.listdir(args.decision_folder):
        if file.endswith(".csv"):
            # Parse stories
            df = pd.read_csv(args.decision_folder + file)

            df[['Story A', 'Story B', 'story_text']] = df.apply(parse_writer_story, axis=1)
            print('***********************************')
            print(file)
            empty_stories = len(df[df['Story A'] == '']) + len(df[df['Story B'] == ''])
            print('Length of dataset: ' + str(len(df)))
            print('Non processed texts = ' + str(empty_stories))
            df['dimension'] = df['task'].str[:-2]


            os.makedirs(os.path.dirname(args.output_folder), exist_ok=True)
            df.to_csv(args.output_folder + file, index=False)





if __name__ == "__main__":

    main()