import sys
import os
import argparse
from pypdf import PdfReader

# =====================================================================
# HOISTED CONFIGURATION CONSTANTS
# =====================================================================
# Model Architecture Choice (Modern Causal LLM with System/User role handling)
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

# Terminal formatting codes (ANSI Escape Sequences)
SUMMARY_COLOR = "\033[92m"  # Green
COLOR_RESET = "\033[0m"     # White

# 1. Rigorous parameter configurations adapted for Causal Text-Generation
SUMMARY_PROFILES = {
    "tldr": {
        "max_new_tokens": 50,
        "do_sample": False,
        "system_instruction": "You are a precise research assistant. Provide a single, punchy, single-sentence summary of the text. Do not include introductory fluff."
    },
    "abstract": {
        "max_new_tokens": 250,
        "do_sample": False,
        "system_instruction": "Provide a rigorous, formal academic abstract summarizing the core methodology, data, and conclusions of the text. Maintain an objective, structural tone."
    },
    "bullets": {
        "max_new_tokens": 150,
        "do_sample": False,
        "system_instruction": (
            "You are an expert executive editor. Summarize the text into a tight, professional bulleted list.\n"
            "CRITICAL CONSTRAINTS:\n"
            "- Use telegraphic style (drop passive articles like 'the article explores', 'this paper focuses on').\n"
            "- Begin each bullet with a strong action verb or clear noun phrase.\n"
            "- THe list of bullets can be titled something like Key Points\n"
            "- Keep phrases extremely concise. Eliminate parenthetical clauses and use 'e.g.' instead of 'such as'."
        )
    },
    "synopsis": {
        "max_new_tokens": 200,
        "do_sample": True,
        "temperature": 0.75,
        "system_instruction": "Provide an engaging, conceptual synopsis of the provided text, capturing its underlying narrative and thematic goals."
    }
}

# 2. Parse arguments
parser = argparse.ArgumentParser(description="Summarize a binary PDF file across distinct algorithmic styles.")
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

# 4. DEFERRED IMPORTS
print("Loading core machine learning frameworks...")
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# 5. Initialize weights and tokenizer using Causal LM classes
print(f"Initializing model '{MODEL_ID}' using style profile: '{selected_style.upper()}'...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype="auto", device_map="auto")

# 6. Causal Prompting Processing Pipeline
def run_processing_pipeline(text, style_config):
    messages = [
        {"role": "system", "content": style_config["system_instruction"]},
        {"role": "user", "content": f"Document Text:\n{text[:3000]}"}
    ]
    
    # FILTER 1: Pre-processing (Using return_dict=True to enforce 2D batched format)
    model_inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)
    
    # Isolate inference arguments
    gen_kwargs = style_config.copy()
    gen_kwargs.pop("system_instruction", None)

    # FILTER 2: Inference Engine Execution
    with torch.inference_mode():
        outputs = model.generate(
            **model_inputs,
            **gen_kwargs
        )
        
    # FILTER 3: Post-processing (Slice away the initial prompt matrix tokens)
    prompt_length = model_inputs["input_ids"].shape[1]
    generated_tokens = outputs[0][prompt_length:]
    decoded_output = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    return decoded_output.strip()

# 7. Execute data flow
config = SUMMARY_PROFILES[selected_style]
summary_output = run_processing_pipeline(document_text, config)

print(f"\n--- {selected_style.upper()} SUMMARY ---")
print(f"{SUMMARY_COLOR}{summary_output}{COLOR_RESET}")
