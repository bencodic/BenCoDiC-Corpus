#!/usr/bin/env python3
"""
Merge BenCoDiC text/metadata and channel-information files.

This script combines the output of:
    - extract_text_and_metadata.gs
    - extract_channel_info.gs

The two files are joined using the `handler` field. The merged columns are
then arranged according to the intermediate BenCoDiC schema used before
auxiliary labeling and annotation.

Requirements:
    pandas
    openpyxl

Example:
    python merge_extracted_data.py \
        --text text_and_metadata.xlsx \
        --channel channel_info.xlsx \
        --output merged_data.xlsx
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


CHANNEL_COLUMNS = [
    "userId",
    "title",
    "subscriberCount",
    "videoCount",
    "userViewCount",
    "joinedDate",
]

OUTPUT_COLUMNS = [
    "slno",
    "userId",
    "handler",
    "title",
    "subscriberCount",
    "videoCount",
    "userViewCount",
    "joinedDate",
    "contentId",
    "contentType",
    "partyName",
    "partyShortName",
    "duration",
    "viewCount",
    "commentCount",
    "text",
    "publishedTime",
    "likeCount",
    "replyCount",
    "parentSlno",
    "grandparentSlno",
]


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Merge text/metadata and channel-information files using "
            "the YouTube channel handler."
        )
    )
    parser.add_argument(
        "--text",
        type=Path,
        default=Path("text_and_metadata.xlsx"),
        help="Path to the Stage-1 text and metadata Excel file.",
    )
    parser.add_argument(
        "--channel",
        type=Path,
        default=Path("channel_info.xlsx"),
        help="Path to the Stage-2 channel-information Excel file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("merged_data.xlsx"),
        help="Path for the merged Excel file.",
    )
    return parser.parse_args()


def check_required_columns(
    dataframe: pd.DataFrame,
    required_columns: list[str],
    file_label: str,
) -> None:
    """Raise an error if an input file is missing required columns."""
    missing = [column for column in required_columns if column not in dataframe.columns]
    if missing:
        raise ValueError(
            f"{file_label} is missing required column(s): {', '.join(missing)}"
        )


def normalize_handler(series: pd.Series) -> pd.Series:
    """Normalize channel handles before merging."""
    return series.astype("string").str.strip().str.lower()


def normalize_joined_date(series: pd.Series) -> pd.Series:
    """Convert channel joining dates to YYYY-MM-DD format."""
    parsed = pd.to_datetime(series, errors="coerce", utc=True)

    invalid_count = int((series.notna() & parsed.isna()).sum())
    if invalid_count:
        print(
            f"Warning: {invalid_count} joinedDate value(s) could not be parsed "
            "and will remain missing."
        )

    return parsed.dt.strftime("%Y-%m-%d")


def merge_extracted_data(
    text_file: Path,
    channel_file: Path,
    output_file: Path,
) -> None:
    """Merge the two extraction-stage files and save the integrated result."""
    text_df = pd.read_excel(text_file)
    channel_df = pd.read_excel(channel_file)

    check_required_columns(
        text_df,
        [
            "slno",
            "handler",
            "contentId",
            "contentType",
            "partyName",
            "partyShortName",
            "duration",
            "viewCount",
            "commentCount",
            "text",
            "publishedTime",
            "likeCount",
            "replyCount",
            "parentSlno",
            "grandparentSlno",
        ],
        "Text/metadata file",
    )

    check_required_columns(
        channel_df,
        ["handler", *CHANNEL_COLUMNS],
        "Channel-information file",
    )

    # Normalize the common merge key.
    text_df["handler"] = normalize_handler(text_df["handler"])
    channel_df["handler"] = normalize_handler(channel_df["handler"])

    # Standardize channel joining dates.
    channel_df["joinedDate"] = normalize_joined_date(channel_df["joinedDate"])

    # Exclude rows without a usable handler from the lookup table.
    channel_lookup = channel_df.dropna(subset=["handler"]).copy()

    # One channel record is required per handler for a many-to-one merge.
    duplicate_mask = channel_lookup.duplicated(subset="handler", keep=False)
    if duplicate_mask.any():
        duplicate_count = int(
            channel_lookup.loc[duplicate_mask, "handler"].nunique()
        )
        print(
            f"Warning: {duplicate_count} duplicate handler(s) found in the "
            "channel-information file. The first occurrence of each handler "
            "will be used."
        )
        channel_lookup = channel_lookup.drop_duplicates(
            subset="handler",
            keep="first",
        )

    # Keep an explicit row-order marker so the Stage-1 order is preserved.
    text_df["__original_order"] = range(len(text_df))

    merged_df = text_df.merge(
        channel_lookup[["handler", *CHANNEL_COLUMNS]],
        on="handler",
        how="left",
        sort=False,
        validate="many_to_one",
    )

    merged_df = (
        merged_df.sort_values("__original_order")
        .drop(columns="__original_order")
        .reset_index(drop=True)
    )

    # Validate that the merge did not add or remove textual records.
    if len(merged_df) != len(text_df):
        raise RuntimeError(
            "Row count changed during the merge. "
            f"Before: {len(text_df)}, after: {len(merged_df)}."
        )

    if merged_df["slno"].duplicated().any():
        raise ValueError("Duplicate slno values were found after merging.")

    check_required_columns(
        merged_df,
        OUTPUT_COLUMNS,
        "Merged data",
    )

    merged_df = merged_df[OUTPUT_COLUMNS]

    output_file.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_excel(output_file, index=False)

    matched_rows = int(merged_df["userId"].notna().sum())
    print(f"Text/metadata rows: {len(text_df):,}")
    print(f"Rows with matched channel information: {matched_rows:,}")
    print(f"Merged file saved to: {output_file}")


def main() -> None:
    """Run the merge workflow."""
    args = parse_arguments()
    merge_extracted_data(args.text, args.channel, args.output)


if __name__ == "__main__":
    main()
