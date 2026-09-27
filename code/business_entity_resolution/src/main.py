#!/usr/bin/env python3
"""
CLI entry point for the MatchNexa Business Entity Resolution System.
Amazon ML Challenge 2026.
"""

import os
import sys
import argparse

# Ensure current directory and src directory are on sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from pipeline import EntityResolutionPipeline
except ImportError:
    from .pipeline import EntityResolutionPipeline

def main():
    parser = argparse.ArgumentParser(description="Run MatchNexa Business Entity Resolution Pipeline.")
    parser.add_argument("--train-dir", default="dataset/train", help="Path to training data directory")
    parser.add_argument("--test-dir", default="dataset/test", help="Path to test data directory")
    parser.add_argument("--output-dir", default="output", help="Path to output directory")
    parser.add_argument("--top-k", type=int, default=25, help="Max candidates per Source 1 entity in blocking")
    
    args = parser.parse_args()
    
    pipeline = EntityResolutionPipeline(top_k_candidates=args.top_k)
    
    print("Starting MatchNexa Entity Resolution System...")
    pipeline.train_and_validate(train_dir=args.train_dir)
    pipeline.predict_test(test_dir=args.test_dir, output_dir=args.output_dir)
    
    print("\n[SUCCESS] Execution completed successfully.")

if __name__ == "__main__":
    main()

# Vercel entrypoint exports
handler = main
app = main
application = main

