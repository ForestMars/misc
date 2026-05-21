import sys
import os
import argparse
from pypdf import PdfReader

# =====================================================================
# HOISTED CONFIGURATION CONSTANTS
# =====================================================================
# Terminal formatting codes (ANSI Escape Sequences)
# Common options: GREEN = "\033[92m", BLUE = "\033[94m", CYAN = "\033[96m", YELLOW = "\033[93m"
SUMMARY_COLOR = "\033[92m"  
COLOR_RESET = "\033[0m"     # Resets the terminal back to white/default text

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

# 2. Parse arguments (Let argparse exit naturally for -h/--help without blocking it)
parser = argparse.ArgumentParser(
    description="Summarize a binary PDF file across distinct algorithmic styles."
)
parser.add_argument("file_path", help="Path to the target PDF file on your system.")
parser.add_argument("-s", "--style", choices=list(SUMMARY_PROFILES.keys()), default="tldr", help="Select the summary style architecture (default: tldr).")

args = parser.parse_args()
file_path = args.file_path
selected_style = args.style

# 3. Subdirectory Cache Management
script_dir = os.path.dirname(os.path.abspath(__file__))
cache_dir = os.path.join(script_dir, ".cache")
os.makedirs(cache_dir, exist_ok=True)

base_filename = os.path.basename(file_path)
cache_path = os.path.join(cache_dir, base_filename + ".txt")

# Verify PDF existence before loading massive ML libraries
if not os.path.exists(file_path) and not os.path.exists(cache_path):
    print(f"Error: Target file does not exist at path '{file_path}'")
    sys.exit(1)

if os.path.exists(cache_path):
    print(f"Found cached text in subdirectory. Loading '{cache_path}'...")
    with open(cache_path, "r", encoding="utf-8") as f:
        document_text = f.read()
else:
    print(f"Cache miss. Extracting binary PDF data from '{file_path}'...")
    try:
        reader = PdfReader(file_path)
        extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        document_text = "\n".join(extracted_pages)
        if not document_text.strip():
            print("Error: Could not extract any text. The PDF might be scanned images.")
            sys.exit(1)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(document_text)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        sys.exit(1)

# 4. DEFERRED IMPORTS: Only load heavy frameworks if validation passes
print("Loading core machine learning frameworks...")
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 5. Initialize weights and tokenizer
print(f"Initializing model using style profile: '{selected_style.upper()}'...")
model_id = "google-t5/t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

# 6. Explicitly Defined Processing Pipeline (Pipes & Filters Structure)
def run_processing_pipeline(text, style_config):
    # FILTER 1: Pre-processing (Raw String -> Token ID Tensors)
    inputs = tokenizer(
        "summarize: " + text, 
        max_length=1000, 
        truncation=True, 
        return_tensors="pt"
    )
    
    # Map pipeline argument names to direct model parameters smoothly
    gen_kwargs = style_config.copy()
    if "max_length" in gen_kwargs:
        gen_kwargs["max_new_tokens"] = gen_kwargs.pop("max_length")
    if "min_length" in gen_kwargs:
        gen_kwargs["min_new_tokens"] = gen_kwargs.pop("min_length")

    # FILTER 2: Inference Engine Execution (Isolated Tensor Generation Loop)
    with torch.inference_mode():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            **gen_kwargs
        )
        
    # FILTER 3: Post-processing (Tokens -> Cleaned String Output)
    decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded_output.strip()

# 7. Execute data flow
config = SUMMARY_PROFILES[selected_style]
summary_output = run_processing_pipeline(document_text, config)

# Print out using the hoisted color configuration
print(f"\n--- {selected_style.upper()} SUMMARY ---")
print(f"{SUMMARY_COLOR}{summary_output}{COLOR_RESET}")
