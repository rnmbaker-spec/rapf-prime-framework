"""
theta_sieve_n9_cuda.py — GPU-accelerated n=9 twin prime class census

Uses CUDA to sieve twin primes in admissible residue classes mod P₉.
Each GPU block handles one admissible class (arithmetic progression).
The sieve marks composites using primes > 23 (those dividing P₉ are already excluded).

Requires: numba with CUDA support
Usage: python theta_sieve_n9_cuda.py [limit] [num_classes]
  limit      : upper bound (default: 100B)
  num_classes: classes to sample (default: -1 = ALL 7,952,175)
"""
import math
import time
import sys
import numpy as np
from numba import cuda


P9 = 2 * 3 * 5 * 7 * 11 * 13 * 17 * 19 * 23  # 223092870
P9_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]


def compute_admissible():
    """Compute all twin-admissible residues mod P₉."""
    admiss = []
    for r in range(P9):
        ok = True
        for p in P9_PRIMES:
            if r % p == 0 or (r + 2) % p == 0:
                ok = False
                break
        if ok:
            admiss.append(r)
    return admiss


@cuda.jit
def sieve_theta_kernel(class_idx, residues, class_counts, base_primes, limit, P9_val):
    """Each block sieves ONE admissible residue class (arithmetic progression)."""
    bid = cuda.blockIdx.x
    if bid >= len(resides):
        return
    
    residue = residues[bid]
    if residue > limit:
        return
    
    # Count elements in this AP up to limit
    # AP: residue, residue + P₉, residue + 2*P₉, ...
    # We need positions >= P₉ and <= limit
    k_start = 1 if residue < P9_val else 0  # skip if residue < P₉
    k_end = (limit - residue) // P9_val
    
    if k_start > k_end:
        return
    
    num_pos = k_end - k_start + 1
    if num_pos <= 0:
        return
    
    # Count primes in this AP by checking divisibility
    # For GPU, we use shared memory per block
    # Each thread checks a range of positions
    
    tid = cuda.threadIdx.x
    n_threads = cuda.blockDim.x
    
    twins_found = 0
    
    # Sieve using base primes
    # Each thread iterates through positions with stride n_threads
    for k in range(k_start + tid, k_end + 1, n_threads):
        n = residue + k * P9_val
        if n < P9_val:
            continue
        
        # Check primality: not divisible by any base prime
        is_prime = True
        for p_idx in range(len(base_primes)):
            p = base_primes[p_idx]
            if p * p > n:
                break
            if n % p == 0:
                is_prime = False
                break
        
        if is_prime:
            # Check if n+2 is also prime (twin)
            n2 = n + 2
            is_prime2 = True
            for p_idx in range(len(base_primes)):
                p = base_primes[p_idx]
                if p * p > n2:
                    break
                if n2 % p == 0:
                    is_prime2 = False
                    break
            if is_prime2:
                twins_found += 1
    
    # Atomic add to class count
    cuda.atomic.add(class_counts, bid, twins_found)


def run_n9_theta_cuda(limit=100_000_000_000, num_classes=-1):
    """
    Run n=9 twin prime class census on GPU.
    
    Args:
        limit: upper bound for sieving
        num_classes: number of admissible classes to process (-1 = all)
    """
    # ── Setup ──
    t0 = time.time()
    print(f"P₉ = {P9:,}")
    print(f"Computing admissible residues...")
    
    all_admiss = compute_admissible()
    num_total = len(all_admiss)
    print(f"  Total twin-admissible: {num_total:,} ({100*num_total/P9:.2f}%)")
    
    if num_classes == -1 or num_classes >= num_total:
        classes = all_admiss
        num_classes = num_total
    else:
        import random
        random.seed(42)
        classes = sorted(random.sample(all_admiss, num_classes))
    
    print(f"  Processing {num_classes:,} classes")
    print(f"  Limit: {limit:,}")
    print(f"  GPU: {cuda.get_current_device().name}")
    
    # ── Base primes ──
    sqrt_limit = int(math.isqrt(limit)) + 100
    print(f"  Sieving base primes up to {sqrt_limit:,}...")
    
    is_p = np.ones(sqrt_limit, dtype=bool)
    is_p[:2] = False
    for i in range(2, int(math.isqrt(sqrt_limit)) + 1):
        if is_p[i]:
            is_p[i*i:sqrt_limit:i] = False
    
    base_primes = np.where(is_p)[0]
    # Remove P₉ factors
    base_primes = base_primes[base_primes > 23]
    base_primes_cpu = base_primes.astype(np.int64)
    print(f"  Base primes (> 23): {len(base_primes_cpu):,}")
    
    # Transfer to device
    d_bp = cuda.to_device(base_primes_cpu)
    d_residues = cuda.to_device(np.array(classes, dtype=np.int64))
    d_counts = cuda.device_array(num_classes, dtype=np.int64)
    d_counts.fill(0)
    
    print(f"\nStarting GPU sieve... ({time.time()-t0:.1f}s setup)")
    
    # ── Configure GPU ──
    threads_per_block = 256
    # Launch one block per class
    # But we can't launch 8M blocks at once. Process in batches.
    batch_size = 10000  # 10K classes per GPU launch
    n_batches = (num_classes + batch_size - 1) // batch_size
    
    t1 = time.time()
    grand_total = 0
    
    for b in range(n_batches):
        start = b * batch_size
        end = min(start + batch_size, num_classes)
        batch_n = end - start
        
        # Kernel launch
        sieve_theta_kernel[(batch_n, 1), (threads_per_block, 1, 1)](
            b, d_residues, d_counts, d_bp, limit, P9
        )
        cuda.synchronize()
        
        # Get results for this batch
        batch_counts = d_counts[start:end].copy_to_host()
        batch_twins = int(np.sum(batch_counts))
        grand_total += batch_twins
        
        elapsed = time.time() - t1
        pct = 100 * (b + 1) / n_batches
        eta = (elapsed / pct * 100 - elapsed) if pct > 0 else 0
        print(f"  Batch {b+1}/{n_batches} ({pct:.1f}%) | "
              f"Classes: {start:,}-{end:,} | Twins: {grand_total:,} | "
              f"Batch time: {elapsed:.1f}s | ETA: {eta:.0f}s")
    
    total_time = time.time() - t0
    print(f"\n{'='*50}")
    print(f"  n=9 Theta Sieve Complete (GPU)")
    print(f"{'='*50}")
    print(f"  Classes processed: {num_classes:,}")
    print(f"  Limit: {limit:,}")
    print(f"  Total twins: {grand_total:,}")
    print(f"  Total time: {total_time:.1f}s")
    
    return classes, grand_total, d_counts


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000_000_000
    classes = int(sys.argv[2]) if len(sys.argv) > 2 else -1
    run_n9_theta_cuda(limit=limit, num_classes=classes)
