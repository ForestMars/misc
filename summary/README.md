# Matrix Engine

A modular, high-performance document processing and analysis pipeline. The system combines a stateless Cython / C++ optimization speed layer, a purely declarative YAML parameter engine, and localized Deep Learning model orchestration optimized for consumer hardware.

---

## Core System Architecture

The software is explicitly engineered to maintain strict decoupling across four distinct operational boundaries:

```text
├── matrix_config.yaml  # 1. Pure Declarative Parameters (Static Schema Layout)
├── matrix_utils.pyx    # 2. Stateless Cython Functions (C++ String/View Layer)
├── setup.py            # 3. Native Extension Compiler
└── summarize.py        # 4. Pipeline Runtime Orchestrator (Logic Shell + Audio Pipeline)
```

1. **The Declarative Schema (matrix_config.yaml)**: An immutable configuration manifest containing zero execution logic. Controls prompt instructions, hyperparameters, and UI lens configuration assets.
2. **The Speed Layer (matrix_utils.pyx)**: A compiled Cython model using native C++ memory views (`libcpp.string`) to execute high-performance string modifications and raw ANSI presentation injection.
3. **The Orchestration Shell (summarize.py)**: A deferred-loading script that executes pipeline orchestration, local cache lookups, textwrap formatting, sub-process audio redirection, and device tensor allocation.

---

## Setup & Installation

### 1. Prerequisites
Ensure you are running an environment with Python 3.10+ and a C++ compiler layout (clang or gcc). Install the core dependencies:

```bash
pip install torch transformers pypdf pyyaml cython setuptools
```

### 2. Compile the Cython Speed Layer
Before running the orchestrator, you must compile the stateless C++ extensions into your local workspace. Run the setup compiler:

```bash
python setup.py build_ext --inplace
```
*This generates a native shared library module (`matrix_utils.so` on macOS/Linux or `matrix_utils.pyd` on Windows) directly inside your working directory.*

---

## Tab-Autocomplete Configuration (PDF Only)

To seamlessly autocomplete path arguments restricted exclusively to .pdf files, configure your shell environment using one of the following blocks.

### For Zsh Users (Default on macOS)

1. Open your global Zsh configuration layout:
   ```bash
   nano ~/.zshrc
   ```
2. Append the following structural completion function to the bottom of the file:
   ```bash
   # Autocomplete on PDF targets
   _summarize_pdf_autocomplete() {
       _files -g '*(pdf|PDF)'
   }

   compdef _summarize_pdf_autocomplete python summarize.py
   ```
3. Save and reload your shell:
   ```bash
   source ~/.zshrc
   ```

### For Bash Users

1. Open your global Bash configuration:
   ```bash
   nano ~/.bashrc
   ```
2. Append the following shell filtering logic:
   ```bash
   _bash_pdf_autocomplete() {
       local current_word
       current_word="${COMP_WORDS[COMP_CWORD]}"
       COMPREPLY=( $(compgen -f -X '!*.pdf' -- "$current_word") )
   }

   complete -F _bash_pdf_autocomplete python summarize.py
   ```
3. Save and reload your shell:
   ```bash
   source ~/.bashrc
   ```

---

## Runtime Invocation Matrix

Execute the orchestrator by passing a target document path along with your declarative format and sampling styles.

```bash
python summarize.py path/to/target_document.pdf -f synopsis -s descriptive -a
```

### Argument Flags

| Flag | Parameter | Choices | Description |
| :--- | :--- | :--- | :--- |
| `file_path` | Position 1 | Any valid PDF path | Target data to ingest into the pipeline. |
| `-f / --format` | Architecture | tldr, abstract, bullets, synopsis | Structural constraints / prompt alignment runner rules. |
| `-s / --style` | Sampling | descriptive, interpretive, structural, experiential, pragmatic | Quantitative hyperparameter temperature values. |
| `-a / --audio` | Execution | None (Binary Flag) | Narrates final layout text out loud via the macOS text-to-speech framework. |

---

## Performance Optimization & Diagnostics

> [!NOTE]
> If your execution trace outputs "Routing model execution matrices directly to device layout: CPU" on an Apple Silicon Mac, verify your local PyTorch installation layout matches your system framework wheels (`torch.backends.mps.is_available()`).

### Tuning Hyperparameter Loops
If your model encounters vocabulary or synonym looping crashes unformatted under low-temperature execution architectures, modify your declarative matrix values inside `matrix_config.yaml` to decouple the repetition penalty boundaries:

```yaml
summary_styles:
  pragmatic:
    do_sample: true
    temperature: 0.300          # Keep safely above absolute deterministic loops
    repetition_penalty: 1.15 # Lower value prevents recursive synonym generation
    top_p: 0.835
```
