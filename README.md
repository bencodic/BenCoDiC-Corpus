# BenCoDiC: A Large-Scale Contextual Cyberbullying Corpus for Bengali Political News Discourse

BenCoDiC is a 50,250-instance Bengali cyberbullying corpus constructed from political YouTube news discourse. It contains captions, comments, and replies with preserved conversational hierarchy, metadata, and binary `bully`/`not bully` labels.

## Dataset

The final corpus is provided as:

```text
bencodic-corpus-v1.csv
```

It contains 24 fields described in `DATA_SCHEMA.md`.

```text
Content type     Instances
caption                100
comment             44,368
reply                5,782
Total               50,250

Label            Instances
bully              30,083
not bully          20,167
```

## Repository Contents

```text
BenCoDiC/
├── README.md
├── bencodic-corpus-v1.csv
├── video_list.csv
├── benchmark_splits.csv
├── DATA_SCHEMA.md
├── DATA_EXTRACTION.md
├── ANNOTATION_GUIDELINES.md
├── code/
│   ├── extract_text_and_metadata.gs
│   ├── extract_channel_info.gs
│   ├── merge_extracted_data.py
│   └── clean_data.py
└── examples/
    └── load_dataset.py
```

- `DATA_SCHEMA.md`: corpus fields, hierarchy, categorical values, and anonymization
- `DATA_EXTRACTION.md`: source-video selection, extraction, integration, and auxiliary labeling
- `ANNOTATION_GUIDELINES.md`: binary cyberbullying annotation criteria
- `video_list.csv`: exact source-video list
- `benchmark_splits.csv`: video-disjoint benchmark split assignments
- `code/`: extraction, integration, and cleaning scripts
- `examples/load_dataset.py`: basic dataset-loading example

## Quick Start

```bash
pip install pandas
python examples/load_dataset.py
```

The script loads `bencodic-corpus-v1.csv` and displays basic corpus statistics and sample records.
