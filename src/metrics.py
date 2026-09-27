"""
Evaluation Metrics Module for Amazon ML Challenge 2026.
Implements the exact challenge Macro F0.5 metric:
- Macro-averaged across all Source 1 entities
- Precision-weighted: F_0.5 = (1.25 * P * R) / (0.25 * P + R)
- Strict singleton handling:
  - If true matches is empty (singleton) and predicted is empty: score = 1.0
  - If true matches is empty (singleton) and predicted is non-empty: score = 0.0
  - If true matches is non-empty and predicted is empty: score = 0.0
  - Otherwise compute P, R, and F0.5.
"""

from typing import Dict, List, Set

def compute_entity_f05(true_matches: Set[str], pred_matches: Set[str]) -> float:
    """Computes F0.5 for a single Source 1 entity."""
    # Singleton case
    if len(true_matches) == 0:
        return 1.0 if len(pred_matches) == 0 else 0.0
        
    if len(pred_matches) == 0:
        return 0.0
        
    true_positives = len(true_matches & pred_matches)
    if true_positives == 0:
        return 0.0
        
    precision = true_positives / len(pred_matches)
    recall = true_positives / len(true_matches)
    
    denominator = 0.25 * precision + recall
    if denominator == 0:
        return 0.0
        
    f05 = (1.25 * precision * recall) / denominator
    return f05

def compute_macro_f05(
    ground_truth: Dict[str, Set[str]],
    predictions: Dict[str, Set[str]]
) -> Dict[str, float]:
    """Computes Macro F0.5, Singleton Accuracy, Precision, and Recall across all S1 entities."""
    s1_ids = list(ground_truth.keys())
    if not s1_ids:
        return {"macro_f05": 0.0, "singleton_acc": 0.0, "mean_precision": 0.0, "mean_recall": 0.0}
        
    scores = []
    singleton_correct = 0
    total_singletons = 0
    precisions = []
    recalls = []
    
    for s1_id in s1_ids:
        true_set = ground_truth.get(s1_id, set())
        pred_set = predictions.get(s1_id, set())
        
        score = compute_entity_f05(true_set, pred_set)
        scores.append(score)
        
        if len(true_set) == 0:
            total_singletons += 1
            if len(pred_set) == 0:
                singleton_correct += 1
        else:
            tp = len(true_set & pred_set)
            p = tp / len(pred_set) if len(pred_set) > 0 else 0.0
            r = tp / len(true_set)
            precisions.append(p)
            recalls.append(r)
            
    return {
        "macro_f05": float(sum(scores) / len(scores)),
        "singleton_acc": float(singleton_correct / max(total_singletons, 1)),
        "total_singletons": total_singletons,
        "mean_precision": float(sum(precisions) / max(len(precisions), 1)),
        "mean_recall": float(sum(recalls) / max(len(recalls), 1)),
        "total_entities": len(s1_ids)
    }
