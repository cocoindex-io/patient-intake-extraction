![Structured Data From Patient Intake Forms](https://github.com/user-attachments/assets/1f6afb69-d26d-4a08-8774-13982d6aec1e)

# 🥥 Patient Intake Extraction with CocoIndex

Extract structured data from patient intake forms (PDF) using [CocoIndex](https://cocoindex.io) v1 and [DSPy](https://github.com/stanfordnlp/dspy) with a Gemini vision model. Each form is rendered to images, passed to the LLM, and written out as a validated JSON record — incrementally, so re-runs only reprocess forms that actually changed.

❤️ Please give [CocoIndex on GitHub](https://github.com/cocoindex-io/cocoindex) a star ⭐ to support us. A warm coconut hug 🥥🤗. [![GitHub](https://img.shields.io/github/stars/cocoindex-io/cocoindex?color=5B5BD6)](https://github.com/cocoindex-io/cocoindex)

## What it does

```
data/patient_forms/*.pdf  ──▶  pages → images  ──▶  DSPy + Gemini  ──▶  output_patients/*.json
```

- **Pydantic models** (`models.py`) define the target schema — type-safe, validated `Patient` records.
- **DSPy module** (`main.py`) extracts directly from page images via `ChainOfThought` with vision — no intermediate text/markdown step.
- **CocoIndex v1 app** (`main.py`) processes each form as an independent component and writes JSON, recomputing only what changed.

## Prerequisites

- **Python 3.11+**
- A **Gemini API key** — no Postgres, no Docker.

## Run

**1. Install dependencies** (sample PDFs are already in `data/patient_forms/`):

```bash
pip install -e .
```

**2. Set your API key** — copy the template and add your Gemini key:

```bash
cp .env.example .env
# then edit .env and set GEMINI_API_KEY=your_api_key_here
```

The template also sets `COCOINDEX_DB=./cocoindex.db` (the local engine state path), which is required.

**3. Extract:**

```bash
cocoindex update main.py
```

This reads each PDF in `data/patient_forms/`, extracts the patient record, and writes JSON to `output_patients/`:

```bash
ls output_patients/
# Patient_Intake_Form_David_Artificial.json
# Patient_Intake_Form_Emily_Artificial.json
# Patient_Intake_Form_Joe_Artificial.json
# Patient_Intake_From_Jane_Artificial.json
```

## Incremental processing

Re-running never redoes work that's already done — `process_patient_form` is memoized by file content:

```bash
cocoindex update main.py        # ⚡ unchanged forms are skipped
```

Add, replace, or remove a PDF and re-run — only the affected form is reprocessed, and a removed PDF's JSON is cleaned up automatically.

## How it works

The pipeline lives in [`main.py`](./main.py):

- `extract_patient` — a `@coco.fn` that renders each PDF page to an image (pymupdf) and runs a DSPy `ChainOfThought` vision module to return a validated `Patient` ([`models.py`](./models.py)).
- `process_patient_form` — a memoized `@coco.fn` that reads a file, extracts, and declares the JSON output.
- `app_main` — walks `data/patient_forms/` and mounts one component per PDF.

Each form is processed independently and memoized by content, so re-runs only touch what changed.

---

The sample forms under `data/` are purely artificial and for testing only.
