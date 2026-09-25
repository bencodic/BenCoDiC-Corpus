#!/usr/bin/env python3
"""
Clean the BenCoDiC corpus while preserving caption-comment-reply hierarchy.

Cleaning operations:
- remove U+200C zero-width non-joiner
- correct spacing around common delimiters
- remove HTML tags and hyperlinks
- collapse redundant whitespace
- remove empty samples
- remove samples containing only English/Bengali digits
- remove samples containing letters from scripts other than Bengali or Latin
- retain valid single-word and emoji-only samples
- cascade deletion from caption -> comments/replies and comment -> replies

Requirements:
    pandas
    openpyxl
"""

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd


HTML_TAG_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"http\S+|www\.\S+", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")
NUMERIC_ONLY_RE = re.compile(r"^[0-9০-৯\s]+$")
DELIMITER_SPACE_RE = re.compile(r"(?<=[,.।॥?!])(?=[^\s])")
SPACE_BEFORE_DELIMITER_RE = re.compile(r"\s+([,.।॥?!])")

HIERARCHY_COLUMNS = {"slno", "contentType", "parentSlno", "grandparentSlno"}


def parse_arguments():
    parser = argparse.ArgumentParser(description="Clean the BenCoDiC corpus.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("corpus_before_cleaning.xlsx"),
        help="Input Excel file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("corpus_cleaned.xlsx"),
        help="Cleaned Excel file.",
    )
    parser.add_argument(
        "--removed-output",
        type=Path,
        default=Path("removed_samples.xlsx"),
        help="Audit file containing removed samples and reasons.",
    )
    return parser.parse_args()


def clean_text(value):
    """Apply the text-normalization operations used during corpus cleaning."""
    if pd.isna(value):
        return ""

    text = str(value).replace("\u200c", "")
    text = DELIMITER_SPACE_RE.sub(" ", text)
    text = SPACE_BEFORE_DELIMITER_RE.sub(r"\1", text)
    text = HTML_TAG_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def contains_unsupported_script(text):
    """Return True if the text contains a non-Bengali/non-Latin letter."""
    for char in text:
        if unicodedata.category(char).startswith("L"):
            name = unicodedata.name(char, "")
            if "BENGALI" not in name and "LATIN" not in name:
                return True
    return False


def direct_removal_reason(text):
    """Return the direct reason for removing a sample, if any."""
    if not text:
        return "empty_after_cleaning"

    if NUMERIC_ONLY_RE.fullmatch(text):
        return "numeric_only"

    if contains_unsupported_script(text):
        return "unsupported_script"

    return None


def normalize_id(value):
    """Normalize hierarchy identifiers loaded from Excel."""
    if pd.isna(value):
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def require_hierarchy_columns(df):
    missing = HIERARCHY_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(
            "Missing hierarchy column(s): " + ", ".join(sorted(missing))
        )


def apply_hierarchical_deletion(df, reasons):
    """
    Remove descendants when a parent is removed.

    A removed caption removes all associated comments/replies.
    A removed comment removes all of its replies.
    """
    require_hierarchy_columns(df)

    reasons = reasons.copy()
    slno = df["slno"].map(normalize_id)
    parent = df["parentSlno"].map(normalize_id)
    grandparent = df["grandparentSlno"].map(normalize_id)
    content_type = df["contentType"].astype("string").str.strip().str.lower()

    removed_caption_ids = set(
        slno[reasons.notna() & content_type.eq("caption")].dropna()
    )
    removed_comment_ids = set(
        slno[reasons.notna() & content_type.eq("comment")].dropna()
    )

    if removed_caption_ids:
        mask = reasons.isna() & grandparent.isin(removed_caption_ids)
        reasons.loc[mask] = "caption_removed"
        removed_comment_ids.update(
            slno[mask & content_type.eq("comment")].dropna()
        )

    if removed_comment_ids:
        mask = (
            reasons.isna()
            & content_type.eq("reply")
            & parent.isin(removed_comment_ids)
        )
        reasons.loc[mask] = "parent_comment_removed"

    return reasons


def validate_hierarchy(df):
    """Verify that the retained rows contain no broken hierarchy references."""
    require_hierarchy_columns(df)

    slno = df["slno"].map(normalize_id)
    parent = df["parentSlno"].map(normalize_id)
    grandparent = df["grandparentSlno"].map(normalize_id)
    content_type = df["contentType"].astype("string").str.strip().str.lower()

    type_by_slno = dict(zip(slno, content_type))
    valid_ids = set(slno.dropna())
    errors = []

    for idx in df.index:
        row_id = slno.loc[idx]
        row_type = content_type.loc[idx]
        row_parent = parent.loc[idx]
        row_grandparent = grandparent.loc[idx]

        if row_type == "caption":
            if row_parent != row_id or row_grandparent != row_id:
                errors.append(f"Caption {row_id}: invalid hierarchy.")

        elif row_type == "comment":
            if (
                row_parent not in valid_ids
                or type_by_slno.get(row_parent) != "caption"
                or row_grandparent != row_parent
            ):
                errors.append(f"Comment {row_id}: invalid caption reference.")

        elif row_type == "reply":
            if (
                row_parent not in valid_ids
                or type_by_slno.get(row_parent) != "comment"
                or row_grandparent not in valid_ids
                or type_by_slno.get(row_grandparent) != "caption"
            ):
                errors.append(f"Reply {row_id}: invalid hierarchy reference.")

        else:
            errors.append(f"{row_id}: invalid contentType '{row_type}'.")

        if len(errors) >= 20:
            break

    if errors:
        raise ValueError(
            "Hierarchy validation failed:\n  - " + "\n  - ".join(errors)
        )


def clean_corpus(input_file, output_file, removed_output):
    df = pd.read_excel(input_file)

    if "text" not in df.columns:
        raise ValueError("The input file must contain a 'text' column.")

    require_hierarchy_columns(df)

    cleaned_text = df["text"].map(clean_text)
    reasons = cleaned_text.map(direct_removal_reason)
    reasons = apply_hierarchical_deletion(df, reasons)

    keep_mask = reasons.isna()

    cleaned_df = df.loc[keep_mask].copy()
    cleaned_df["text"] = cleaned_text.loc[keep_mask]
    cleaned_df.reset_index(drop=True, inplace=True)

    removed_df = df.loc[~keep_mask].copy()
    removed_df.insert(
        removed_df.columns.get_loc("text") + 1,
        "cleanedText",
        cleaned_text.loc[~keep_mask],
    )
    removed_df.insert(
        removed_df.columns.get_loc("cleanedText") + 1,
        "removalReason",
        reasons.loc[~keep_mask],
    )
    removed_df.reset_index(drop=True, inplace=True)

    validate_hierarchy(cleaned_df)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    removed_output.parent.mkdir(parents=True, exist_ok=True)

    cleaned_df.to_excel(output_file, index=False)
    removed_df.to_excel(removed_output, index=False)

    print(f"Input rows:   {len(df):,}")
    print(f"Removed rows: {len(removed_df):,}")
    print(f"Output rows:  {len(cleaned_df):,}")

    if not removed_df.empty:
        print("\nRemoval summary:")
        print(removed_df["removalReason"].value_counts().to_string())

    print(f"\nCleaned corpus saved to: {output_file}")
    print(f"Removed-sample audit saved to: {removed_output}")


def main():
    args = parse_arguments()
    clean_corpus(args.input, args.output, args.removed_output)


if __name__ == "__main__":
    main()
