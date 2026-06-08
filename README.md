# The Recursive Admissibility Prime Framework (RAPF)

Research program investigating prime admissibility, twin prime density, and primorial-level equidistribution through a recursive polynomial certificate framework.

## Overview

This repository contains the computational tools and papers for the RAPF research program, consisting of three interconnected papers:

1. **Discrete Geometry & Twin Prime Admissibility** — Structural theory of admissible classes
2. **Recursive Polynomial Certificates** — Computational engine for verifying admissibility
3. **Primorial Equidistribution** — Empirical analysis of prime distributions across moduli

## Repository Structure

```
papers/
  1-discrete-geometry/      Paper 1: Discrete Geometry
  2-polynomial-certificates/ Paper 2: Polynomial Certificates
  3-equidistribution/       Paper 3: Primorial Equidistribution

code/
  basic-sieve/              Standard segmented prime sieves
  recursive-sieve/          Theta/line sieve implementations (GPU-accelerated)
  analysis/                 Statistical analysis tools

data/                       Census results
docs/                       Supplementary materials
```

## Computational Setup

- Hardware: standard 4-core Intel processor (Alder Lake N100)
- Sieve: 1 GB segmented memory buffer
- Total compute: ~95.56 core-hours across n=6,7,8 census

## Usage

```bash
# Basic twin prime sieve (up to 10^9)
python3 code/basic-sieve/sieve_10_9.py

# Theta sieve (GPU-accelerated, up to 10^9)
python3 code/recursive-sieve/theta_sieve_n9_cuda.py
```

## Papers

Each paper compiles standalone with `pdflatex`. Cross-references use plain-text citations to avoid inter-document dependency.

## Citation

@misc{miller2026rapf,
  title={The Recursive Admissibility Prime Framework},
  author={Rob Miller},
  year={2026},
  url={https://github.com/rnmbaker-spec/rapf-prime-framework}
}

## License

Open source — research code shared for reproducibility and collaboration.
