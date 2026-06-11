#!/usr/bin/env python3
"""
triplet_census_mt.py — Multi-core segmented census of prime triplet admissible classes.

Launches N subprocesses (taskset-pinned to separate cores), each sieving
a chunk of [Pn, Pn^2 + 7]. Counts triplets only by pivot within the
chunk to avoid double-counting. Segment-level overlap handles internal
boundaries; the +7 buffer at each chunk end handles cross-chunk triplets.

Usage:
    python3 triplet_census_mt.py --n 7 [--threads 3] [--output results.json]
"""

import math, time, json, argparse, subprocess, os, sys, statistics

def compute_primorial_and_primes(n):
    primes, p, Pn = [], 2, 1
    while len(primes) < n:
        is_prime = all(p % q != 0 for q in primes if q * q <= p) if primes else True
        if is_prime:
            primes.append(p)
            Pn *= p
        p += 1
    return Pn, primes

WORKER_CODE = r"""
import json, math, time, sys

def sieve_chunk(chunk_start, chunk_end, sieve_end, Pn, base_primes,
                res2idx_A, res2idx_B, start, limit, segment_size):
    '''
    Sieve [chunk_start, sieve_end) counting triplets with pivot in [chunk_start, chunk_end).
    sieve_end >= chunk_end (typically chunk_end + 7) to catch cross-boundary triplets.
    '''
    overlap = 6
    len_A = len(res2idx_A)
    len_B = len(res2idx_B)
    counts_A = [0] * len_A
    counts_B = [0] * len_B
    total_A = total_B = total_primes = 0
    overlap_primes = []
    seg_start = chunk_start
    n_segs = max(1, (sieve_end - chunk_start + segment_size - 1) // segment_size)
    seg_idx = 0

    while seg_start < sieve_end:
        seg_end = min(seg_start + segment_size, sieve_end)
        seg_len = seg_end - seg_start
        seg = bytearray([True]) * seg_len

        for p in base_primes:
            start_mark = max(p * p, ((seg_start + p - 1) // p) * p)
            offset = start_mark - seg_start
            if offset < seg_len:
                seg[offset:seg_len:p] = bytearray(
                    [False] * ((seg_len - 1 - offset) // p + 1))

        seg_primes = [seg_start + i for i, b in enumerate(seg) if b]
        total_primes += len(seg_primes)

        # Internal segment overlap
        candidates = [pp for pp in overlap_primes if pp >= seg_start - overlap] + seg_primes
        candidate_set = set(candidates)

        for p in candidates:
            if p + 6 > limit:
                break
            # Only count if pivot is in this chunk's counting range
            if p < chunk_start or p >= chunk_end:
                continue
            if (p + 2) in candidate_set and (p + 6) in candidate_set:
                r = p % Pn
                if r in res2idx_A:
                    counts_A[res2idx_A[r]] += 1
                    total_A += 1
            if (p + 4) in candidate_set and (p + 6) in candidate_set:
                r = p % Pn
                if r in res2idx_B:
                    counts_B[res2idx_B[r]] += 1
                    total_B += 1

        overlap_primes = [pp for pp in seg_primes if pp > seg_end - overlap - 1]
        seg_start = seg_end
        seg_idx += 1
        if seg_idx % max(1, n_segs // 10) == 0:
            pct = min(100, (min(seg_end, sieve_end) - chunk_start) / (sieve_end - chunk_start) * 100)
            print(f"  {pct:5.1f}%: A={total_A:,}, B={total_B:,}, {time.time()-t0:.0f}s", flush=True)

    return counts_A, counts_B, total_A, total_B, total_primes

with open(sys.argv[1], 'r') as f:
    cfg = json.load(f)

# Reconstruct dicts from list-of-tuples and convert string keys back to ints
cfg['res2idx_A'] = {int(k): v for k, v in cfg['res2idx_A']}
cfg['res2idx_B'] = {int(k): v for k, v in cfg['res2idx_B']}

t0 = time.time()
# sieve_end includes +7 buffer, counting only up to chunk_end
sieve_end = min(cfg['chunk_end'] + 7, cfg['limit'])
ca, cb, ta, tb, tp = sieve_chunk(
    cfg['chunk_start'], cfg['chunk_end'], sieve_end,
    cfg['Pn'], cfg['base_primes'],
    cfg['res2idx_A'], cfg['res2idx_B'],
    cfg['start'], cfg['limit'], cfg.get('segment_size', 1 << 24)
)
elapsed = time.time() - t0

result = {
    'counts_A': ca, 'counts_B': cb, 'total_A': ta, 'total_B': tb,
    'total_primes': tp, 'elapsed': round(elapsed, 1),
    'chunk_start': cfg['chunk_start'], 'chunk_end': cfg['chunk_end']
}
with open(sys.argv[2], 'w') as f:
    json.dump(result, f)
print(f"  DONE: A={ta:,}, B={tb:,} in {elapsed:.0f}s", flush=True)
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--threads", type=int, default=3)
    parser.add_argument("--segment-size", type=int, default=1 << 24)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--workdir", type=str, default=None)
    args = parser.parse_args()

    n_threads = min(args.threads, 3)
    if args.workdir:
        os.chdir(args.workdir)

    Pn, primes = compute_primorial_and_primes(args.n)
    limit = Pn * Pn
    start = Pn
    sqrt_lim = int(math.isqrt(limit))

    print(f"n={args.n}, P_n={Pn:,}, P_n^2={limit:,}")
    print(f"Range: [{start:,}, {limit:,}] = {limit - start:,} integers")

    # Pattern A: (p,p+2,p+6)
    Adm_A_list, res2idx_A = [], {}
    for a in range(Pn):
        if all(a % p != 0 and (a+2) % p != 0 and (a+6) % p != 0 for p in primes):
            res2idx_A[a] = len(Adm_A_list)
            Adm_A_list.append(a)

    # Pattern B: (p,p+4,p+6)
    Adm_B_list, res2idx_B = [], {}
    for a in range(Pn):
        if all(a % p != 0 and (a+4) % p != 0 and (a+6) % p != 0 for p in primes):
            res2idx_B[a] = len(Adm_B_list)
            Adm_B_list.append(a)

    print(f"Pattern A (p,p+2,p+6): {len(Adm_A_list)} classes")
    print(f"Pattern B (p,p+4,p+6): {len(Adm_B_list)} classes")

    # Base primes
    t0 = time.time()
    ss = bytearray([True]) * (sqrt_lim + 1)
    ss[0] = ss[1] = False
    for i in range(2, int(math.isqrt(sqrt_lim)) + 1):
        if ss[i]:
            ss[i*i:sqrt_lim+1:i] = bytearray([False] * ((sqrt_lim - i*i) // i + 1))
    base_primes = [i for i, b in enumerate(ss) if b]
    print(f"Base primes: {len(base_primes):,} (to {sqrt_lim:,}) in {time.time()-t0:.0f}s")

    # Split into contiguous chunks
    total_range = limit - start
    chunk_base = total_range // n_threads
    chunks = []
    for tid in range(n_threads):
        c_start = start + tid * chunk_base
        if tid == n_threads - 1:
            c_end = limit
        else:
            c_end = start + (tid + 1) * chunk_base
        chunks.append((tid, c_start, c_end))
        sz = c_end - c_start
        print(f"  T{tid}: [{c_start:,}..{c_end:,}) = {sz:,}")

    # Write worker script
    with open('/tmp/triplet_worker.py', 'w') as f:
        f.write(WORKER_CODE)

    # Launch workers with taskset pinning
    print("\nLaunching workers...")
    t0_global = time.time()
    procs, result_files = [], []
    for tid, c_start, c_end in chunks:
        cfg_path = f'/tmp/triplet_cfg_{tid}.json'
        out_path = f'/tmp/triplet_result_{tid}.json'
        result_files.append(out_path)
        cfg = {
            'Pn': Pn, 'limit': limit, 'start': start,
            'chunk_start': c_start, 'chunk_end': c_end,
            'segment_size': args.segment_size,
            'res2idx_A': list(res2idx_A.items()), 'res2idx_B': list(res2idx_B.items()),
            'base_primes': base_primes,
        }
        with open(cfg_path, 'w') as f:
            json.dump(cfg, f)
        cmd = f'taskset -c {tid} python3 /tmp/triplet_worker.py {cfg_path} {out_path}'
        print(f"  T{tid}: core {tid}, {cmd}")
        procs.append(subprocess.Popen(cmd, shell=True))

    # Wait for all
    print("\nWaiting for workers...")
    for proc in procs:
        proc.wait()

    wall_time = time.time() - t0_global

    # Merge results
    print("\nMerging results...")
    fA = [0] * len(res2idx_A)
    fB = [0] * len(res2idx_B)
    gA = gB = gP = 0
    for out_path in result_files:
        with open(out_path, 'r') as f:
            r = json.load(f)
        print(f"  T({r['chunk_start']:,}-{r['chunk_end']:,}): A={r['total_A']:,}, B={r['total_B']:,}")
        for i in range(len(r['counts_A'])):
            fA[i] += r['counts_A'][i]
        for i in range(len(r['counts_B'])):
            fB[i] += r['counts_B'][i]
        gA += r['total_A']
        gB += r['total_B']
        gP += r['total_primes']

    mA = gA / len(fA) if fA else 0
    mB = gB / len(fB) if fB else 0
    cvA = 100 * statistics.pstdev(fA) / mA if len(fA) > 1 and mA > 0 else 0
    cvB = 100 * statistics.pstdev(fB) / mB if len(fB) > 1 and mB > 0 else 0

    print(f"\n=== DONE in {wall_time:.0f}s ({wall_time/60:.1f} min) ===")
    print(f"Primes scanned: {gP:,}")
    print(f"Pattern A: {gA:,} pairs, mean={mA:.1f}, CV={cvA:.4f}%, "
          f"min={min(fA)}, max={max(fA)}, empty={sum(1 for c in fA if c==0)}")
    print(f"Pattern B: {gB:,} pairs, mean={mB:.1f}, CV={cvB:.4f}%, "
          f"min={min(fB)}, max={max(fB)}, empty={sum(1 for c in fB if c==0)}")

    results = {
        "n": args.n, "P_n": Pn, "limit": limit,
        "range": f"[{start}, {limit}]", "threads": n_threads,
        "elapsed_seconds": round(wall_time, 1),
        "total_primes_scanned": gP,
        "pattern_A": {
            "num_classes": len(Adm_A_list), "admissible_residues": Adm_A_list,
            "counts": fA, "total_pairs": gA, "mean": round(mA, 1),
            "min": min(fA), "max": max(fA), "cv_pct": round(cvA, 4),
            "empty_classes": sum(1 for c in fA if c == 0),
        },
        "pattern_B": {
            "num_classes": len(Adm_B_list), "admissible_residues": Adm_B_list,
            "counts": fB, "total_pairs": gB, "mean": round(mB, 1),
            "min": min(fB), "max": max(fB), "cv_pct": round(cvB, 4),
            "empty_classes": sum(1 for c in fB if c == 0),
        }
    }
    outfile = args.output or f"triplet_census_n{args.n}_mt.json"
    with open(outfile, "w") as f:
        json.dump(results, f)
    print(f"\nSaved to {outfile}")

if __name__ == "__main__":
    main()
