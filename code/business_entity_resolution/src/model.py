"""
Machine Learning Matching Model and F0.5 Threshold Optimizer.
Trains a precision-tuned LightGBM / Gradient Boosting classifier on pairwise features
and optimizes decision threshold specifically for Macro F0.5.
"""

import numpy as np
import lightgbm as lgb
from sklearn.ensemble import HistGradientBoostingClassifier
from typing import Dict, List, Set, Tuple
try:
    from .metrics import compute_macro_f05
except ImportError:
    from metrics import compute_macro_f05

class EntityMatchingModel:
    def __init__(self, use_lightgbm: bool = True):
        self.use_lightgbm = use_lightgbm
        if use_lightgbm:
            self.model = lgb.LGBMClassifier(
                n_estimators=250,
                learning_rate=0.05,
                num_leaves=31,
                max_depth=6,
                min_child_samples=20,
                subsample=0.8,
                colsample_bytree=0.8,
                class_weight="balanced",
                random_state=42,
                verbosity=-1
            )
        else:
            self.model = HistGradientBoostingClassifier(
                max_iter=200,
                learning_rate=0.05,
                max_leaf_nodes=31,
                random_state=42
            )
        self.feature_names = []
        self.best_threshold = 0.65  # Default precision-heavy threshold

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str] = None):
        """Fit model on pair features and binary match labels."""
        self.feature_names = feature_names or [f"f_{i}" for i in range(X.shape[1])]
        self.model.fit(X, y)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Returns match probability (class 1)."""
        return self.model.predict_proba(X)[:, 1]

    def optimize_threshold(
        self,
        val_pairs: List[Tuple[str, str, np.ndarray]],  # list of (s1_id, tgt_id, feature_vector)
        val_ground_truth: Dict[str, Set[str]],
        thresholds: np.ndarray = np.linspace(0.40, 0.90, 51)
    ) -> float:
        """
        Sweeps decision threshold on validation set to directly maximize Macro F0.5.
        """
        if not val_pairs:
            return self.best_threshold

        X_val = np.array([feat for _, _, feat in val_pairs])
        probs = self.predict_proba(X_val)

        # Group probabilities by s1_id
        s1_to_scored_cands = {}
        for (s1_id, tgt_id, _), prob in zip(val_pairs, probs):
            if s1_id not in s1_to_scored_cands:
                s1_to_scored_cands[s1_id] = []
            s1_to_scored_cands[s1_id].append((tgt_id, prob))

        best_score = -1.0
        best_thresh = self.best_threshold

        all_val_s1 = list(val_ground_truth.keys())

        for thresh in thresholds:
            preds = {}
            for s1_id in all_val_s1:
                cands = s1_to_scored_cands.get(s1_id, [])
                # Filter candidates strictly above threshold
                matched = {tgt_id for tgt_id, prob in cands if prob >= thresh}
                preds[s1_id] = matched

            metrics = compute_macro_f05(val_ground_truth, preds)
            score = metrics["macro_f05"]
            if score > best_score:
                best_score = score
                best_thresh = float(thresh)

        print(f"Optimal F0.5 Threshold: {best_thresh:.4f} (Validation Macro F0.5 = {best_score:.4f})")
        self.best_threshold = best_thresh
        return best_thresh

    def predict_matches(
        self,
        pairs: List[Tuple[str, str, np.ndarray]],
        all_s1_ids: List[str],
        threshold: float = None
    ) -> Dict[str, Set[str]]:
        """Generates matched entity IDs for every S1 entity using optimal threshold."""
        thresh = threshold if threshold is not None else self.best_threshold
        predictions = {s1_id: set() for s1_id in all_s1_ids}

        if not pairs:
            return predictions

        X = np.array([feat for _, _, feat in pairs])
        probs = self.predict_proba(X)

        for (s1_id, tgt_id, _), prob in zip(pairs, probs):
            if prob >= thresh:
                predictions[s1_id].add(tgt_id)

        return predictions
