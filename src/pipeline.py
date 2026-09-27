"""
End-to-End Scalable Machine Learning Entity Resolution Pipeline.
Orchestrates:
Data Loading -> Preprocessing -> Multi-Pass Blocking -> Pairwise Feature Engineering
-> LightGBM Training -> F0.5 Optimization -> Test Inference -> TSV Output Generation.
"""

import os
import csv
import random
import numpy as np
import pandas as pd
from typing import Dict, List, Set, Tuple

try:
    from .preprocessing import preprocess_dataframe
    from .blocking import ScalableBlocker
    from .features import extract_pair_features
    from .model import EntityMatchingModel
    from .metrics import compute_macro_f05
except ImportError:
    from preprocessing import preprocess_dataframe
    from blocking import ScalableBlocker
    from features import extract_pair_features
    from model import EntityMatchingModel
    from metrics import compute_macro_f05

def load_source_tsv(path: str) -> pd.DataFrame:
    """Reads source TSV safely with tab delimiter."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)

def load_ground_truth(path: str) -> Dict[str, Set[str]]:
    """Loads ground truth mapping source1_entity_id -> set of matched_entity_ids."""
    gt = {}
    if not os.path.exists(path):
        raise FileNotFoundError(f"Ground truth file not found: {path}")
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    for _, row in df.iterrows():
        s1_id = row["source1_entity_id"].strip()
        matched_str = row["matched_entity_ids"].strip() if "matched_entity_ids" in row else ""
        if matched_str:
            matched_ids = {m.strip() for m in matched_str.split(",") if m.strip()}
        else:
            matched_ids = set()
        gt[s1_id] = matched_ids
    return gt

class EntityResolutionPipeline:
    def __init__(self, top_k_candidates: int = 25):
        self.top_k = top_k_candidates
        self.blocker = ScalableBlocker(top_k_candidates=top_k_candidates)
        self.model = EntityMatchingModel(use_lightgbm=True)
        self.feature_names = None

    def train_and_validate(self, train_dir: str, val_ratio: float = 0.2, seed: int = 42):
        """Runs complete training, validation, blocking recall analysis, and threshold tuning."""
        print("=" * 60)
        print("STAGE 1: Loading & Preprocessing Training Data")
        print("=" * 60)
        s1_path = os.path.join(train_dir, "train_source1.tsv")
        s2_path = os.path.join(train_dir, "train_source2.tsv")
        s3_path = os.path.join(train_dir, "train_source3.tsv")
        gt_path = os.path.join(train_dir, "train_ground_truth.tsv")

        s1_df = preprocess_dataframe(load_source_tsv(s1_path))
        s2_df = preprocess_dataframe(load_source_tsv(s2_path))
        s3_df = preprocess_dataframe(load_source_tsv(s3_path))
        ground_truth = load_ground_truth(gt_path)

        total_s1 = len(s1_df)
        total_targets = len(s2_df) + len(s3_df)
        print(f"Loaded records: S1={total_s1}, S2={len(s2_df)}, S3={len(s3_df)} (Total Targets: {total_targets})")

        # Split S1 entities into Train and Validation
        random.seed(seed)
        all_s1_ids = list(s1_df["entity_id"].unique())
        random.shuffle(all_s1_ids)
        val_size = int(len(all_s1_ids) * val_ratio)
        val_ids = set(all_s1_ids[:val_size])
        train_ids = set(all_s1_ids[val_size:])

        train_s1_df = s1_df[s1_df["entity_id"].isin(train_ids)].copy()
        val_s1_df = s1_df[s1_df["entity_id"].isin(val_ids)].copy()
        val_gt = {k: ground_truth.get(k, set()) for k in val_ids}

        print(f"Train/Val split: {len(train_ids)} train S1 entities, {len(val_ids)} val S1 entities")

        print("\n" + "=" * 60)
        print("STAGE 2: Multi-Pass Inverted Index Blocking & Candidate Generation")
        print("=" * 60)
        self.blocker.fit_targets(s2_df, s3_df)

        # Generate candidates for training set
        train_candidates = self.blocker.generate_all_candidate_pairs(train_s1_df)
        val_candidates = self.blocker.generate_all_candidate_pairs(val_s1_df)

        # Measure Blocking Recall and Reduction Ratio on Validation Set
        total_true_links = sum(len(val_gt[sid]) for sid in val_ids)
        recalled_true_links = 0
        total_pairs_generated = 0

        for sid in val_ids:
            true_set = val_gt[sid]
            cand_set = set(val_candidates.get(sid, []))
            recalled_true_links += len(true_set & cand_set)
            total_pairs_generated += len(cand_set)

        blocking_recall = recalled_true_links / max(total_true_links, 1)
        total_possible_comparisons = len(val_ids) * total_targets
        reduction_ratio = 1.0 - (total_pairs_generated / max(total_possible_comparisons, 1))
        avg_candidates = total_pairs_generated / max(len(val_ids), 1)

        print(f"Validation Blocking Metrics:")
        print(f"  • True Links in Val: {total_true_links}")
        print(f"  • Recalled by Blocker: {recalled_true_links}")
        print(f"  • Blocking Recall Ceiling: {blocking_recall * 100:.2f}%")
        print(f"  • Average Candidates per S1: {avg_candidates:.2f}")
        print(f"  • Search Space Reduction Ratio: {reduction_ratio * 100:.4f}%")

        print("\n" + "=" * 60)
        print("STAGE 3: Pairwise Feature Engineering")
        print("=" * 60)
        # Build training feature matrix
        X_train_list, y_train_list = [], []
        target_map = {**{r["entity_id"]: r for _, r in s2_df.iterrows()},
                      **{r["entity_id"]: r for _, r in s3_df.iterrows()}}

        for _, s1_row in train_s1_df.iterrows():
            sid = s1_row["entity_id"]
            true_matches = ground_truth.get(sid, set())
            cands = set(train_candidates.get(sid, []))
            
            # Add true matches to training if missing (for complete positive coverage)
            for true_id in true_matches:
                if true_id in target_map:
                    cands.add(true_id)

            for cid in cands:
                tgt_row = target_map[cid]
                feat_dict = extract_pair_features(s1_row, tgt_row)
                label = 1 if cid in true_matches else 0
                X_train_list.append(list(feat_dict.values()))
                y_train_list.append(label)
                if self.feature_names is None:
                    self.feature_names = list(feat_dict.keys())

        X_train = np.array(X_train_list)
        y_train = np.array(y_train_list)
        print(f"Extracted {len(X_train)} training pairs ({np.sum(y_train)} positive, {len(y_train) - np.sum(y_train)} negative)")

        # Build validation feature pairs
        val_pair_records = []
        for _, s1_row in val_s1_df.iterrows():
            sid = s1_row["entity_id"]
            cands = val_candidates.get(sid, [])
            for cid in cands:
                tgt_row = target_map[cid]
                feat_dict = extract_pair_features(s1_row, tgt_row)
                val_pair_records.append((sid, cid, np.array(list(feat_dict.values()))))

        print("\n" + "=" * 60)
        print("STAGE 4: Model Training & Macro F0.5 Threshold Tuning")
        print("=" * 60)
        self.model.fit(X_train, y_train, feature_names=self.feature_names)
        self.model.optimize_threshold(val_pair_records, val_gt)

        # Evaluate final validation metrics with optimal threshold
        val_preds = self.model.predict_matches(val_pair_records, list(val_ids))
        val_metrics = compute_macro_f05(val_gt, val_preds)

        print("\n" + "=" * 60)
        print("STAGE 5: Final Validation Evaluation")
        print("=" * 60)
        print(f"  • Macro F0.5: {val_metrics['macro_f05']:.4f}")
        print(f"  • Singleton Accuracy: {val_metrics['singleton_acc'] * 100:.2f}% ({val_metrics['total_singletons']} singletons)")
        print(f"  • Mean Precision: {val_metrics['mean_precision']:.4f}")
        print(f"  • Mean Recall: {val_metrics['mean_recall']:.4f}")
        print("=" * 60)

        return val_metrics

    def predict_test(self, test_dir: str, output_dir: str):
        """Generates candidate_pairs.tsv and matching_results.tsv for test records."""
        print("\n" + "=" * 60)
        print("STAGE 6: Test Inference & Submission Generation")
        print("=" * 60)
        s1_path = os.path.join(test_dir, "test_source1.tsv")
        s2_path = os.path.join(test_dir, "test_source2.tsv")
        s3_path = os.path.join(test_dir, "test_source3.tsv")

        s1_df = preprocess_dataframe(load_source_tsv(s1_path))
        s2_df = preprocess_dataframe(load_source_tsv(s2_path))
        s3_df = preprocess_dataframe(load_source_tsv(s3_path))

        print(f"Loaded test records: S1={len(s1_df)}, S2={len(s2_df)}, S3={len(s3_df)}")

        # Fit blocker on test targets
        test_blocker = ScalableBlocker(top_k_candidates=self.top_k)
        test_blocker.fit_targets(s2_df, s3_df)
        test_candidates = test_blocker.generate_all_candidate_pairs(s1_df)

        target_map = {**{r["entity_id"]: r for _, r in s2_df.iterrows()},
                      **{r["entity_id"]: r for _, r in s3_df.iterrows()}}

        # Extract test pair features
        test_pairs = []
        for _, s1_row in s1_df.iterrows():
            sid = s1_row["entity_id"]
            cands = test_candidates.get(sid, [])
            for cid in cands:
                tgt_row = target_map[cid]
                feat_dict = extract_pair_features(s1_row, tgt_row)
                test_pairs.append((sid, cid, np.array(list(feat_dict.values()))))

        all_s1_ids = list(s1_df["entity_id"])
        test_matches = self.model.predict_matches(test_pairs, all_s1_ids)

        os.makedirs(output_dir, exist_ok=True)
        cand_path = os.path.join(output_dir, "candidate_pairs.tsv")
        match_path = os.path.join(output_dir, "matching_results.tsv")

        # 1. Write candidate_pairs.tsv
        with open(cand_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t", lineterminator="\n")
            writer.writerow(["source1_entity_id", "candidate_entity_ids"])
            for sid in all_s1_ids:
                cand_list = test_candidates.get(sid, [])
                writer.writerow([sid, ",".join(cand_list)])

        # 2. Write matching_results.tsv (ensuring matches are strictly a subset of candidates)
        with open(match_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t", lineterminator="\n")
            writer.writerow(["source1_entity_id", "matched_entity_ids"])
            for sid in all_s1_ids:
                match_set = test_matches.get(sid, set())
                cand_set = set(test_candidates.get(sid, []))
                # Enforce subset integrity
                valid_matches = sorted(list(match_set & cand_set))
                writer.writerow([sid, ",".join(valid_matches)])

        print(f"Generated candidate pairs: {cand_path}")
        print(f"Generated matching results: {match_path}")
        print("Ready for official validator check.")
