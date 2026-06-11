#!/usr/bin/env python3
"""
triplet_census.py — Segmented census of prime triplet admissible classes.

Computes class counts for both triplet patterns:
  Pattern A: (p, p+2, p+6)
  Pattern B: (p, p+4, p+6)

over the range [P_n, P_n^2], binned by residue mod P_n.

Usage:
    python3 triplet_census.py --n 6 [--segment-size 4194304] [--output results.json]

Range for n=6:  [30030, 901810900]    ~9e8   (640 classes each)
Range for n=7:  [510510, 2.606e11]    ~2.6e11 (8960 classes each)
Range for n=8:  [9699690, 9.41e13]    ~9.4e13 (143360 classes each)
"""

import math
import time
import json
import argparse
import sys

def compute_admissible_classes(n):
    """Compute triplet-admissible residues mod P_n for (p,p+2,p+6).
    A residue a is admissible if a, a+2, a+6 are all coprime to all primes <= p_n."""
    # Primorial and primes up to n
    primes = []
    p = 2
    Pn = 1
    while p <= n:
        primes.append(p)
        Pn *= p
        p += 1
        while any(p % q == 0 for q in primes):
            p += 1
    
    admissible = []
    for a in range(Pn):
        ok = True
        for p in primes:
            if a % p == 0 or (a + 2) % p == 0 or (a + 6) % p == 0:
                ok = False
                break
        if ok:
            admissible.append(a)
    return Pn, admissible

def compute_admissible_classes_B(n):
    """Compute triplet-admissible residues mod P_n for (p,p+4,p+6)."""
    primes = []
    p = 2
    Pn = 1
    while p <= n:
        primes.append(p)
        Pn *= p
        p += 1
        while any(p % q == 0 for q in primes):
            p += 1
    
    admissible = []
    for a in range(Pn):
        ok = True
        for p in primes:
            if a % p == 0 or (a + 4) % p == 0 or (a + 6) % p == 0:
                ok = False
                break
        if ok:
            admissible.append(a)
    return Pn, admissible

