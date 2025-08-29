# Creating Annotation Data

This folder contains scripts and instructions for preprocessing and annotating data.

## Workflow Overview

1. **Filtering Data**  
   - Run `select_data.py` to filter data based on length criteria. This creates a subset of data (default=200) in `data/selected_data/raw_data`.

2. **Manual Data Checking**  
   - Manually review data to filter out noisy documents by adding new column called Filter, assigning 1 to keep the document. Place cleaned data in `data/selected_data/manually_checked_data`.

3. **Creating Translation Prompts**  
   - Use `create_text_batch.py` to generate translation prompts for the GPT-4o API in batches. JSONL files are outputted to `data/selected_data/gpt_4o_batch`.

4. **API Translation**  
   - Post-translation, store API outputs in `data/selected_data/gpt_4o_batch/translation_batch_output.jsonl`.

5. **Annotation Data Preparation**  
   - Execute `create_annotation_data.py` to prepare data for annotation.

6. **Annotation Process**  
   - Annotate data using Google Sheets. Final annotated data is stored in `data/annotated_data`.

```