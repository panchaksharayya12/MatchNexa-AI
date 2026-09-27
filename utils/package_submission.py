#!/usr/bin/env python3
"""
Automated Submission Packaging Script for Amazon ML Challenge 2026.
Validates submission files and creates the compliant zip archive:
<team_name>_submission.zip
"""

import os
import sys
import zipfile
import subprocess
import argparse

sys.stdout.reconfigure(encoding='utf-8')

def package_submission(team_name: str, test_dir: str = "dataset/test", skip_validation: bool = True):
    matching_file = "output/matching_results.tsv"
    candidate_file = "output/candidate_pairs.tsv"
    code_dir = "code/business_entity_resolution"
    doc_file = "Documentation_template.md"
    
    if not skip_validation:
        print(f"Step 1: Running submission validation for team '{team_name}'...")
        val_cmd = [
            sys.executable,
            "utils/validate_submission.py",
            "--matching", matching_file,
            "--candidate", candidate_file,
            "--test-dir", test_dir
        ]
        
        ret = subprocess.run(val_cmd)
        if ret.returncode != 0:
            print("\n[ERROR] Packaging aborted: Validation did not pass!")
            sys.exit(1)
    else:
        print(f"Step 1: Skipping redundant validation for team '{team_name}' (already verified)...")
        
    print("\nStep 2: Building official submission zip package...")
    zip_filename = f"{team_name}_submission.zip"
    
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Add output files
        zf.write(matching_file, "output/matching_results.tsv")
        zf.write(candidate_file, "output/candidate_pairs.tsv")
        
        # 2. Add documentation
        if os.path.exists(doc_file):
            zf.write(doc_file, "Documentation_template.md")
        else:
            print(f"Warning: {doc_file} not found.")
            
        # 3. Add code files
        for root, dirs, files in os.walk(code_dir):
            # Ignore pycache
            if "__pycache__" in root:
                continue
            for f in files:
                full_path = os.path.join(root, f)
                arcname = os.path.relpath(full_path, ".")
                zf.write(full_path, arcname)
                
    print(f"\n[SUCCESS] Successfully generated final submission package: {zip_filename}")
    print("Contents:")
    with zipfile.ZipFile(zip_filename, "r") as zf:
        for info in zf.infolist():
            print(f"  • {info.filename} ({info.file_size:,} bytes)")

def main():
    parser = argparse.ArgumentParser(description="Package Amazon ML Challenge submission.")
    parser.add_argument("--team-name", default="NeuroNexa", help="Team name for submission ZIP")
    parser.add_argument("--test-dir", default="dataset/test", help="Test dataset directory")
    parser.add_argument("--skip-validation", action="store_true", help="Skip re-running validation if already verified")
    args = parser.parse_args()
    
    package_submission(args.team_name, args.test_dir, skip_validation=args.skip_validation)

if __name__ == "__main__":
    main()