def sieve_triplet_census(n, segment_size=1 << 22):
    """Run segmented sieve over [Pn, Pn^2], binning by residue class mod Pn."""
    # Find first n primes
    primes = []
    p = 2
    Pn = 1
    while len(primes) < n:
        # check if p is prime
        is_prime = all(p % q != 0 for q in primes if q * q <= p) if primes else True
        if is_prime:
            primes.append(p)
            Pn *= p
        p += 1
    
    limit = Pn * Pn
    start = Pn
    sqrt_lim = int(math.isqrt(limit))
    
    print(f"n={n}, P_n={Pn:,}, P_n^2={limit:,}")
    print(f"Range: [{start:,}, {limit:,}] = {limit - start:,} integers")
    
    # Compute admissible classes for pattern A (p, p+2, p+6)
    Adm_A = set()
    Adm_A_list = []
    for a in range(Pn):
        ok = True
        for p in primes:
            if a % p == 0 or (a + 2) % p == 0 or (a + 6) % p == 0:
                ok = False
                break
        if ok:
            Adm_A.add(a)
            Adm_A_list.append(a)
    
    # Residue -> index map for fast binning
    res2idx_A = {r: i for i, r in enumerate(Adm_A_list)}
    counts_A = [0] * len(Adm_A_list)
    
    # And pattern B (p, p+4, p+6)
    Adm_B_list = []
    res2idx_B = {}
    for a in range(Pn):
        ok = True
        for p in primes:
            if a % p == 0 or (a + 4) % p == 0 or (a + 6) % p == 0:
                ok = False
                break
        if ok:
            res2idx_B[a] = len(Adm_B_list)
            Adm_B_list.append(a)
    
    counts_B = [0] * len(Adm_B_list)
    
    print(f"Pattern A (p,p+2,p+6): {len(Adm_A_list)} admissible classes")
    print(f"Pattern B (p,p+4,p+6): {len(Adm_B_list)} admissible classes")
    
    # Base primes up to sqrt(limit)
    t0 = time.time()
    small_sieve = bytearray([True]) * (sqrt_lim + 1)
    small_sieve[0] = small_sieve[1] = False
    for i in range(2, int(math.isqrt(sqrt_lim)) + 1):
        if small_sieve[i]:
            small_sieve[i*i:sqrt_lim+1:i] = bytearray(
                [False] * ((sqrt_lim - i*i) // i + 1)
            )
    base_primes = [i for i, b in enumerate(small_sieve) if b]
    print(f"Base primes: {len(base_primes):,} (to {sqrt_lim:,})")
    
    total_primes = 0
    prev_primes = []  # overlap for boundary detection
    seg_total_A = 0
    seg_total_B = 0
    overlap = 6
    
    seg_start = start
    seg_idx = 0
    num_segs = (limit - start + segment_size - 1) // segment_size
    
    while seg_start < limit:
        seg_end = min(seg_start + segment_size, limit)
        seg_len = seg_end - seg_start
        seg = bytearray([True]) * seg_len
        
        for p in base_primes:
            start_mark = max(p * p, ((seg_start + p - 1) // p) * p)
            offset = start_mark - seg_start
            if offset < seg_len:
                seg[offset:seg_len:p] = bytearray([False] * ((seg_len - 1 - offset) // p + 1))
        
        # Extract primes from this segment
        seg_primes = [seg_start + i for i, b in enumerate(seg) if b]
        total_primes += len(seg_primes)
        
        # Boundary detection
        candidates = [pp for pp in prev_primes if pp >= seg_start - overlap] + seg_primes
        candidate_set = set(candidates)
        
        # Count triplets by class
        for p in candidates:
            if p + 6 > limit:
                break
            if p < start:
                continue
            # Pattern A
            if (p + 2) in candidate_set and (p + 6) in candidate_set:
                r = p % Pn
                if r in res2idx_A:
                    idx = res2idx_A[r]
                    counts_A[idx] += 1
                    seg_total_A += 1
            # Pattern B
            if (p + 4) in candidate_set and (p + 6) in candidate_set:
                r = p % Pn
                if r in res2idx_B:
                    idx = res2idx_B[r]
                    counts_B[idx] += 1
                    seg_total_B += 1
        
        # Save overlap primes
        prev_primes = [p for p in seg_primes if p > seg_end - overlap - 1]
        
        seg_idx += 1
        if seg_idx % max(1, num_segs // 10) == 0:
            elapsed = time.time() - t0
            pct = seg_end / limit * 100
            print(f"  {pct:5.1f}% ({seg_end:,}/{limit:,}): {total_primes:,} primes, "
                  f"A={seg_total_A:,}, B={seg_total_B,:}, {elapsed:.0f}s")
        
        seg_start = seg_end
    
    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"Total primes scanned: {total_primes:,}")
    print(f"Pattern A total: {seg_total_A:,}")
    print(f"Pattern B total: {seg_total_B:,}")
    
    # Summary stats
    import statistics
    total_A = sum(counts_A)
    total_B = sum(counts_B)
    mean_A = total_A / len(counts_A) if counts_A else 0
    mean_B = total_B / len(counts_B) if counts_B else 0
    empty_A = sum(1 for c in counts_A if c == 0)
    empty_B = sum(1 for c in counts_B if c == 0)
    
    if len(counts_A) > 1 and mean_A > 0:
        cv_A = 100 * statistics.pstdev(counts_A) / mean_A
    else:
        cv_A = 0
    if len(counts_B) > 1 and mean_B > 0:
        cv_B = 100 * statistics.pstdev(counts_B) / mean_B
    else:
        cv_B = 0
    min_A = min(counts_A) if counts_A else 0
    max_A = max(counts_A) if counts_A else 0
    min_B = min(counts_B) if counts_B else 0
    max_B = max(counts_B) if counts_B else 0
    
    results = {
        "n": n,
        "P_n": Pn,
        "limit": limit,
        "range": f"[{start}, {limit}]",
        "elapsed_seconds": round(elapsed, 1),
        "total_primes_scanned": total_primes,
        "pattern_A": {
            "num_classes": len(Adm_A_list),
            "admissible_residues": Adm_A_list,
            "counts": counts_A,
            "total_pairs": total_A,
            "mean": round(mean_A, 1),
            "min": min_A,
            "max": max_A,
            "cv_pct": round(cv_A, 4),
            "empty_classes": empty_A,
        },
        "pattern_B": {
            "num_classes": len(Adm_B_list),
            "admissible_residues": Adm_B_list,
            "counts": counts_B,
            "total_pairs": total_B,
            "mean": round(mean_B, 1),
            "min": min_B,
            "max": max_B,
            "cv_pct": round(cv_B, 4),
            "empty_classes": empty_B,
        }
    }
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True, help="Primorial index n")
    parser.add_argument("--segment-size", type=int, default=1 << 22, help="Segment size in bytes")
    parser.add_argument("--output", type=str, default=None, help="Output JSON file")
    args = parser.parse_args()
    
    results = sieve_triplet_census(args.n, args.segment_size)
    
    outfile = args.output or f"triplet_census_n{args.n}.json"
    with open(outfile, "w") as f:
        json.dump(results, f)
    print(f"\nResults saved to {outfile}")
