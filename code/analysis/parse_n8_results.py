#!/usr/bin/env python3
"""Parse final n=8 twin sieve results from the log file or JSON output."""

import json
import sys
import re

LOG_PATH = "/home/rebecca/n8_run_v3.log"
JSON_PATH = "/home/rebecca/n8_results_v2.json"

def main():
    # Check for JSON output first
    try:
        with open(JSON_PATH) as f:
            data = json.load(f)
        print("=== n=8 Census Results (JSON) ===")
        print(f"  Total twin pairs:    {data['total_twins']:,.0f}")
        print(f"  Mean per class:      {data['mean_per_class']:,.2f}")
        print(f"  CV:                  {data['cv_percent']:.4f}%")
        print(f"  Min class:           {data['min_class']:,}")
        print(f"  Max class:           {data['max_class']:,}")
        print(f"  Empty classes:       {data['empty_classes']}")
        print(f"  Elapsed:             {data['elapsed_seconds']/3600:.2f} hours")
        
        predicted_total = 128_248_757_262
        error_pct = (data['total_twins'] - predicted_total) / predicted_total * 100
        print(f"  Prediction error:    {error_pct:+.4f}%")
        return
    except FileNotFoundError:
        pass
    
    # Parse from log
    try:
        with open(LOG_PATH) as f:
            content = f.read()
        if "COMPLETE!" not in content:
            print("Not yet complete.")
            return
        for field in ['Total twin pairs', 'Mean per class', 'CV:', 'Min class', 'Max class']:
            m = re.search(rf'{field}[:\s]+([\d,.]+)', content)
            if m:
                print(f"  {field}: {m.group(1)}")
    except FileNotFoundError:
        print("Log not found.")

if __name__ == "__main__":
    main()
