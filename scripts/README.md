# RAPF v4.2 — Sieve Scripts

Validated Python scripts for twin prime analysis. All outputs in the paper
were produced by these scripts.

## Primary Sieve: `sieve_twin_primes.py`

The main script that produced all Table 2 results. Memory-efficient
segmented sieve with boundary-correct twin pair detection.

```bash
python3 sieve_twin_primes.py           # Run to 10^9 (~150s, ~55MB RAM)
```

**Validated results:**
| Range | π₂(X) | Status |
|-------|-------|--------|
| 10⁶ | 8,169 | ✓ exact match |
| 10⁷ | 58,980 | ✓ exact match |
| 10⁸ | 440,312 | ✓ exact match |
| 10⁹ | 3,424,506 | ✓ exact match |

**Features:**
- Segmented sieve (4MB segments) — scales beyond available RAM
- Boundary-correct twin pair detection (handles pairs spanning segment boundaries)
- Single-threaded, deterministic output
- Reports λ̂ (mean twin-to-twin gap), λ_HL (Hardy-Littlewood), and convergence ratio
- Verifies all twin-to-twin gaps are multiples of 6

## Legacy: `theta_sieve_original.py`

Original segmented sieve from v4.1 (10^8 only). Kept for reference
and reproducibility of the initial empirical falsification results.
Uses 1MB segments, stores all primes in memory at once.

```bash
python3 theta_sieve_original.py        # Runs to 10^8 only
```

See paper Section 3.1 for discussion of boundary bug fixed in `sieve_twin_primes.py`.

## Supporting Scripts

- **`discrete_fisher.py`** — Computes Fisher information I(λ) = 9/[λ⁴ sinh²(3/λ)]
  and continuous vs. discrete comparisons.
- **`gap_analysis.py`** — Gap distribution analysis, KS/AD tests,
  geometric PMF fitting.
- **`verify_transition.py`** — Transition verification utilities
  from RAPF v2.6→v3.4 continuous model era.

## Extending the Sieve

To extend beyond 10^9, simply edit the `limit` variable in
`sieve_twin_primes.py`. The segmented approach means memory stays
constant (~55MB) regardless of limit — only runtime scales as O(n log log n).

```python
# In sieve_twin_primes.py:
limit = 10**10     # 10 billion (~25 minutes estimated)
limit = 10**11     # 100 billion (~4-5 hours estimated)
```
