#!/usr/bin/env python3
"""
theta_sieve_10^8.py - Segmented sieve counting twin primes up to 10^8.
Correctly handles segment boundaries. Reports count, timing, and gap stats.
"""
import math
import time

def segmented_prime_sieve(limit):
    """Segmented sieve returning all primes up to limit."""
    sqrt_lim = int(math.isqrt(limit))
    # Small sieve for base primes
    small_sieve = bytearray([True]) * (sqrt_lim + 1)
    small_sieve[0] = small_sieve[1] = False
    for i in range(2, int(math.isqrt(sqrt_lim)) + 1):
        if small_sieve[i]:
            slice_start = i * i
            small_sieve[slice_start:sqrt_lim + 1:i] = bytearray([False]) * ((sqrt_lim - slice_start) // i + 1)
    
    base_primes = [i for i, is_p in enumerate(small_sieve) if is_p]
    
    # Count primes in segments
    segment_size = 1 << 20  # ~1 MB segments
    primes_found = []
    
    for seg_start in range(0, limit + 1, segment_size):
        seg_end = min(seg_start + segment_size, limit + 1)
        seg = bytearray([True]) * (seg_end - seg_start)
        
        for p in base_primes:
            # First multiple of p >= seg_start
            start = max(p * p, ((seg_start + p - 1) // p) * p)
            for multiple in range(start - seg_start, seg_end - seg_start, p):
                seg[multiple] = False
        
        if seg_start == 0:
            seg[0] = seg[1] = False
        
        for i in range(seg_end - seg_start):
            if seg[i]:
                primes_found.append(seg_start + i)
    
    return primes_found

def count_twin_primes(primes):
    """Count twin prime pairs and return gap statistics."""
    twin_count = 0
    gaps = []
    
    for i in range(len(primes) - 1):
        gap = primes[i + 1] - primes[i]
        gaps.append(gap)
        if gap == 2:
            twin_count += 1
    
    return twin_count, gaps

if __name__ == "__main__":
    limit = 10**8
    print(f"Sieving primes up to {limit:,}...")
    
    t0 = time.time()
    primes = segmented_prime_sieve(limit)
    sieve_time = time.time() - t0
    print(f"Found {len(primes):,} primes in {sieve_time:.2f}s")
    
    t1 = time.time()
    twin_count, gaps = count_twin_primes(primes)
    twin_time = time.time() - t1
    print(f"Twin prime pairs: {twin_count:,} (computed in {twin_time:.2f}s)")
    
    if twin_count != 440312:
        print(f"WARNING: Expected 440,312 but got {twin_count}. Discrepancy: {440312 - twin_count:+d}")
    else:
        print("MATCH: Confirmed π₂(10⁸) = 440,312 ✓")
    
    # Gap distribution stats
    gap_counts = {}
    for g in gaps:
        gap_counts[g] = gap_counts.get(g, 0) + 1
    
    print(f"\nGap distribution (top 10):")
    for gap, count in sorted(gap_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  gap={gap}: {count:,} ({count/len(gaps)*100:.2f}%)")
    
    # Exponential fit for gap=2 pairs (twin gaps)
    twin_gaps = [2 for _ in range(twin_count)]  # All twins have gap 2
    regular_gaps = [g for g in gaps if g > 2]
    print(f"\nNon-twin gaps: {len(regular_gaps):,}")
    mean_gap = sum(regular_gaps) / len(regular_gaps) if regular_gaps else 0
    print(f"Mean non-twin gap: {mean_gap:.4f}")
