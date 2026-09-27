"""
Pairwise Feature Engineering Module for Business Entity Resolution.
Extracts rich lexical, token, character n-gram, address component, numeric,
and source-specific indicators for each (Source 1, Candidate) pair.
"""

import numpy as np
import pandas as pd
from rapidfuzz import fuzz

def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Computes Jaccard index between two sets."""
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)

def char_ngram_jaccard(str_a: str, str_b: str, n: int = 3) -> float:
    """Computes Jaccard similarity over character n-grams."""
    if not str_a and not str_b:
        return 1.0
    if not str_a or not str_b:
        return 0.0
    ng_a = {str_a[i:i+n] for i in range(len(str_a) - n + 1)} if len(str_a) >= n else {str_a}
    ng_b = {str_b[i:i+n] for i in range(len(str_b) - n + 1)} if len(str_b) >= n else {str_b}
    return jaccard_similarity(ng_a, ng_b)

def extract_pair_features(s1_rec: pd.Series, tgt_rec: pd.Series) -> dict:
    """Extracts high-dimensional similarity features between an S1 and Target record."""
    s1_name = s1_rec["business_name_clean"]
    tgt_name = tgt_rec["business_name_clean"]
    s1_addr = s1_rec["business_address_clean"]
    tgt_addr = tgt_rec["business_address_clean"]
    s1_tokens = s1_rec["name_tokens"]
    tgt_tokens = tgt_rec["name_tokens"]
    s1_addr_tokens = s1_rec["address_tokens"]
    tgt_addr_tokens = tgt_rec["address_tokens"]
    s1_nums = s1_rec["address_numbers"]
    tgt_nums = tgt_rec["address_numbers"]
    
    # 1. Business Name Features
    name_exact = 1.0 if s1_name and s1_name == tgt_name else 0.0
    name_fuzz_ratio = fuzz.ratio(s1_name, tgt_name) / 100.0
    name_partial_ratio = fuzz.partial_ratio(s1_name, tgt_name) / 100.0
    name_token_sort = fuzz.token_sort_ratio(s1_name, tgt_name) / 100.0
    name_token_set = fuzz.token_set_ratio(s1_name, tgt_name) / 100.0
    name_token_jaccard = jaccard_similarity(s1_tokens, tgt_tokens)
    name_3gram_jaccard = char_ngram_jaccard(s1_name, tgt_name, n=3)
    name_2gram_jaccard = char_ngram_jaccard(s1_name, tgt_name, n=2)
    
    # First token matching (brand anchor)
    s1_first = s1_name.split()[0] if s1_name else ""
    tgt_first = tgt_name.split()[0] if tgt_name else ""
    first_token_match = 1.0 if s1_first and s1_first == tgt_first else 0.0
    first_token_sim = (fuzz.ratio(s1_first, tgt_first) / 100.0) if (s1_first and tgt_first) else 0.0
    
    # Name length difference
    len_s1 = len(s1_name)
    len_tgt = len(tgt_name)
    name_len_diff = abs(len_s1 - len_tgt) / max(len_s1, len_tgt, 1)
    
    # 2. Address Features
    addr_exact = 1.0 if s1_addr and s1_addr == tgt_addr else 0.0
    addr_fuzz_ratio = fuzz.ratio(s1_addr, tgt_addr) / 100.0
    addr_partial_ratio = fuzz.partial_ratio(s1_addr, tgt_addr) / 100.0
    addr_token_sort = fuzz.token_sort_ratio(s1_addr, tgt_addr) / 100.0
    addr_token_set = fuzz.token_set_ratio(s1_addr, tgt_addr) / 100.0
    addr_token_jaccard = jaccard_similarity(s1_addr_tokens, tgt_addr_tokens)
    addr_3gram_jaccard = char_ngram_jaccard(s1_addr, tgt_addr, n=3)
    
    # Numeric / PIN / Suite components
    nums_shared = len(s1_nums & tgt_nums)
    nums_jaccard = jaccard_similarity(s1_nums, tgt_nums)
    has_exact_num_match = 1.0 if nums_shared > 0 else 0.0
    has_num_mismatch = 1.0 if (s1_nums and tgt_nums and nums_shared == 0) else 0.0
    
    # 3. Country Agreement
    c1 = s1_rec["country_clean"]
    c2 = tgt_rec["country_clean"]
    country_match = 1.0 if c1 and c2 and c1 == c2 else 0.0
    country_missing = 1.0 if not c1 or not c2 else 0.0
    
    # 4. Target Source Indicators
    tgt_id = tgt_rec["entity_id"]
    is_source2 = 1.0 if tgt_id.startswith("S2-") else 0.0
    is_source3 = 1.0 if tgt_id.startswith("S3-") else 0.0
    
    # 5. Interaction Signals
    name_x_addr = name_token_set * addr_token_set
    high_confidence_name = 1.0 if name_token_set >= 0.90 else 0.0
    high_confidence_addr = 1.0 if addr_token_set >= 0.85 else 0.0
    both_high = 1.0 if (high_confidence_name and high_confidence_addr) else 0.0
    
    return {
        "name_exact": name_exact,
        "name_fuzz_ratio": name_fuzz_ratio,
        "name_partial_ratio": name_partial_ratio,
        "name_token_sort": name_token_sort,
        "name_token_set": name_token_set,
        "name_token_jaccard": name_token_jaccard,
        "name_3gram_jaccard": name_3gram_jaccard,
        "name_2gram_jaccard": name_2gram_jaccard,
        "first_token_match": first_token_match,
        "first_token_sim": first_token_sim,
        "name_len_diff": name_len_diff,
        "addr_exact": addr_exact,
        "addr_fuzz_ratio": addr_fuzz_ratio,
        "addr_partial_ratio": addr_partial_ratio,
        "addr_token_sort": addr_token_sort,
        "addr_token_set": addr_token_set,
        "addr_token_jaccard": addr_token_jaccard,
        "addr_3gram_jaccard": addr_3gram_jaccard,
        "nums_shared": float(nums_shared),
        "nums_jaccard": nums_jaccard,
        "has_exact_num_match": has_exact_num_match,
        "has_num_mismatch": has_num_mismatch,
        "country_match": country_match,
        "country_missing": country_missing,
        "is_source2": is_source2,
        "is_source3": is_source3,
        "name_x_addr": name_x_addr,
        "both_high": both_high,
    }
