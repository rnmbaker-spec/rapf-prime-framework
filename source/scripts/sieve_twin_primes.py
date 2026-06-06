#!/usr/bin/env python3
"""
sieve_10_9.py - Memory-efficient segmented sieve up to 10^9.
Computes twin-to-twin gaps without storing all primes simultaneously.
Tracks only boundary primes between segments to detect cross-segment twins.
"""
import math
import time
import sys
from array import array

def segmented_twin_sieve(limit, segment_size=1 << 22):
    """Segmented sieve up to limit, collecting twin prime pair pivots.
    
    Processes segments sequentially, keeping only the last prime from the
    previous segment to detect twins that cross segment boundaries.
    
    Returns: (sorted list of twin pivots, total prime count)
    """
    sqrt_lim = int(math.isqrt(limit))
    
    # Small sieve for base primes up to sqrt(limit)
    small_sieve = bytearray([True]) * (sqrt_lim + 1)
    small_sieve[0] = small_sieve[1] = False
    for i in range(2, int(math.isqrt(sqrt_lim)) + 1):
        if small_sieve[i]:
            slice_start = i * i
            small_sieve[slice_start:sqrt_lim + 1:i] = bytearray([False]) * (
                (sqrt_lim - slice_start) // i + 1
            )
    
    base_primes = [i for i, is_p in enumerate(small_sieve) if is_p]
    print(f"Base primes up to sqrt({limit:,})={sqrt_lim:,}: {len(base_primes):,}")
    
    twin_pivots = []  # Store the smaller prime p in each twin pair (p, p+2)
    total_primes = 0
    prev_prime = None  # Last prime from previous segment (for boundary twin detection)
    num_segments = (limit + segment_size - 1) // segment_size
    
    for seg_idx, seg_start in enumerate(range(0, limit + 1, segment_size)):
        seg_end = min(seg_start + segment_size, limit + 1)
        seg = bytearray([True]) * (seg_end - seg_start)
        
        for p in base_primes:
            # First multiple of p >= seg_start
            start = max(p * p, ((seg_start + p - 1) // p) * p)
            for multiple in range(start - seg_start, seg_end - seg_start, p):
                seg[multiple] = False
        
        if seg_start == 0:
            seg[0] = seg[1] = False
        
        # Extract primes from this segment
        seg_primes = []
        for i in range(seg_end - seg_start):
            if seg[i]:
                seg_primes.append(seg_start + i)
        
        # Check for twin pair crossing the segment boundary
        if prev_prime is not None and len(seg_primes) > 0:
            if seg_primes[0] - prev_prime == 2:
                twin_pivots.append((prev_prime, seg_primes[0]))
        
        # Find twin pairs within this segment
        for i in range(len(seg_primes) - 1):
            if seg_primes[i + 1] - seg_primes[i] == 2:
                twin_pivots.append((seg_primes[i], seg_primes[i + 1]))
        
        total_primes += len(seg_primes)
        if seg_primes:
            prev_prime = seg_primes[-1]
    
    return twin_pivots, total_primes

def analyze_results(twin_pivots, total_primes, limit):
    """Analyze twin prime statistics and compare to Hardy-Littlewood."""
    C2 = 0.6601618158
    logX = math.log(limit)
    lambdaHL = logX * logX / (2 * C2)
    
    print(f"\n{'='*60}")
    print(f"Results: Twin Prime Analysis up to {limit:,}")
    print(f"{'='*60}")
    print(f"Total primes:       {total_primes:>12,}")
    print(f"Twin prime pairs:   {len(twin_pivots):>12,}")
    
    # Validate known values
    expected = {10**6: 8169, 10**7: 58980, 10**8: 440312, 10**9: 3424506}
    if limit in expected:
        exp = expected[limit]
        diff = len(twin_pivots) - exp
        status = "MATCH" if diff == 0 else "MISMATCH"
        print(f"Expected pi2(limit): {exp:>12,} -> {status} (diff: {diff:+,})")
    
    # Twin-to-twin gaps (excluding the 3→5 transition gap=2, which is the only
    # gap not divisible by 6; theory applies only for primes > 3)
    n_gaps = len(twin_pivots) - 2  # exclude first gap
    twin_gaps = array('I')
    for i in range(1, len(twin_pivots) - 1):  # start from index 1, skip first gap
        gap = twin_pivots[i + 1][0] - twin_pivots[i][0]
        twin_gaps.append(gap)
    
    mean_gap = sum(twin_gaps) / n_gaps
    ratio = mean_gap / lambdaHL
    
    print(f"\nTwin-to-twin gaps:   {n_gaps:>12,} (excluding 3->5 gap=2)")
    print(f"Mean gap (lambda-hat): {mean_gap:.4f}")
    print(f"HL prediction:         {lambdaHL:.4f}")
    print(f"Ratio (hat/HL):        {ratio:.6f}")
    print(f"Deviation:             {(1 - ratio)*100:.2f}%")
    
    # Verify all gaps divisible by 6
    non_mult6 = sum(1 for g in twin_gaps if g % 6 != 0)
    print(f"\nAll gaps mod 6 == 0:  {'YES' if non_mult6 == 0 else f'NO ({non_mult6} violations)'}")
    print(f"Min gap: {min(twin_gaps)} (expected: 6)")
    print(f"Max gap: {max(twin_gaps):,}")
    
    # Gap distribution
    gap_counts = {}
    for g in twin_gaps:
        gap_counts[g] = gap_counts.get(g, 0) + 1
    
    print(f"\nTop twin-to-twin gap values:")
    for gap, count in sorted(gap_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  gap={gap:<5} ({gap//6:>3}x6): {count:>8,} ({count/n_gaps*100:5.2f}%)")
    
    return {
        'limit': limit,
        'pi': total_primes,
        'pi2': len(twin_pivots),
        'lambda_hat': mean_gap,
        'lambda_hl': lambdaHL,
        'ratio': ratio,
        'n_gaps': n_gaps,
    }

if __name__ == "__main__":
    limit = 10**9
    print(f"Segmented twin sieve: limit = {limit:,}")
    print(f"Expected pi2(10^9) = 3,424,506")
    print()
    
    t0 = time.time()
    twin_pivots, total_primes = segmented_twin_sieve(limit)
    sieve_time = time.time() - t0
    
    print(f"\nSieve complete in {sieve_time:.2f}s")
    print(f"Twin pivots: {len(twin_pivots):,} tuples ({len(twin_pivots) * 16 / 10**6:.1f}MB)")
    
    print()
    analyze_results(twin_pivots, total_primes, limit)

    print(f"\nTotal time: {time.time() - t0:.2f}s")
