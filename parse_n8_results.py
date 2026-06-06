#!/usr/bin/env python3
"""Parse final n=8 twin sieve results from the log file."""

import json
import sys

LOG_PATH = "/home/rebecca/n8_run_v3.log"
JSON_PATH = "/home/rebecca/n8_results_v2.json"

def main():
    # First check for the JSON output (preferred — structured data)
    try:
        with open(JSON_PATH) as f:
            data = json.load(f)
        
        print("=== n=8 Census Results (from JSON) ===")
        print(f"  Total twin pairs:    {data['total_twins']:,.0f}")
        print(f"  Admissible classes:  {data['admissible_classes']:,}")
        print(f"  Mean per class:      {data['mean_per_class']:,.2f}")
        print(f"  Min class count:     {data['min_class']:,}")
        print(f"  Max class count:     {data['max_class']:,}")
        print(f"  CV:                  {data['cv_percent']:.4f}%")
        print(f"  m(8)/Avg ratio:      {data['m_avg_ratio']:.6f}")
        print(f"  Empty classes:       {data['empty_classes']}")
        print(f"  Elapsed:             {data['elapsed_seconds']/3600:.2f} hours")
        print()
        
        # Compare to Li₂ structural prediction
        predicted_total = 128_248_757_262  # Li₂(P₈²)
        predicted_mean = 338_677.65
        actual = data['total_twins']
        error_pct = (actual - predicted_total) / predicted_total * 100
        
        print("=== vs. Structural Prediction (Li₂) ===")
        print(f"  Predicted total:     {predicted_total:,}")
        print(f"  Actual total:        {actual:,}")
        print(f"  Error:               {error_pct:+.4f}%")
        print(f"  Predicted mean:      {predicted_mean:,.2f}")
        print(f"  Actual mean:         {data['mean_per_class']:,.2f}")
        return
        
    except FileNotFoundError:
        pass
    
    # Fallback: parse from log file
    try:
        with open(LOG_PATH) as f:
            content = f.read()
        
        if "COMPLETE!" not in content:
            print("n=8 census not yet complete. Check progress:")
            print("  tail -3 /home/rebecca/n8_run_v3.log")
            return
        
        import re
        
        total_match = re.search(r'Total twin pairs:\s+([\d,]+)', content)
        mean_match = re.search(r'Mean per class:\s+([\d.]+)', content)
        cv_match = re.search(r'CV:\s+([\d.]+)%', content)
        min_match = re.search(r'Min class:\s+([\d,]+)', content)
        max_match = re.search(r'Max class:\s+([\d,]+)', content)
        empty_match = re.search(r'Empty classes:\s+([\d,]+)', content)
        elapsed_match = re.search(r'Elapsed:\s+([\d.]+)\s+hours', content)
        
        print("=== n=8 Census Results (from log) ===")
        if total_match:
            total = int(total_match.group(1))
            print(f"  Total twin pairs:    {total:,}")
        if mean_match:
            print(f"  Mean per class:      {float(mean_match.group(1)):,.2f}")
        if cv_match:
            print(f"  CV:                  {float(cv_match.group(1)):.4f}%")
        if min_match:
            print(f"  Min class:           {int(min_match.group(1)):,}")
        if max_match:
            print(f"  Max class:           {int(max_match.group(1)):,}")
        if empty_match:
            print(f"  Empty classes:       {int(empty_match.group(1))}")
        if elapsed_match:
            print(f"  Elapsed:             {elapsed_match.group(1)} hours")
        
    except FileNotFoundError:
        print(f"Log file not found at {LOG_PATH}")

if __name__ == "__main__":
    main()
