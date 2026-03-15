"""
Excel to LLM Input Converter
==============================
Converts a multi-sheet Q&A Excel file into structured formats
that can be fed as input to a Large Language Model (LLM).

Outputs:
  1. qa_full_text.txt        → Plain text (Q: ... A: ...) for LLM context/system prompt
  2. qa_complete_pairs.json  → Only rows with both Question + Answer (for RAG / fine-tuning)
  3. qa_missing_answers.json → Questions that still have no answer (to fill manually)
  4. qa_data.json            → Full structured data grouped by Sheet → Section → Q&A

Requirements:
  pip install pandas openpyxl
"""

import pandas as pd
import json
import re

# ── Config ─────────────────────────────────────────────────────────────────────

EXCEL_FILE = "QA_Sessions_for_AI_.xlsx"

# Map each sheet to how its columns are laid out:
#   "3col"  → [Index | Question | Answer]  (some rows are section headers)
#   "2col"  → [Index | Question]           (no answer column)
#   "flat"  → [Question | Answer]          (no index, sections as plain rows)

SHEET_CONFIG = {
    "QA Session for AI ":              "flat",
    "CSE CSBS | IoT ":                 "3col",
    "ECE | EEE | IT ":                 "2col",
    "Chemical |Textile ":              "3col",
    "CSE General ":                    "2col",
    "CSE AI & ML | CSE Data Science ": "3col",
    "Food Tech | B.Sc Agriculture ":   "3col",
    "Civil | Mechanical Eng":          "2col",
    "BioTech | Bio Medical ":          "2col",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def clean(val):
    """Convert cell value to string and strip whitespace; return '' for empty."""
    return "" if pd.isna(val) else str(val).strip()

def is_section_header(c0, c1, c2):
    """A row is a section header if col-0 is empty, col-1 has text, col-2 is empty."""
    return not c0 and c1 and not c2

def strip_number(text):
    """Remove leading numbering like '1.' or '1)' from question text."""
    return re.sub(r"^\d+[\.\)]\s*", "", text).strip()

# ── Sheet Parsers ──────────────────────────────────────────────────────────────

def parse_flat(sheet_name):
    """
    Flat layout: no index column.
    col-0 = Question (may include leading number like '1. ...')
    col-1 = Answer
    Rows without col-1 are treated as section headers.
    """
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=None)
    sections = {}
    current_section = sheet_name.strip()
    qa_list = []

    for _, row in df.iterrows():
        c1 = clean(row[1]) if len(row) > 1 else ""
        c2 = clean(row[2]) if len(row) > 2 else ""

        if not c1 and not c2:
            continue  # blank row — skip

        if c1 and not c2:
            # Could be a section header (no answer)
            if qa_list:
                sections[current_section] = qa_list
            current_section = c1
            qa_list = []
        elif c1 and c2:
            qa_list.append({
                "question": strip_number(c1),
                "answer": c2
            })

    if qa_list:
        sections[current_section] = qa_list
    return sections


def parse_3col(sheet_name):
    """
    3-column layout: [Index | Question | Answer]
    Rows where index is empty and answer is empty = section headers.
    """
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=None)
    sections = {}
    current_section = sheet_name.strip()
    qa_list = []

    for _, row in df.iterrows():
        c0 = clean(row[0])
        c1 = clean(row[1]) if len(row) > 1 else ""
        c2 = clean(row[2]) if len(row) > 2 else ""

        if not c0 and not c1 and not c2:
            continue  # blank row

        if is_section_header(c0, c1, c2):
            if qa_list:
                sections[current_section] = qa_list
            current_section = c1
            qa_list = []
        elif c1:
            qa_list.append({
                "question": c1,
                "answer": c2 if c2 else None
            })

    if qa_list:
        sections[current_section] = qa_list
    return sections


def parse_2col(sheet_name):
    """
    2-column layout: [Index | Question]  — answers are missing entirely.
    Section headers are rows where index is empty.
    """
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=None)
    sections = {}
    current_section = sheet_name.strip()
    qa_list = []

    for _, row in df.iterrows():
        c0 = clean(row[0])
        c1 = clean(row[1]) if len(row) > 1 else ""

        if not c0 and not c1:
            continue  # blank row

        if not c0 and c1:
            # Section header (no index number)
            if qa_list:
                sections[current_section] = qa_list
            current_section = c1
            qa_list = []
        elif c1:
            qa_list.append({
                "question": c1,
                "answer": None   # answer column doesn't exist in this sheet
            })

    if qa_list:
        sections[current_section] = qa_list
    return sections

# ── Main Conversion ────────────────────────────────────────────────────────────

PARSERS = {
    "flat": parse_flat,
    "3col": parse_3col,
    "2col": parse_2col,
}

def convert_excel(excel_path=EXCEL_FILE):
    xl = pd.ExcelFile(excel_path)
    all_data = {}

    for sheet_name in xl.sheet_names:
        layout = SHEET_CONFIG.get(sheet_name, "3col")
        parser = PARSERS[layout]
        all_data[sheet_name.strip()] = parser(sheet_name)
        print(f"  ✓ Parsed sheet: '{sheet_name.strip()}' [{layout}]")

    return all_data

# ── Output Writers ─────────────────────────────────────────────────────────────

def write_full_text(data, out_path="qa_full_text.txt"):
    """Plain text format — best for pasting directly into an LLM prompt."""
    lines = ["# University Q&A Knowledge Base\n"]

    for sheet, sections in data.items():
        lines.append(f"\n## {sheet}\n")
        for section, qas in sections.items():
            lines.append(f"\n### {section}\n")
            for qa in qas:
                lines.append(f"Q: {qa['question']}")
                lines.append(f"A: {qa['answer'] if qa['answer'] else '[ANSWER MISSING]'}")
                lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  → Saved: {out_path}")


def write_complete_pairs(data, out_path="qa_complete_pairs.json"):
    """JSON list of rows that have BOTH a question and an answer — for RAG or fine-tuning."""
    complete = []
    for sheet, sections in data.items():
        for section, qas in sections.items():
            for qa in qas:
                if qa["answer"] and str(qa["answer"]).strip():
                    complete.append({
                        "source": sheet,
                        "category": section,
                        "question": qa["question"],
                        "answer": qa["answer"]
                    })

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(complete, f, indent=2, ensure_ascii=False)
    print(f"  → Saved: {out_path}  ({len(complete)} complete Q&A pairs)")


def write_missing_answers(data, out_path="qa_missing_answers.json"):
    """JSON list of questions that still have no answer — so you can fill them in."""
    missing = []
    for sheet, sections in data.items():
        for section, qas in sections.items():
            for qa in qas:
                if not qa["answer"] or not str(qa["answer"]).strip():
                    missing.append({
                        "source": sheet,
                        "category": section,
                        "question": qa["question"]
                    })

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(missing, f, indent=2, ensure_ascii=False)
    print(f"  → Saved: {out_path}  ({len(missing)} questions need answers)")


def write_full_json(data, out_path="qa_data.json"):
    """Full structured JSON grouped by Sheet → Section → Q&A list."""
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  → Saved: {out_path}")

# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n📄 Step 1: Reading Excel sheets...")
    data = convert_excel()

    print("\n💾 Step 2: Writing output files...")
    write_full_text(data)
    write_complete_pairs(data)
    write_missing_answers(data)
    write_full_json(data)

    print("\n✅ Done! Files are ready to feed into your LLM.")
