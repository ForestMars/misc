import sys
import os
import argparse
from pypdf import PdfReader

# Model Architecture Choice (Modern Causal LLM with System/User role handling)
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

# Terminal formatting codes (ANSI Escape Sequences)
SUMMARY_COLOR = "\033[92m"  # Green
COLOR_RESET = "\033[0m"     # White

# 1. Rigorous parameter configurations adapted for Causal Text-Generation
SUMMARY_FORMATS = {
    "tldr": {
        "max_new_tokens": 50,
        "do_sample": True,
        "system_instruction": "You are a precise research assistant. Provide a single, punchy, single-sentence summary of the text. Do not include introductory fluff."
    },
    "abstract": {
        "max_new_tokens": 250,
        "do_sample": True,
        "system_instruction": "Provide a rigorous, formal academic abstract summarizing the core methodology, data, and conclusions of the text. Maintain an objective, structural tone."
    },
    "bullets": {
        "max_new_tokens": 150,
        "do_sample": True,
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

# 2. Qualitative Style Parameters (Ordered by Descending Temperature Gradient)
SUMMARY_STYLES = {
    "descriptive": {
        "do_sample": True,
        "temperature": 0.85,          # High temperature: allows fluid lexical exploration of facts
        "repetition_penalty": 1.1,
        "no_repeat_ngram_size": 4,
        "top_p": 0.95
    },
    "interpretive": {
        "do_sample": True,
        "temperature": 0.65,          # Mid-high: encourages abstract analysis and linking
        "repetition_penalty": 1.2,
        "no_repeat_ngram_size": 3,
        "top_p": 0.92
    },
    "structural": {
        "do_sample": True,
        "temperature": 0.45,          # Mid-low: shifts balance toward formal structural mapping keywords
        "repetition_penalty": 1.3,
        "no_repeat_ngram_size": 3,
        "top_p": 0.88
    },
    "experiential": {
        "do_sample": True,
        "temperature": 0.30,          # Low: anchors choices down into concrete human observations
        "repetition_penalty": 1.3,
        "no_repeat_ngram_size": 2,
        "top_p": 0.80
    },
    "pragmatic": {
        "do_sample": True,
        "temperature": 0.15,          # Near-deterministic floor: strictly isolates explicit utility/action tokens
        "repetition_penalty": 1.4,
        "no_repeat_ngram_size": 2,
        "top_p": 0.70                 # Tight nucleus limit to keep execution clear and direct
    }
}

# 3. Parse arguments
parser = argparse.ArgumentParser(description="Summarize a binary PDF file across distinct algorithmic styles.")
parser.add_argument("file_path", help="Path to the target PDF file on your system.")
parser.add_argument("-f", "--format", choices=list(SUMMARY_FORMATS.keys()), default="tldr", help="Select the summary style architecture (default: tldr).")
parser.add_argument("-s", "--style", choices=list(SUMMARY_STYLES.keys()), default="descriptive", help="Select the summary style architecture (default: descriptive).")

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


# 6. PARAMETER-DRIVEN PIPELINE EXECUTION (FIXED MATRIX MERGE)
# =====================================================================
def run_processing_pipeline(text, format_key, style_key):
    format_cfg = SUMMARY_FORMATS[format_key]
    style_cfg = SUMMARY_STYLES[style_key]

    # Construct the base text instruction with its structural format suffix
    system_prompt = f"{BASE_SYSTEM_PROMPT}{format_cfg['suffix_prompt']}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Document Text:\n{text[:3000]}"}
    ]

    # FILTER 1: Pre-processing (Tokenization & Matrix alignment)
    model_inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)

    # CRITICAL FIX: Merge the structural length limits and the mathematical style parameters
    # into a single, cohesive keyword arguments dictionary for the generation engine.
    gen_kwargs = style_cfg.copy()
    gen_kwargs["max_new_tokens"] = format_cfg["max_new_tokens"]
    gen_kwargs["min_new_tokens"] = format_cfg["min_new_tokens"]

    # FILTER 2: Inference Engine Execution (Unpacking the true mathematical matrix)
    with torch.inference_mode():
        outputs = model.generate(
            **model_inputs,
            **gen_kwargs  # <-- Unpacks temperature, top_p, repetition_penalty, etc.
        )

    # FILTER 3: Post-processing
    prompt_length = model_inputs["input_ids"].shape[1]
    generated_tokens = outputs[0][prompt_length:]
    return tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

# 7. Execute data flow
# config = SUMMARY_PROFILES[selected_style]
# summary_output = run_processing_pipeline(document_text, config)
#
def render_matrix_dashboard(output_text, style_name, format_name, style_cfg, inquiry_text):
    """Renders a structured CLI component with strict separation of data and formatting."""
    # 1. UI Style Constants
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[92m"
    RESET = "\033[0m"
    divider = "─" * 70

    # 2. Raw Data Assignments (Zero Formatting, Pure Primitives)
    matrix_engine = style_name
    format_type = format_name
    temp_val = style_cfg["temperature"]
    topp_val = style_cfg["top_p"]
    reppen_val = style_cfg["repetition_penalty"]

    # 3. Pure Presentation Layer (All Formatters Isolated Here)
    template = (
        f"\n{DIM}[Matrix Engine: {matrix_engine.upper()} ✕ {format_type.upper()}]\n"
        f"[Parameters: temp={temp_val:.2f} | top_p={topp_val:.2f} | rep_pen={reppen_val:.2f}]{RESET}\n"
        f"{CYAN}❯ Lens Inquiry: {inquiry_text}{RESET}\n"
        f"{divider}\n"
        f"{GREEN}{output_text}{RESET}\n"
        f"{divider}\n"
    )

    print(template)


# =====================================================================
# 8. EXECUTE PASS & PARAMETRIC RENDERING
# =====================================================================
STYLE_QUESTIONS = {
    "descriptive": "What happened?",
    "interpretive": "What does it mean?",
    "structural": "How is it organized?",
    "experiential": "What was it like?",
    "pragmatic": "What matters / what should be done?"
}

# 1. Fetch configurations directly from your decoupled matrices
fmt_cfg = SUMMARY_FORMATS[selected_format]
sty_cfg = SUMMARY_STYLES[selected_style]

# 2. Run the dynamic inference engine execution pass
summary_output = run_processing_pipeline(document_text, selected_format, selected_style)

# 3. HERE IS THE CALL: It acts as the final sink for your data pipeline
render_matrix_dashboard(
    output_text=summary_output,
    style_name=selected_style,
    format_name=selected_format,
    style_cfg=sty_cfg,
    inquiry_text=STYLE_QUESTIONS[selected_style]
)

exit("bye")

print(f"\n--- {selected_style.upper()} SUMMARY ---")
print(f"{SUMMARY_COLOR}{summary_output}{COLOR_RESET}")
