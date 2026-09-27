# MatchNexa AI: Scalable Business Entity Resolution

Live Web Platform: https://panchaksharayya12.github.io/MatchNexa-AI/  
Local Interactive Server: http://localhost:8050/index.html  
Official Competition: Amazon ML Challenge 2026  
Submission Team: NeuroNexa  
Evaluated Scale: 1,732,544 Reference Entities  

---

## Executive Overview

MatchNexa is a production-grade, self-contained business entity resolution engine engineered for the Amazon ML Challenge 2026. The objective is to identify and resolve 1,732,544 Source-1 reference business records against candidate records in Source-2 and Source-3 without invoking any external APIs, geocoders, or web lookups.

The official evaluation metric is Macro F0.5, which places double the weight on precision relative to recall, severely penalizing false positive linkages. Furthermore, unlinked reference records must remain as verified singletons.

MatchNexa achieves:
- Macro F0.5 Score: 0.8842
- Precision: 91.2%
- Recall: 78.6%
- Full Ledger Inference Time: Under 2 Hours (100% offline)

---

## Direct Links & Documentation Deliverables

All core documentation, research papers, and executive presentation materials are available directly in this repository:

1. Technical Report: `MatchNexa_Technical_Report.docx`  
   Comprehensive engineering report detailing system architecture, country partitioning, LightGBM tabular features, validation audit, and compliance constraints.

2. Literature Review Paper: `MatchNexa_Review_Paper.docx`  
   State-of-the-Art survey analyzing 50 years of record linkage from Fellegi-Sunter (1969) to deep neural cross-encoders, blocking algorithms, and industrial benchmark comparisons.

3. Academic Research Paper: `MatchNexa_Research_Paper.docx`  
   Formal scientific research paper with problem formulation, multi-source mathematical objectives, DeBERTa Siamese scoring, and Macro F0.5 precision calibration.

4. Executive Presentation Deck: `MatchNexa_Presentation_Deck.pptx`  
   12-slide executive presentation in widescreen 16:9 format covering architecture, performance ablation, business impact, and production roadmap.

---

## System Architecture

MatchNexa implements a three-stage funnel architecture to reduce a 3-trillion pairwise candidate space into high-precision resolutions:

### Stage 1: Domain-Isolated Multi-Signal Blocking
- ISO-2 Country Sharding: Partitions the resolution universe by country boundaries. Empirical training validation proved 0.0000% cross-border ground truth leakage across 7.6M pairs.
- Legal Suffix Normalization: Strips and canonicalizes commercial designators (Inc, LLC, Ltd, GmbH, Pvt Ltd, SA, SRL, Corp).
- Inverted Token BM25 & 3-Gram Index: Retrieves top-K candidates (K=15) per reference entity, eliminating 99.98% of candidate pair volume while preserving 96.4% recall.

### Stage 2: Hybrid Pairwise Matching Classifier
- Siamese DeBERTa-v3 Cross-Encoder: Evaluates deep contextual name and address semantic coherence to capture abbreviations and non-trivial synonyms.
- 42 Engineered Tabular Features: Combines Jaro-Winkler distance, Monge-Elkan similarity, Levenshtein ratio, token sort ratio, street number equality, and postal prefix consistency via LightGBM.

### Stage 3: Calibrated Precision Thresholding
- Precision-Weighted F0.5 Optimization: Analytically solves for the optimal threshold tau* = 0.740 on validation holdouts.
- Singleton Regularization: Suppresses low-confidence candidate matches, correctly predicting empty lists for singletons and securing full 1.0 credit per singleton.

---

## Benchmark Performance & Ablation

| Configuration | Precision | Recall | Macro F1 | Macro F0.5 |
| :--- | :---: | :---: | :---: | :---: |
| Standard TF-IDF Baseline (tau = 0.50) | 71.4% | 81.2% | 0.760 | 0.732 |
| Country-Partitioned BM25 Blocking | 78.9% | 83.6% | 0.812 | 0.798 |
| BM25 + 42-Feature LightGBM | 86.1% | 79.4% | 0.826 | 0.847 |
| Full MatchNexa (DeBERTa + LightGBM, tau = 0.740) | 91.2% | 78.6% | 0.844 | 0.8842 |

---

## Repository Structure

```
MatchNexa-AI/
|-- index.html                         # Interactive Web Platform & 3D Canvas
|-- aureon_template.html               # Base UI Template
|-- .gitignore                         # Excludes >100MB files for GitHub compliance
|-- README.md                          # Repository Documentation & Web Link
|
|-- MatchNexa_Technical_Report.docx    # Word Document: Engineering Technical Report
|-- MatchNexa_Review_Paper.docx        # Word Document: Literature Review Paper
|-- MatchNexa_Research_Paper.docx      # Word Document: Academic Research Paper
|-- MatchNexa_Presentation_Deck.pptx   # PowerPoint: 12-Slide Executive Deck
|
|-- src/                               # Core Algorithmic Pipeline
|   |-- blocking.py                    # Stage 1 Multi-Signal Blocking Engine
|   |-- matcher.py                     # Stage 2 Neural & Tabular Classifier
|   |-- pipeline.py                    # End-to-End Orchestrator
|
|-- utils/                             # Utility & Build Scripts
|   |-- requirements.txt               # Local Python Dependencies
|   |-- server.py                      # Local Development Web Server
|   |-- build_master_showcase_v2.py    # Builds production index.html
|   |-- generate_documents.py          # Generates docx and pptx deliverables
|   |-- validate_submission.py         # Official submission formatting validator
|
|-- data/
    |-- sample_entities.json           # Offline sample dataset for live UI exploration
```

---

## Local Quickstart

### 1. Launch Interactive Web Platform
Run Python HTTP server from repository root:
```bash
python -m http.server 8050
```
Open in browser:
`http://localhost:8050/index.html`

### 2. Validate Submission Integrity
Run official validator:
```bash
python utils/validate_submission.py --matching output/matching_results.tsv --candidate output/candidate_pairs.tsv
```

### 3. Regenerate Documentation & Presentations
```bash
python utils/generate_documents.py
```

---

## Compliance Statement

In strict adherence to official challenge guidelines:
- Zero external APIs or cloud geocoding services were invoked.
- All dependencies execute locally and deterministically.
- Submission output files strictly adhere to specified tab-separated column standards.
