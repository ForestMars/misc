import sys
import os
import argparse
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from transformers.pipelines.text2text_generation import Text2TextGenerationPipeline
from pypdf import PdfReader

# 1. Define the rigorous parameter configurations for our Summary Styles
SUMMARY_PROFILES = {
    "tldr": {
        "max_length": 45,
        "min_length": 15,
        "length_penalty": 0.4,
        "repetition_penalty": 1.3,
        "no_repeat_ngram_size": 2,
        "do_sample": False
    },
    "abstract": {
        "max_length": 250,
        "min_length": 90,
        "length_penalty": 1.6,
        "repetition_penalty": 1.1,
        "no_repeat_ngram_size": 4,
        "do_sample": False
    },
    "bullets": {
        "max_length": 150,
        "min_length": 50,
        "length_penalty": 0.8,
        "repetition_penalty": 1.5,
        "no_repeat_ngram_size": 2,
        "do_sample": False
    },
    "synopsis": {
        "max_length": 180,
        "min_length": 60,
        "length_penalty": 1.2,
        "repetition_penalty": 1.2,
        "no_repeat_ngram_size": 3,
        "do_sample": True,
        "temperature": 0.85
    }
}

# 2. Set up robust CLI argument parsing
parser = argparse.ArgumentParser(
    description="Summarize a binary PDF file across distinct algorithmic styles."
)
parser.add_argument(
    "file_path", 
    help="Path to the target PDF file on your system."
)
parser.add_argument(
    "-s", "--style", 
    choices=list(SUMMARY_PROFILES.keys()), 
    default="tldr",
    help="Select the summary style architecture (default: tldr)."
)

args = parser.parse_args()
file_path = args.file_path
selected_style = args.style

# 3. Subdirectory Cache Management
script_dir = os.path.dirname(os.path.abspath(__file__))
cache_dir = os.path.join(script_dir, ".cache")
os.makedirs(cache_dir, exist_ok=True)

base_filename = os.path.basename(file_path)
cache_path = os.path.join(cache_dir, base_filename + ".txt")

# 4. Handle Text Extraction / Cache Verification
if os.path.exists(cache_path):
    print(f"Found cached text in subdirectory. Loading '{cache_path}'...")
    with open(cache_path, "r", encoding="utf-8") as f:
        document_text = f.read()
else:
    print(f"Cache miss. Extracting binary PDF data from '{file_path}'...")
    try:
        reader = PdfReader(file_path)
        extracted_pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_pages.append(text)
                
        document_text = "\n".join(extracted_pages)
        
        if not document_text.strip():
            print("Error: Could not extract any text. The PDF might be scanned images.")
            sys.exit(1)
            
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(document_text)
        print(f"Saved text dump safely inside subdirectory: '{cache_path}'")
            
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        sys.exit(1)

# 5. Initialize the Pipeline explicitly (bypasses broken string registries)
print(f"Initializing pipeline with style profile: '{selected_style.upper()}'...")
model_id = "google-t5/t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

summarizer = pipeline(
    task="text2text-generation",
    model=model,
    tokenizer=tokenizer,
    pipeline_class=Text2TextGenerationPipeline
)

# 6. Explode the configuration dictionary directly into the pipeline executor
config = SUMMARY_PROFILES[selected_style]

result = summarizer(
    "summarize: " + document_text,
    truncation=True,
    **config
)

# 7. Deliver the structured output
print(f"\n--- {selected_style.upper()} SUMMARY ---")
print(result[0]['generated_text'].strip())
