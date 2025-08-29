<h1 align="center">
<span>
<span>Large Language Models Discriminate Against Speakers of German Dialects</span>
</h1>

[![arxiv preprint](https://img.shields.io/badge/arXiv-2208.01575-b31b1b.svg)](https://xxx)


We examine whether such stereotypes are mirrored by large language models (LLMs). We draw on the sociolinguistic literature on dialect perception to analyze traits commonly associated with dialect speakers. Based on these traits, we assess the *dialect naming* bias and *dialect usage* bias expressed by LLMs in two tasks: *association task* and *decision task*. To assess a model's *dialect usage* bias, we construct a novel evaluation corpus that pairs sentences from seven regional German dialects (e.g., Alemannic and Bavarian) with their standard German counterparts.


---

## 📂 Directory/File Structure Overview

- **scripts/__init__.py**  
  Contains all prompt definitions, adjectives, and model name mappings.
  
- **scripts/prompt_creation/create_tasks.py**  
  Script for creating prompt tasks based on your annotated data.
  
- **scripts/inference.py**  
  Runs the model inference to generate predictions.
  
- **scripts/eval_implicit.py**  
  Evaluates the model predictions for association task.
  
- **scripts/extract_decision.py**  
  Extracts decision outputs from the model.
  
- **scripts/eval_decision.py**  
  Evaluates the model for decision task.

- See plots/ to generate final plots

---

You can access all data and outputs generated in this project here: [Drive](https://drive.google.com/drive/folders/14Kt4z-y8WEmDwiQKzClCzDPaF80buUYp?usp=sharing).

## 0. Requirements.txt

- Python **3.12** (recommended)  
- Install dependencies with:

```bash
pip install -r requirements.txt
```

## 1. Data Creation Stage

### Steps

1. **Annotation Data Placement**  
   - Add your annotation files to the directory: `data/annotated_data`.
  
2. **Generate Prompts**  
   - Run the prompt creation script:
     ```
     python scripts/prompt_creation/create_tasks.py
     ```

---

## 2. Run Inference

### Running the Inference

1. **Dialect Usage Bias Inference**  
   - Execute the following command:
     ```
     python scripts/inference.py --model_name $MODEL_PATH --output_folder output/association_usage --gt_file data/prompts/tasks/association_usage.csv
     ```
  
2. **Dialect Naming Bias Inference**  
   - Execute the following command:
     ```
     python scripts/inference.py --model_name $MODEL_PATH --output_folder output/association_naming --gt_file data/prompts/tasks/association_naming.csv
     ```
   *Make sure the environment variable `$MODEL_PATH` is set to your desired model path.*

---

## 3. Evaluation of the Association Task 

- Run the implicit bias evaluation script:
  ```
  python scripts/eval_association.py
  ```
---

## 4. Evaluation of Decision Task

### Steps

1. **Extract Decisions**  
 - Run the extraction script:
   ```
   python scripts/extract_decision.py --model_name $MODEL_PATH
   ```

2. **Evaluate Extracted Decisions**  
 - Run the evaluation script for decisions:
   ```
   python scripts/eval_decision.py
   ```


---

## Additional Notes

- In scripts/__init__.py, we specifiy the model name mapping function that is being used in the eval scripts to clean model names up.
- Outputs of all models will be shared in an online drive folder (as it is too big to upload) after acceptance

------------------------



## License

This project is licensed under the xxxx - see the [LICENSE.md](LICENSE.md) file for details</span>