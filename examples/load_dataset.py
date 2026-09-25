#!/usr/bin/env python3
"""
Load the BenCoDiC corpus and display a brief dataset summary.

Requirements:
    pandas
"""

from pathlib import Path

import pandas as pd


DATASET_PATH = (
    Path(__file__).resolve().parents[1] / "bencodic-corpus-v1.csv"
)


def main():
    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset: {DATASET_PATH.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nContent types:")
    print(df["contentType"].value_counts().to_string())

    print("\nBinary labels:")
    print(df["bullyLabel"].value_counts().to_string())

    print("\nSample records:")
    print(
        df[["slno", "contentType", "text", "bullyLabel"]]
        .head()
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
