"""
High-Recall, Scalable Multi-Pass Blocking and Candidate Generation Module.
Combines:
1. Informative Name Token Inverted Index (filtered by IDF)
2. Character 3-Gram Inverted Index for typo & transliteration resilience
3. Address Numeric / PIN Code + Name Prefix Index
4. Country-consistency gating
5. Fast lexical candidate ranking and Top-K pruning to optimize candidate set size
"""

from collections import defaultdict
import math
from typing import Dict, List, Set, Tuple
import pandas as pd
from rapidfuzz import fuzz

STOP_TOKENS = {
    "the", "and", "or", "of", "in", "at", "by", "for", "with", "a", "an",
    "inc", "ltd", "pvtltd", "llc", "llp", "co", "corp", "sa", "sarl", "sas",
    "gmbh", "enterprise", "enterprises", "services", "solutions", "group", "holdings"
}

def generate_char_ngrams(text: str, n: int = 3) -> Set[str]:
    """Generates character n-grams from text."""
    if not text or len(text) < n:
        return {text} if text else set()
    return {text[i:i+n] for i in range(len(text) - n + 1)}

class ScalableBlocker:
    def __init__(self, top_k_candidates: int = 25, min_token_len: int = 3):
        self.top_k = top_k_candidates
        self.min_token_len = min_token_len
        self.name_token_index = defaultdict(set)
        self.ngram_index = defaultdict(set)
        self.country_num_index = defaultdict(set)
        self.target_records = {}
        self.idf_dict = {}

    def fit_targets(self, s2_df: pd.DataFrame, s3_df: pd.DataFrame):
        """Builds multi-pass inverted indexes over combined target records (S2 + S3)."""
        target_df = pd.concat([s2_df, s3_df], ignore_index=True)
        total_targets = len(target_df)
        
        # 1. Compute Document Frequencies for target name tokens
        df_counts = defaultdict(int)
        for _, row in target_df.iterrows():
            tokens = row["name_tokens"]
            for tok in tokens:
                if len(tok) >= self.min_token_len and tok not in STOP_TOKENS:
                    df_counts[tok] += 1
                    
        # Compute IDF
        self.idf_dict = {
            tok: math.log((total_targets + 1) / (cnt + 1)) + 1
            for tok, cnt in df_counts.items()
        }
        
        # 2. Build Inverted Indexes
        for _, row in target_df.iterrows():
            tid = row["entity_id"]
            self.target_records[tid] = row
            
            # Country
            country = row["country_clean"]
            
            # Pass A: Token index (filtered for informative tokens, max DF threshold)
            for tok in row["name_tokens"]:
                if len(tok) >= self.min_token_len and tok not in STOP_TOKENS:
                    # Ignore tokens that appear in more than 5% of all records (too uninformative)
                    if df_counts[tok] < max(50, total_targets * 0.05):
                        self.name_token_index[(country, tok)].add(tid)
                        # Also index without country for records with missing country
                        self.name_token_index[("", tok)].add(tid)
            
            # Pass B: Character 3-grams of first/core token
            norm_name = row["business_name_clean"]
            if norm_name:
                first_tok = norm_name.split()[0]
                if len(first_tok) >= 3:
                    for ng in generate_char_ngrams(first_tok, 3):
                        self.ngram_index[(country, ng)].add(tid)
            
            # Pass C: Country + Address Number / Postal code
            for num in row["address_numbers"]:
                if len(num) >= 3:  # House number or zip code
                    # Combine with first 2 chars of name
                    prefix = norm_name[:2] if len(norm_name) >= 2 else "xx"
                    self.country_num_index[(country, num, prefix)].add(tid)

    def retrieve_candidates_for_record(self, s1_row: pd.Series) -> List[str]:
        """Multi-pass candidate retrieval and fast scoring for a single S1 record."""
        s1_country = s1_row["country_clean"]
        s1_name = s1_row["business_name_clean"]
        s1_tokens = s1_row["name_tokens"]
        s1_nums = s1_row["address_numbers"]
        
        candidates = set()
        
        # 1. Informative Token Index Retrieval
        for tok in s1_tokens:
            if len(tok) >= self.min_token_len and tok not in STOP_TOKENS:
                # Query with country
                candidates.update(self.name_token_index.get((s1_country, tok), set()))
                if not s1_country:
                    candidates.update(self.name_token_index.get(("", tok), set()))
        
        # 2. Character 3-Gram Index Retrieval on first token
        if s1_name:
            s1_first = s1_name.split()[0]
            if len(s1_first) >= 3:
                for ng in generate_char_ngrams(s1_first, 3):
                    cands = self.ngram_index.get((s1_country, ng), set())
                    # Limit noisy ngram fan-out
                    if len(cands) <= 100:
                        candidates.update(cands)
                        
        # 3. Numeric / PIN code + Prefix Index Retrieval
        for num in s1_nums:
            if len(num) >= 3:
                prefix = s1_name[:2] if len(s1_name) >= 2 else "xx"
                candidates.update(self.country_num_index.get((s1_country, num, prefix), set()))
                
        # 4. Strict Country Check
        # If both S1 and target have specified countries and they conflict, discard
        filtered_cands = []
        for tid in candidates:
            tgt = self.target_records[tid]
            tgt_country = tgt["country_clean"]
            if s1_country and tgt_country and s1_country != tgt_country:
                continue
            filtered_cands.append(tid)
            
        if not filtered_cands:
            return []
            
        # 5. Fast Lexical Pre-ranking if candidate pool > top_k
        if len(filtered_cands) <= self.top_k:
            return filtered_cands
            
        scored = []
        s1_addr = s1_row["business_address_clean"]
        for tid in filtered_cands:
            tgt = self.target_records[tid]
            tgt_name = tgt["business_name_clean"]
            tgt_addr = tgt["business_address_clean"]
            
            # Fast token overlap / sort ratio
            name_score = fuzz.token_sort_ratio(s1_name, tgt_name)
            addr_score = fuzz.token_set_ratio(s1_addr, tgt_addr)
            combined_score = 0.7 * name_score + 0.3 * addr_score
            scored.append((combined_score, tid))
            
        # Sort descending and take top_k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [tid for _, tid in scored[:self.top_k]]

    def generate_all_candidate_pairs(self, s1_df: pd.DataFrame) -> Dict[str, List[str]]:
        """Generates candidates for every Source 1 record."""
        results = {}
        for _, row in s1_df.iterrows():
            s1_id = row["entity_id"]
            results[s1_id] = self.retrieve_candidates_for_record(row)
        return results
