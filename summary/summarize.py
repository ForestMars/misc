import argparse
import os
import sys
import subprocess
import textwrap
import hashlib
from pathlib import Path

import yaml
from pypdf import PdfReader


# SYSTEM CACHE STATE BOUNDARIES
CACHE_DIR = Path(".cache")
PDF_TXT_DIR = CACHE_DIR / "pdf-txt"
SUMMARIES_DIR = CACHE_DIR / "summaries"

PDF_TXT_DIR.mkdir(parents=True, exist_ok=True)
SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

def get_file_hash(target_path: str) -> str:
    """Generate a stable unique signature from file content bytes."""
    hasher = hashlib.sha256()
    with open(target_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

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

if not os.path.exists(file_path):
    print(f"Error: Target file does not exist at path '{file_path}'")
    sys.exit(1)

# Generate unique identity fingerprints for the target data asset
pdf_hash = get_file_hash(file_path)
results_cache_file = SUMMARIES_DIR / f"{pdf_hash}_{selected_format}_{selected_style}.txt"
document_cache_file = PDF_TXT_DIR / f"{pdf_hash}.txt"


# STAGE 1 CACHE LAYER: INSTANT COMPLED RESULTS CHECK
if results_cache_file.exists():
    print(f"★ Cache Hit [Stage 1/2]: Pre-compiled matrix matching (-f {selected_format} -s {selected_style}) located. Rendering view instantly.")
    summary_output = results_cache_file.read_text(encoding="utf-8")

    # Process the cached text string back through your dashboard rendering engine
    sty_cfg = cfg["summary_styles"][selected_style]
    wrapped_lines = []
    for raw_line in summary_output.splitlines():
        stripped = raw_line.lstrip()
        if stripped.startswith(("- ", "* ", "• ")):
            leading_indent_count = len(raw_line) - len(stripped)
            indent_spaces = " " * (leading_indent_count + 2)
            bullet_wrapped = textwrap.wrap(raw_line, width=70, subsequent_indent=indent_spaces)
            wrapped_lines.extend(bullet_wrapped)
        elif not stripped:
            wrapped_lines.append("")
        else:
            wrapped_lines.extend(textwrap.wrap(raw_line, width=70))

    clean_wrapped_text = "\n".join(wrapped_lines)

    from matrix_utils import c_render_dashboard
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
        subprocess.run(["say", "--", summary_output])
    sys.exit(0)

# STAGE 2 CACHE LAYER: DOCUMENT PARSING INGESTION CHECK
document_text = ""
if document_cache_file.exists():
    print("⚡ Cache Hit [Stage 2/2]: Pre-parsed document plain text located. Skipping PDF ingestion layer.")
    document_text = document_cache_file.read_text(encoding="utf-8")
else:
    print("⚠ Cache Miss [Stage 2/2]: Ingesting and parsing raw binary PDF layout asset...")
    try:
        reader = PdfReader(file_path)
        extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        document_text = "\n".join(extracted_pages)
        if not document_text.strip():
            sys.exit("Error: Could not extract any text.")

        # Save pristine plain-text artifact to disk
        document_cache_file.write_text(document_text, encoding="utf-8")
        print(f"✓ Saved pristine text layout asset to: {document_cache_file}")
    except Exception as e:
        sys.exit(f"Error reading PDF file: {e}")

# 3. UNTOUCHED MACHINE LEARNING FRAMEWORK INITIALIZATION
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

# 4. RUNTIME PIPELINE EXECUTION ENGINE
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

# 5. EXECUTION & PRESENTATION SINK
sty_cfg = cfg["summary_styles"][selected_style]

# Run processing pass using loaded settings
summary_output = run_processing_pipeline(document_text, selected_format, selected_style)

# Cache the fresh inference string artifact before running dashboard layout string mutations
results_cache_file.write_text(summary_output, encoding="utf-8")
print(f"✓ Committed finalized summary layout asset to: {results_cache_file}")

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
    # Send the raw text summary to the native macOS audio layer with flag insulation
    subprocess.run(["say", "--", summary_output])
