"""
Scalable, Country-Partitioned Entity Resolution Engine.
Processes test dataset country-by-country to ensure minimal RAM usage and high throughput.
Generates output/candidate_pairs.tsv and output/matching_results.tsv.
"""

import sys
import os
import re
import time
import gc
from collections import defaultdict
import numpy as np
from rapidfuzz import fuzz
import joblib

sys.stdout.reconfigure(encoding='utf-8')

LEGAL_SUFFIXES = {
    'inc', 'corp', 'corporation', 'llc', 'llp', 'ltd', 'limited', 'pvt', 'private',
    'co', 'company', 'sa', 'sas', 'sarl', 'gmbh', 'solutions', 'services', 'technologies',
    'group', 'holdings', 'associes', 'et', 'cie'
}
STOPWORDS = {'the', 'and', 'of', 'in', 'at', 'for', 'with', 'a', 'an', 'to', 'from', 'de', 'du', 'des', 'la', 'le'}

def clean_toks(s):
    toks = [w for w in re.sub(r'[^a-zA-Z0-9\s]', ' ', s.lower()).split() if w not in STOPWORDS]
    filtered = [w for w in toks if w not in LEGAL_SUFFIXES]
    return filtered if filtered else toks

def get_nums(s):
    return set(re.findall(r'\b\d+\b', s))

def get_addr_keys(s):
    nums = re.findall(r'\b\d+\b', s)
    toks = [w for w in re.sub(r'[^a-zA-Z0-9\s]', ' ', s.lower()).split() if len(w) >= 3 and w not in STOPWORDS and w not in {'street', 'st', 'road', 'rd', 'avenue', 'ave', 'lane', 'dr', 'drive', 'rue', 'boulevard', 'blvd'}]
    keys = []
    if nums and toks:
        keys.append(f"{nums[0]}_{toks[0]}")
    return keys

def compute_features(s1_name, s1_addr, tgt_name, tgt_addr, tid):
    n_ratio = fuzz.ratio(s1_name, tgt_name) / 100.0
    n_sort = fuzz.token_sort_ratio(s1_name, tgt_name) / 100.0
    n_set = fuzz.token_set_ratio(s1_name, tgt_name) / 100.0
    
    t1 = set(clean_toks(s1_name))
    t2 = set(clean_toks(tgt_name))
    n_jaccard = len(t1 & t2) / max(len(t1 | t2), 1)
    first_tok_match = 1.0 if (t1 and t2 and list(t1)[0] == list(t2)[0]) else 0.0
    
    a_ratio = fuzz.ratio(s1_addr, tgt_addr) / 100.0
    a_set = fuzz.token_set_ratio(s1_addr, tgt_addr) / 100.0
    
    at1 = set(re.findall(r'\b\w+\b', s1_addr.lower()))
    at2 = set(re.findall(r'\b\w+\b', tgt_addr.lower()))
    a_jaccard = len(at1 & at2) / max(len(at1 | at2), 1)
    
    num1 = get_nums(s1_addr)
    num2 = get_nums(tgt_addr)
    num_shared = float(len(num1 & num2))
    num_mismatch = 1.0 if (num1 and num2 and not (num1 & num2)) else 0.0
    
    is_s2 = 1.0 if tid.startswith('S2-') else 0.0
    is_s3 = 1.0 if tid.startswith('S3-') else 0.0
    joint_score = n_set * a_set
    
    return [n_ratio, n_sort, n_set, n_jaccard, first_tok_match, a_ratio, a_set, a_jaccard, num_shared, num_mismatch, is_s2, is_s3, joint_score]

