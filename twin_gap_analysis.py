#!/usr/bin/env python3
"""
twin_gap_analysis.py - Extract twin prime positions, compute gaps between successive twins,
and fit the exponential model P(r) = (1/λ) e^{-r/λ} to the twin-to-twin gap distribution.
Reports: twin count, mean twin gap, MLE λ, Fisher metric, KS test result.
"""
import math
import time
import numpy as np
from scipy import stats

def segmented_prime_sieve(limit):
    """Segmented sieve returning all primes up to limit."""
    sqrt_lim = int(math.isqrt(limit))
    small_sieve = bytearray([True]) * (sqrt_lim + 1)
    small_sieve[0] = small_sieve[1] = False
    for i in range(2, int(math.isqrt(sqrt_lim)) + 1):
        if small_sieve[i]:
            slice_start = i * i
            small_sieve[slice_start:sqrt_lim + 1:i] = bytearray([False]) * ((sqrt_lim - slice_start) // i + 1)
    
    base_primes = [i for i, is_p in enumerate(small_sieve) if is_p]
    
    primes_found = []
    segment_size = 1 << 20
    
    for seg_start in range(0, limit + 1, segment_size):
        seg_end = min(seg_start + segment_size, limit + 1)
        seg = bytearray([True]) * (seg_end - seg_start)
        
        for p in base_primes:
            start = max(p * p, ((seg_start + p - 1) // p) * p)
            for multiple in range(start - seg_start, seg_end - seg_start, p):
                seg[multiple] = False
        
        if seg_start == 0:
            seg[0] = seg[1] = False
        
        for i in range(seg_end - seg_start):
            if seg[i]:
                primes_found.append(seg_start + i)
    
    return primes_found

if __name__ == "__main__":
    limit = 10**8
    print(f"Sieving primes up to {limit:,}...")
    t0 = time.time()
    primes = segmented_prime_sieve(limit)
    print(f"Found {len(primes):,} primes in {time.time()-t0:.2f}s")
    
    # Extract twin prime positions (smaller member of each pair)
    twins = []
    for i in range(len(primes) - 1):
        if primes[i + 1] - primes[i] == 2:
            twins.append(primes[i])
    
    print(f"\nTwin prime pairs: {len(twins):,}")
    print(f"Confirmed π₂(10⁸) = {len(twins):,} {'✓' if len(twins) == 440312 else '✗'}")
    
    # Compute gaps between successive twin prime pairs
    twin_gaps = [twins[i+1] - twins[i] for i in range(len(twins) - 1)]
    print(f"Twin-to-twin gaps: {len(twin_gaps):,}")
    
    # Fit exponential model: MLE for exponential is the sample mean
    mean_gap = sum(twin_gaps) / len(twin_gaps)
    print(f"Mean twin-to-twin gap: {mean_gap:.4f}")
    print(f"MLE λ̂ = {mean_gap:.4f}")
    
    # Fisher information metric
    fisher_metric = 1.0 / (mean_gap ** 2)
    print(f"Fisher metric g = 1/λ̂² = {fisher_metric:.6f}")
    
    # Normalized gap distribution (scale by λ)
    normalized = [g / mean_gap for g in twin_gaps]
    
    # KS test against exponential(1)
    ks_stat, ks_pval = stats.kstest(normalized, 'expon')
    print(f"\nKolmogorov-Smirnov test against Exp(1):")
    print(f"  KS statistic: {ks_stat:.6f}")
    print(f"  p-value: {ks_pval:.6f}")
    print(f"  {'Fail to reject' if ks_pval > 0.05 else 'Reject'} exponential hypothesis at α=0.05")
    
    # Anderson-Darling test
    ad_result = stats.anderson(normalized, dist='expon')
    print(f"\nAnderson-Darling test:")
    print(f"  A-D statistic: {ad_result.statistic:.6f}")
    print(f"  Critical values (15%, 10%, 5%, 2.5%, 1%): {ad_result.critical_values}")
    print(f"  {'Fail to reject' if ad_result.statistic < ad_result.critical_values[2] else 'Reject'} at 5% level")
    
    # Admissibility deformation parameter
    C2 = 0.6601618158468696
    lambda_obs = mean_gap
    lambda_0 = C2 * lambda_obs  # baseline (unthinned) scale
    g_obs = 1.0 / (lambda_obs ** 2)
    g_0 = 1.0 / (lambda_0 ** 2)
    delta_g = g_obs - g_0
    print(f"\nAdmissibility deformation (corrected):")
    print(f"  λ_obs = {lambda_obs:.4f}")
    print(f"  λ_0 = C₂ · λ_obs = {lambda_0:.4f}")
    print(f"  g_obs = 1/λ_obs² = {g_obs:.6f}")
    print(f"  g_0 = 1/λ_0² = {g_0:.6f}")
    print(f"  Δg = g_obs - g_0 = {delta_g:.6f}")
    
    # Theoretical vs observed comparison
    lambda_theory = 3.70
    g_theory = 1.0 / (lambda_theory ** 2)
    print(f"\nTheory vs observation:")
    print(f"  λ_theory = {lambda_theory}")
    print(f"  λ_obs = {mean_gap:.4f}")
    print(f"  |λ_obs - λ_theory| / λ_theory = {abs(mean_gap - lambda_theory)/lambda_theory*100:.2f}%")
    print(f"  g_theory = {g_theory:.6f}")
    print(f"  g_obs = {fisher_metric:.6f}")
    print(f"  |g_obs - g_theory| = {abs(fisher_metric - g_theory):.6f}")
    print(f"  1/√N = {1.0/math.sqrt(len(twin_gaps)):.6f}")
