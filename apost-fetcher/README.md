# BUILD AI Code Extractor

Scrapes the full [BUILD AI](https://buildai.substack.com) series, extracts
fenced code blocks from every post, names each file with Claude AI, and
writes a clean local directory tree you can `git push` straight to GitHub.

## Output structure

```
buildai_repo/
├── module_1_foundation_model_training/
│   ├── unit_1_distributed_training/
│   │   ├── 01_tensor_parallelism/
│   │   │   ├── naive_multi_head_attention.py
│   │   │   ├── tensor_parallel_attention.py
│   │   │   └── post.md   ← prose only, code replaced with file links
│   │   └── 02_pipeline_parallelism/
│   └── unit_2_data_pipeline/
└── module_2_training_large_models/
```

`post.md` contains the full article with each code block replaced by a
labelled link to the corresponding file in the same directory.

## Setup

```bash
pip install anthropic requests beautifulsoup4 lxml
export ANTHROPIC_API_KEY="sk-ant-..."
python substack_extractor.py
```

## Then push to GitHub

```bash
cd buildai_repo
git init && git add .
git commit -m "feat: import buildai.substack.com code examples"
git remote add origin https://github.com/YOU/YOUR_REPO.git
git push -u origin main
```

## Notes
- Paywalled posts yield only the free-preview code.
- Re-running overwrites files in place (idempotent).
- ~1 Claude Sonnet API call per post that has code.
- Edit OUTPUT_DIR at the top of the script to change destination.