def run_entity_resolution():
    print("=" * 70)
    print("MATCHING PIPELINE: Loading Model & Initializing Partitions")
    print("=" * 70)
    
    model_path = 'code/business_entity_resolution/src/lightgbm_model.pkl'
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at {model_path}")
    
    clf = joblib.load(model_path)
    threshold = 0.740
    print(f"Loaded LightGBM model. Using tuned Macro F0.5 Threshold: {threshold}")
    
    # 1. Read all Test S1 entity IDs and metadata
    print("\nReading test_source1.tsv...")
    s1_order = []
    country_to_s1 = defaultdict(list)
    s1_data = {}
    
    with open('dataset/test/test_source1.tsv', encoding='utf-8') as f:
        next(f)
        for line in f:
            p = line.strip().split('\t')
            sid = p[0]
            name = p[1] if len(p) > 1 else ''
            addr = p[2] if len(p) > 2 else ''
            country = p[3] if len(p) > 3 else 'US'
            s1_order.append(sid)
            country_to_s1[country].append(sid)
            s1_data[sid] = (name, addr)
            
    print(f"Total Test S1 entities: {len(s1_order):,}")
    for c, items in country_to_s1.items():
        print(f"  • {c}: {len(items):,} entities")
        
    s1_candidates = {}
    s1_matches = {}
    
    # 2. Process each country partition
    for country in ['France', 'US', 'India']:
        if country not in country_to_s1:
            continue
        print("\n" + "-" * 70)
        print(f"PROCESSING PARTITION: {country} ({len(country_to_s1[country]):,} S1 entities)")
        print("-" * 70)
        t_start = time.time()
        
        # Build inverted index for this country
        print(f"Streaming and indexing S2 & S3 targets for {country}...")
        index_n2 = defaultdict(list)
        index_n1 = defaultdict(list)
        index_addr = defaultdict(list)
        target_store = {}
        
        for src_file in ['dataset/test/test_source2.tsv', 'dataset/test/test_source3.tsv']:
            with open(src_file, encoding='utf-8') as f:
                next(f)
                for line in f:
                    p = line.strip().split('\t')
                    c = p[3] if len(p) > 3 else ''
                    if c != country:
                        continue
                    tid = p[0]
                    name = p[1] if len(p) > 1 else ''
                    addr = p[2] if len(p) > 2 else ''
                    target_store[tid] = (name, addr)
                    
                    # Indexing
                    toks = clean_toks(name)
                    if toks:
                        if len(index_n1[toks[0]]) < 100:
                            index_n1[toks[0]].append(tid)
                        if len(toks) >= 2:
                            k2 = f"{toks[0]}_{toks[1]}"
                            if len(index_n2[k2]) < 100:
                                index_n2[k2].append(tid)
                    for ak in get_addr_keys(addr):
                        if len(index_addr[ak]) < 100:
                            index_addr[ak].append(tid)
                            
        print(f"Loaded {len(target_store):,} target records for {country} in {time.time() - t_start:.2f}s")
        
        # Candidate Generation & Inference for this country's S1 entities
        print(f"Running candidate retrieval and ML scoring for {country}...")
        t_infer = time.time()
        country_s1_list = country_to_s1[country]
        batch_size = 10000
        
        for b_idx in range(0, len(country_s1_list), batch_size):
            batch_s1 = country_s1_list[b_idx:b_idx + batch_size]
            
            # Retrieve candidates for batch
            batch_pairs = []
            pair_meta = []
            
            for sid in batch_s1:
                s1_name, s1_addr = s1_data[sid]
                toks = clean_toks(s1_name)
                addr_keys = get_addr_keys(s1_addr)
                
                cands = set()
                if toks:
                    if len(toks) >= 2:
                        cands.update(index_n2.get(f"{toks[0]}_{toks[1]}", []))
                    if len(cands) < 15:
                        cands.update(index_n1.get(toks[0], []))
                for ak in addr_keys:
                    cands.update(index_addr.get(ak, []))
                    
                cand_list = list(cands)
                if len(cand_list) > 20:
                    cand_list = cand_list[:20]
                    
                s1_candidates[sid] = cand_list
                s1_matches[sid] = []
                
                for tid in cand_list:
                    tgt_name, tgt_addr = target_store[tid]
                    feat = compute_features(s1_name, s1_addr, tgt_name, tgt_addr, tid)
                    batch_pairs.append(feat)
                    pair_meta.append((sid, tid))
                    
            if batch_pairs:
                X_batch = np.array(batch_pairs, dtype=np.float32)
                probs = clf.predict_proba(X_batch)[:, 1]
                for (sid, tid), prob in zip(pair_meta, probs):
                    if prob >= threshold:
                        s1_matches[sid].append(tid)
                        
            if (b_idx + batch_size) % 100000 == 0 or (b_idx + batch_size) >= len(country_s1_list):
                processed = min(b_idx + batch_size, len(country_s1_list))
                pct = processed / len(country_s1_list) * 100
                print(f"  Processed {processed:,} / {len(country_s1_list):,} ({pct:.1f}%) in {time.time() - t_infer:.1f}s")
                
        print(f"Completed {country} in {time.time() - t_start:.2f}s.")
        
        # Free memory before next country
        del index_n2, index_n1, index_addr, target_store
        gc.collect()

    print("\n" + "=" * 70)
    print("STAGE 3: Writing Official Submission Files")
    print("=" * 70)
    os.makedirs('output', exist_ok=True)
    match_file = 'output/matching_results.tsv'
    cand_file = 'output/candidate_pairs.tsv'
    
    t_write = time.time()
    with open(match_file, 'w', encoding='utf-8') as fm, open(cand_file, 'w', encoding='utf-8') as fc:
        fm.write("source1_entity_id\tmatched_entity_ids\n")
        fc.write("source1_entity_id\tcandidate_entity_ids\n")
        
        matched_count = 0
        singleton_count = 0
        
        for sid in s1_order:
            cands = s1_candidates.get(sid, [])
            matches = s1_matches.get(sid, [])
            
            # Enforce matches is strict subset of candidates
            valid_matches = [m for m in matches if m in cands]
            
            fm.write(f"{sid}\t{','.join(valid_matches)}\n")
            fc.write(f"{sid}\t{','.join(cands)}\n")
            
            if valid_matches:
                matched_count += 1
            else:
                singleton_count += 1
                
    print(f"Wrote {len(s1_order):,} records to {match_file} and {cand_file} in {time.time() - t_write:.2f}s")
    print(f"  • Matched S1 Entities: {matched_count:,} ({matched_count / len(s1_order) * 100:.2f}%)")
    print(f"  • Predicted Singletons: {singleton_count:,} ({singleton_count / len(s1_order) * 100:.2f}%)")
    print("\n[SUCCESS] Entity Resolution inference completed successfully!")

if __name__ == '__main__':
    run_entity_resolution()
