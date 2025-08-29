from transformers import AutoTokenizer, AutoModelForCausalLM, Gemma3ForConditionalGeneration, LogitsProcessorList
import torch
import pandas as pd
import argparse
from tqdm import tqdm
import os
import re


DEVICE = "cuda"
MAX_NEW_TOKENS = 1024


def load_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, padding_side='left')
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if DEVICE == "cuda":
        if "gemma-3" in model_name:
            model = Gemma3ForConditionalGeneration.from_pretrained(model_name, device_map="auto", torch_dtype=torch.bfloat16).eval()
            #model.to(DEVICE)
        else:
            model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16, trust_remote_code=True).eval()
            #model.to(DEVICE)
    else:
        print('HI')
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
        model.to(DEVICE)
    model.config.pad_token_id = tokenizer.eos_token_id
    return model, tokenizer


def tokenize_data(tokenizer, gt_file):

    all_prompts = set_prompts(gt_file)

    # all_prompts = all_prompts[:32] + all_prompts[-32:]

    prompts_template = []
    prompt_metadata = []
    for _, prompt in enumerate(all_prompts):
        messages = tokenizer.apply_chat_template(
            prompt[0], add_generation_prompt=True, tokenize=False)
        prompts_template.append(messages)
        prompt_metadata.append(prompt[1])
    return prompts_template, prompt_metadata


def set_prompts(gt_file):

    # load gt file
    df_gt = pd.read_csv(gt_file)

    all_prompts = []
    for index, row in df_gt.iterrows():
        # Create message
        messages = [{"role": "user", "content": row["prompts"]}]

        metadata = row.to_dict()
        for key in ["prompts"]:
            metadata.pop(key, None)  # `None` prevents errors if the key isn't found

        all_prompts.append(
            [messages, metadata])
    return all_prompts



def batch_inference(input_texts, model, tokenizer, prompt_metadata, output_file, batch_size=32, num_return_sequences=1):
    """
    Perform batch inference on a list of input texts:

        Perform batch inference on a list of input texts.

    Parameters:
    - input_texts: List of strings, the texts to run inference on.
    - batch_size: int, the number of texts to process per batch.
    - max_length: int, maximum length of generated response.

    Returns:
    - List of generated responses.
    """
    results = []

    # Process each batch
    for i in tqdm(range(0, len(input_texts), batch_size)):
        batch_texts = input_texts[i:i + batch_size]

        # Tokenize and pad inputs for batch processing
        inputs = tokenizer(batch_texts, return_tensors="pt",
                           padding=True, truncation=True).to(DEVICE)
        

        # Generate predictions
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                #attention_mask=inputs["attention_mask"],
                max_new_tokens=MAX_NEW_TOKENS,
                num_return_sequences=num_return_sequences,
                pad_token_id=tokenizer.eos_token_id,  # Ensure padding if needed,
                do_sample=True,
                temperature=0.7,
                top_k=100,
                top_p=0.9,
                #logits_processor=logits_processor
            )



        # Decode the predictions and append to results
        decoded_outputs = [tokenizer.decode(
            output, skip_special_tokens=True) for output in outputs]
        decoded_outputs = [decoded_outputs[i:i+num_return_sequences] for i in range(0, len(decoded_outputs), num_return_sequences)]
        results += decoded_outputs

        if i % 30 == 0:
            save_data(results, prompt_metadata, output_file)

    return results

# Save the data
def save_data(results, prompt_metadata, output_path):
    """
    Save the processed data to a CSV file.

    Parameters:
        data (pd.DataFrame): Data with inference results to be saved.
        output_path (str): Path to the output file.
    """

    split_texts = ["assistant\\n\\n", "assistant\\n",
                  "assistant\n\n", "assistant\n", "assistant", "<|CHATBOT_TOKEN|>",
                  "\nmodel\n"]

    answers = results
    for split_text in split_texts:
        answers = [[salary.split(split_text)[-1]
                    for salary in n_seq] for n_seq in answers]
    processed_data = pd.DataFrame(prompt_metadata[:len(results)])
    processed_data["answer"] = answers
    processed_data.to_csv(output_path, index=False)
    pickle_output = output_path.replace(".csv", ".pkl")
    processed_data.to_pickle(pickle_output)


# Main workflow
def main(model_name, output_file, gt_file):
    # Step 0: Load the Model
    model, tokenizer = load_model(model_name)

    prompts, prompt_metadata = tokenize_data(tokenizer, gt_file)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Step 2: Perform inference
    #model_size = re.search(r'(\d+)b', s).group(1)
    results = batch_inference(prompts, model, tokenizer, prompt_metadata, output_file)

    save_data(results, prompt_metadata, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run inference on a dataset and save the results.")
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-72B-Instruct",
                        help="Name of the model to use for inference.")
    parser.add_argument("--output_folder", type=str,
                        default="salary_estimation/output/implicit", help="Path to the output CSV file.")
    parser.add_argument("--gt_file", type=str,
                        default="salary_estimation/data/prompts/tasks/implicit/implicit.csv", help="Path to the output CSV file.")

    args = parser.parse_args()

    model_name = args.model_name.split("/")[-1]
    print(model_name)
    print(args.gt_file)
    output_file = os.path.join(args.output_folder, model_name + ".csv")

    main(args.model_name, output_file, args.gt_file)
