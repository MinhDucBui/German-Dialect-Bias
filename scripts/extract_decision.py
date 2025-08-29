from transformers import AutoTokenizer, AutoModelForCausalLM, Gemma3ForConditionalGeneration
import torch
import pandas as pd
import argparse
from tqdm import tqdm
import os
from inference import *
import ast


PROMPT = "Text: '<TEXT>'\n\nExtract which writer is recommended to go to the agent specialized in '<CONCEPT1>' and which writer is recommended to go to the agent specialized in '<CONCEPT2>'. Provide your answer in the exact following format (without additional text): 'Writer A: <<CONCEPT1> or <CONCEPT2>>\nWriter B: <<CONCEPT1> or <CONCEPT2>>'"

def tokenize_data(tokenizer, file_path):

    df = pd.read_pickle(file_path)
    answers = df["answer"]

    prompts = []
    for answer, concepts in zip(df["answer"], df["concepts"]):
        current_prompt = PROMPT
        concepts = ast.literal_eval(concepts)
        answer[0] = answer[0].replace("\n", "")
        current_prompt = current_prompt.replace("<TEXT>", answer[0])
        current_prompt = current_prompt.replace("<CONCEPT1>", concepts[0][0])
        current_prompt = current_prompt.replace("<CONCEPT2>", concepts[0][1])
        prompts.append(current_prompt)
    df["prompts"] = prompts
    
    all_prompts = []
    for index, row in df.iterrows():
        # Create message
        messages = [{"role": "user", "content": row["prompts"]}]

        metadata = row.to_dict()
        for key in ["prompts"]:
            metadata.pop(key, None)  # `None` prevents errors if the key isn't found

        all_prompts.append(
            [messages, metadata])

    prompts_template = []
    prompt_metadata = []
    for _, prompt in enumerate(all_prompts):
        messages = tokenizer.apply_chat_template(
            prompt[0], add_generation_prompt=True, tokenize=False)
        prompts_template.append(messages)
        prompt_metadata.append(prompt[1])
    # print(prompts_template[:2])
    return prompts_template, prompt_metadata


# Main workflow
def main(model_name, output_file, decision_folder):
    
    # Step 0: Load the Model
    model, tokenizer = load_model(model_name)
    #model, tokenizer, logits_processor = None, None, None
    for file in os.listdir(decision_folder):
        if file.endswith(".pkl"):
            output_file = os.path.join(args.output_folder, file.split(".pkl")[0] + ".csv")
            file_path = os.path.join(decision_folder, file)
            prompts, prompt_metadata = tokenize_data(tokenizer, file_path)

            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Step 2: Perform inference
            results = batch_inference(prompts, model, tokenizer, prompt_metadata, output_file)
            
            save_data(results, prompt_metadata, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run inference on a dataset and save the results.")
    parser.add_argument("--model_name", type=str, default="gemma-3-12b-it",
                        help="Name of the model to use for inference.")
    parser.add_argument("--output_folder", type=str,
                        default="output/decision_extracted", help="Path to the output CSV file.")
    parser.add_argument("--decision_folder", type=str,
                        default="output/decision", help="Path to the output CSV file.")

    args = parser.parse_args()

    main(args.model_name, args.output_folder, args.decision_folder)

