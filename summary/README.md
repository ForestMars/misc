# Matrix Engine

A modular, high-performance document processing and analysis pipeline. The system combines a stateless Cython / C++ optimization speed layer, a purely declarative YAML parameter engine, and localized Deep Learning model orchestration optimized for consumer hardware.

---

## Core System Architecture

The software is explicitly engineered to maintain strict decoupling across four distinct operational boundaries:

```text
├── matrix_config.yaml  # 1. Pure Declarative Parameters (Static Schema)
├── matrix_utils.pyx    # 2. Stateless Cython Functions (C++ String/View Layer)
├── setup.py            # 3. Native Extension Compiler
└── summarize.py        # 4. Pipeline Runtime Orchestrator (Logic Shell)

Markdown# Matrix Engine

A modular, high-performance document processing and analysis pipeline. The system combines a stateless Cython / C++ optimization speed layer, a purely declarative YAML parameter engine, and localized Deep Learning model orchestration optimized for consumer hardware.

The Declarative Schema (matrix_config.yaml): An immutable configuration manifest containing zero execution logic. Controls prompt instructions, hyperparameters, and UI lens configurations.The Speed Layer (matrix_utils.pyx): A compiled Cython module using native C++ memory views (libcpp.string) to execute high-speed string modifications and raw ANSI presentation injection.The Orchestration Shell (summarize.py): A deferred-loading script that executes pipeline orchestration, local cache lookups, and device tensor allocation.Setup & Installation1. PrerequisitesEnsure you are running an environment with Python 3.10+ and a C++ compiler layout (clang or gcc). Install the core dependencies:Bashpip install torch transformers pypdf pyyaml cython setuptools
2. Compile the Cython Speed LayerBefore running the orchestrator, you must compile the stateless C++ extensions into your local workspace. Run the setup compiler:Bashpython setup.py build_ext --inplace
This generates a native shared library module (matrix_utils.so on macOS/Linux or matrix_utils.pyd on Windows) directly inside your working directory.Tab-Autocomplete ConfigurationTo seamlessly autocomplete path arguments restricted only to .pdf files, configure your shell environment using one of the following blocks.For Zsh Users (Default on macOS)Open your global Zsh configuration layout:Bashnano ~/.zshrc

2. Append the following structural completion function to the bottom of the file:
   ```bash
   # Autocomplete engine for matrix engine PDF targets
   _summarize_pdf_autocomplete() {
       _files -g '*.(pdf|PDF)'
   }
   
   # Register the autocomplete target for python summarize.py execution
   compdef _summarize_pdf_autocomplete python summarize.py
   
Save (Ctrl+O, Enter) and exit (Ctrl+X), then reload your shell environment:Bashsource ~/.zshrc
For Bash UsersOpen your global Bash configuration layout:Bashnano ~/.bashrc

2. Append the following shell filtering logic to the bottom of the file:
   ```bash
   _bash_pdf_autocomplete() {
       local current_word
       current_word="${COMP_WORDS[COMP_CWORD]}"
       
       # Filter local directories for matching PDF targets dynamically
       COMPREPLY=( $(compgen -f -X '!*.pdf' -- "$current_word") )
   }
   
   # Bind completion mechanics directly to your runner script
   complete -F _bash_pdf_autocomplete python summarize.py
Save (Ctrl+O, Enter) and exit (Ctrl+X), then reload your shell environment:Bashsource ~/.bashrc
Runtime Invocation MatrixExecute the orchestrator by passing a target document path along with your declarative format and sampling styles.Bashpython summarize.py path/to/target_document.pdf -f synopsis -s descriptive
Argument FlagsFlagParameterChoicesDescriptionfile_pathPosition 1Any valid PDF pathTarget data to ingest into the pipeline.-f / --formatArchitecturetldr, abstract, bullets, synopsisStructural constraints / prompt alignment rules.-s / --styleSamplingdescriptive, interpretive, structural, experiential, pragmaticQuantitative hyperparameter temperature tokens.Performance Optimization & Diagnostics[!NOTE]If your execution trace outputs "Routing model execution matrices directly to device layout: CPU" on an Apple Silicon Mac, verify your local PyTorch installation layout matches your system framework wheels (torch.backends.mps.is_available()).Tuning Hyperparameter LoopsIf your model encounters vocabulary or synonym looping crashes under low-temperature execution architectures, modify your declarative matrix values inside matrix_config.yaml to decouple the repetition penalty boundaries:YAMLsummary_styles:
  pragmatic:
    do_sample: true
    temperature: 0.30       # Keep safely above absolute deterministic loops
    repetition_penalty: 1.15 # Lower value prevents recursive synonym generation
    top_p: 0.85
