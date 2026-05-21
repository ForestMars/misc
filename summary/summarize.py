import argparse
import os
import sys
import subprocess
import textwrap

import yaml
from pypdf import PdfReader

CACHE_DIR = Path(".cache")
PDF_TXT_DIR = CACHE_DIR / "pdf-txt"
SUMMARIES_DIR = CACHE_DIR / "summaries"
CONFIG_FILE = Path("matrix_config.yaml")

# 1. Deserialize the absolute configuration state before compiling logic
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matrix_config.yaml")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
except Exception as e:
    sys.exit(f"Fatal: Failed to load declarative configuration schema: {e}")

# 2. Parse arguments against the validated yaml structures
parser = argparse.ArgumentParser(description="Summarize a binary PDF file across distinct algorithmic styles.")
parser.add_argument("file_path", help="Path to the target PDF file on your system.")
parser.add_argument("-f", "--format", choices=list(cfg["summary_formats"].keys()), default="tldr", help="Select summary architecture.")
parser.add_argument("-s", "--style", choices=list(cfg["summary_styles"].keys()), default="descriptive", help="Select style matrix.")
parser.add_argument("-a", "--audio", action="store_true", help="Narrate final presentation via macOS text-to-speech engine.")

args = parser.parse_args()
file_path = args.file_path
selected_format = args.format
selected_style = args.style

# Subdirectory Cache Management
script_dir = os.path.dirname(os.path.abspath(__file__))
cache_dir = os.path.join(script_dir, ".cache")
os.makedirs(cache_dir, exist_ok=True)

base_filename = os.path.basename(file_path)
cache_path = os.path.join(cache_dir, base_filename + ".txt")

if not os.path.exists(file_path) and not os.path.exists(cache_path):
    print(f"Error: Target file does not exist at path '{file_path}'")
    sys.exit(1)

if os.path.exists(cache_path):
    with open(cache_path, "r", encoding="utf-8") as f:
        document_text = f.read()
else:
    try:
        reader = PdfReader(file_path)
        extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        document_text = "\n".join(extracted_pages)
        if not document_text.strip():
            sys.exit("Error: Could not extract any text.")
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(document_text)
    except Exception as e:
        sys.exit(f"Error reading PDF file: {e}")

# 3. Deferred ML Initialization Frameworks
print("Loading core machine learning frameworks...")
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
try:
    from matrix_utils import c_slice_document, c_build_system_instruction, c_render_dashboard
except ImportError:
    sys.exit("Fatal: Compiled Cython binary module 'matrix_utils' not found. Run 'python setup.py build_ext --inplace' first.")

print(f"Initializing model '{cfg['model_id']}'...")
tokenizer = AutoTokenizer.from_pretrained(cfg['model_id'])

# Detect device natively: Use Apple Silicon MPS if available, otherwise fall back to CPU
device_target = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Routing model execution matrices directly to device layout: {device_target.upper()}")

model = AutoModelForCausalLM.from_pretrained(
    cfg['model_id'],
    torch_dtype=torch.bfloat16,
    device_map=device_target # Binds execution straight to your Apple Silicon layout
)

# =====================================================================
# 4. RUNTIME PIPELINE EXECUTION ENGINE
# =====================================================================
def run_processing_pipeline(text, format_key, style_key):
    format_cfg = cfg["summary_formats"][format_key]
    style_cfg = cfg["summary_styles"][style_key]

    # Process text input boundary through native C++ buffer slicing
    optimized_text = c_slice_document(text, max_chars=3000)

    # Compile instruction payload via stateless string builder
    system_prompt = c_build_system_instruction(
        base_instruction=format_cfg["system_instruction"],
        style_nudge=cfg["style_nudges"][style_key]
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Document Text:\n{optimized_text}"}
    ]

    model_inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt"
    ).to(model.device)

    gen_kwargs = style_cfg.copy()
    gen_kwargs.update({
        "max_new_tokens": format_cfg["max_new_tokens"],
        "min_new_tokens": format_cfg["min_new_tokens"],
        "use_cache": True,
        "return_dict_in_generate": False,
        "pad_token_id": tokenizer.eos_token_id
    })

    with torch.inference_mode():
        outputs = model.generate(**model_inputs, **gen_kwargs)

    prompt_length = model_inputs["input_ids"].shape[1]
    return tokenizer.decode(outputs[0][prompt_length:], skip_special_tokens=True).strip()

# =====================================================================
# 5. EXECUTION & PRESENTATION SINK
# =====================================================================
sty_cfg = cfg["summary_styles"][selected_style]

# Run processing pass using loaded settings
summary_output = run_processing_pipeline(document_text, selected_format, selected_style)
# wrapped_output_lines = textwrap.wrap(summary_output, width=70)

# Bullet-safe intelligent wrapper matrix
wrapped_lines = []
for raw_line in summary_output.splitlines():
    stripped = raw_line.lstrip()

    # Detect markdown bullet points dynamically
    if stripped.startswith(("- ", "* ", "• ")):
        # Calculate how many spaces exist before the bullet icon
        leading_indent_count = len(raw_line) - len(stripped)
        indent_spaces = " " * (leading_indent_count + 2) # Matches item text start

        # Wrap the bullet line, matching the subsequent margin depths
        bullet_wrapped = textwrap.wrap(
            raw_line,
            width=70,
            subsequent_indent=indent_spaces
        )
        wrapped_lines.extend(bullet_wrapped)

    elif not stripped:
        # Maintain your explicit layout spacing paragraphs intact
        wrapped_lines.append("")
    else:
        # Standard paragraph blocks wrap without indents
        wrapped_lines.extend(textwrap.wrap(raw_line, width=70))

clean_wrapped_text = "\n".join(wrapped_lines)

# Pass exact primitives out to the immutable view layer function
c_render_dashboard(
    output_text=clean_wrapped_text,
    style_name=selected_style,
    format_name=selected_format,
    temperature=sty_cfg["temperature"],
    top_p=sty_cfg["top_p"],
    repetition_penalty=sty_cfg["repetition_penalty"],
    inquiry_text=cfg["style_questions"][selected_style]
)

if args.audio:
    print("\nNarrating output text via system audio channel...")
    # Send the raw text summary to the native macOS audio layer
    subprocess.run(["say", summary_output])
