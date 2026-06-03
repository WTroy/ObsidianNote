# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

This is an Obsidian vault with PARA structure (10-Projects, 20-Areas, 30-Resources, 40-Archives) and Python scripts for AI-powered note management.

## Python Environment

Before running any Python scripts, activate the Conda environment:

```bash
conda activate obsidian
```

All Python dependencies should be installed and executed within the `obsidian` environment.

## Architecture

- **vault_llm.py** - Shared LLM and utility module providing:
  - `load_config()` - Reads `90-System/config.json`
  - `normalize_api_url()` - Auto-completes API paths for OpenAI/Anthropic providers
  - `call_llm()` - Unified LLM API caller (supports OpenAI and Anthropic)
  - `get_embeddings()` - Embedding API for semantic similarity
  - `find_similar_notes()` - Find similar notes using embeddings
  - `assess_content_quality()` - Evaluate note quality (1-10 score)
  - `assess_timeliness()` - Check if content is time-sensitive
  - `parse_frontmatter_list()` / `merge_frontmatter_list()` - Frontmatter helpers
  - `C` class and `colored()` - Terminal ANSI colors
- **import_youdao.py** - Imports Youdao notes from PDF exports, adds AI-powered bi-directional links
- **organize.py** - AI-powered note organization with:
  - Inbox note analysis and PARA directory assignment
  - Global vault re-analysis with duplicate detection
  - Quality assessment and improvement suggestions
- **90-System/format_markdown_notes.py** - Conservative local formatter for imported notes:
  - Adds code fences for command/config/code snippets
  - Merges duplicated `related` frontmatter and related-note sections
  - Repairs PDF-export SQL artifacts such as glued line numbers and split SQL fences
- **90-System/config.json** - Configuration for LLM and embedding services

## Running Scripts

```bash
# Import Youdao notes
python import_youdao.py /path/to/exported/folder
python import_youdao.py /path/to/exported/folder --dry-run

# Analyze and add bi-directional links
python import_youdao.py --link
python import_youdao.py --link --dry-run

# Organize inbox notes
python organize.py
python organize.py --dry-run  # Preview only
python organize.py --auto    # Auto-confirm all suggestions

# Global vault re-analysis
python organize.py --global              # Interactive mode
python organize.py --global --dry-run    # Preview only
python organize.py --global --auto       # Auto-confirm all

# Format imported Markdown notes
python 90-System/format_markdown_notes.py          # Preview only
python 90-System/format_markdown_notes.py --apply  # Apply formatting fixes
```

## Configuration

Edit `90-System/config.json`:
```json
{
  "llm": {
    "provider": "openai|anthropic",
    "api_url": "http://127.0.0.1:8000/v1/chat/completions",
    "api_key": "your-key",
    "model": "model-name"
  },
  "embedding": {
    "api": "http://127.0.0.1:8000/v1",
    "model": "bge-m3-mlx-4bit",
    "api_key": "your-embedding-key"
  }
}
```

The `normalize_api_url()` function auto-completes partial URLs:
- OpenAI: appends `/v1/chat/completions` if needed
- Anthropic: appends `/v1/messages` if needed
