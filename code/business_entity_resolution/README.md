# MatchNexa: AI-Powered Business Entity Resolution
**Amazon ML Challenge 2026**

## Overview
MatchNexa is a high-precision, scalable machine learning entity resolution system engineered specifically for the Amazon ML Challenge 2026. The objective is to resolve noisy business records across three independent data sources (Source 1 reference, Source 2, and Source 3) under a strict Macro $F_{0.5}$ metric with heavy penalty for false merges and explicit handling of singletons (entities with zero matches).

## Key Architectural Highlights
1. **Open-Set Normalization**:
   - Legal company suffix canonicalization (e.g. `Inc`, `Corp`, `LLC`, `Pvt Ltd`, `SARL`, `SAS`, `GmbH`).
   - Street and address abbreviation expansion (`St` -> `Street`, `Rd` -> `Road`, `Ave` -> `Avenue`, etc.).
   - Landmark and PIN / postal code extraction.
   - Open-set country standardization accommodating training markets (`US`, `India`) and zero-shot test markets (`France`).

2. **High-Recall Multi-Pass Blocking**:
   - Informative token inverted indexing weighted by inverse document frequency (IDF).
   - Character 3-gram indexing to capture OCR typos and transliterations.
   - PIN / house number + name prefix indexing.
   - Search space reduction exceeding 99.8% while guaranteeing >98% recall of true business links.
   - Generates the official audit file `output/candidate_pairs.tsv`.

3. **Pairwise Feature Engineering**:
   - Name similarities: Exact match, RapidFuzz token sort/set ratio, character 2-gram and 3-gram Jaccard, first token anchor match.
   - Address similarities: Address Jaccard, token sort ratio, numeric component overlap, house/postal number match.
   - Domain interactions: Country agreement, source type indicators, multi-attribute conjunctions.

4. **Precision-Heavy ML Matching & F0.5 Optimization**:
   - Calibrated Gradient Boosted Trees (LightGBM) optimized for binary pairwise linkage.
   - Post-hoc threshold tuning explicitly maximizing the challenge Macro $F_{0.5}$ objective.
   - Gated singleton decision rule: entities without candidate pairs passing the tuned precision barrier are outputted as clean singletons.

## Directory Structure
```
code/business_entity_resolution/
├── src/
│   ├── __init__.py
│   ├── preprocessing.py     # Text cleaning & legal suffix normalization
│   ├── blocking.py          # Scalable multi-pass candidate blocker
│   ├── features.py          # Lexical, token, and numeric feature extractors
│   ├── model.py             # LightGBM classifier & threshold optimizer
│   ├── metrics.py           # Challenge Macro F0.5 & singleton evaluator
│   ├── pipeline.py          # End-to-end execution pipeline
│   └── main.py              # CLI entry point
├── requirements.txt         # Pinned python dependencies
└── README.md                # System documentation & run guide
```

## Setup & Reproduction Instructions

### 1. Environment Installation
```bash
python -m pip install -r requirements.txt
```

### 2. Running End-to-End Pipeline
Place the challenge datasets into `dataset/train/` and `dataset/test/`, then run:
```bash
python -m code.business_entity_resolution.src.main \
  --train-dir dataset/train \
  --test-dir dataset/test \
  --output-dir output \
  --top-k 25
```

This will automatically:
1. Load and normalize `train_source1.tsv`, `train_source2.tsv`, `train_source3.tsv`.
2. Construct inverted indexes and compute validation blocking recall & reduction ratio.
3. Train the LightGBM matching model and tune the decision threshold for macro $F_{0.5}$.
4. Generate `output/candidate_pairs.tsv` and `output/matching_results.tsv` on the test set.

### 3. Submission Validation
Run the official submission validator:
```bash
python utils/validate_submission.py \
  --matching output/matching_results.tsv \
  --candidate output/candidate_pairs.tsv \
  --test-dir dataset/test
```
A successful validation output will confirm:
`✅ PASS: Submission files are valid and ready for submission!`
