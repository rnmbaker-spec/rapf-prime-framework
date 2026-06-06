# RAPF v5.0 Supplement — 2026-06-02

## Bombieri-Vinogradov for Primorial Moduli: Literature Survey

### Context
From the June 1 session: we identified three paths to actually **prove** the twin prime conjecture (not just quantify the cost of failure). Path #3 — **Bombieri-Vinogradov for primorial moduli** — was new territory. This note surveys the existing literature and identifies where primorials fit.

---

### The Core Problem

Classical **Bombieri-Vinogradov** (1965):
$$\sum_{q \leq Q} \max_{y \leq x} \max_{(a,q)=1} \left|\psi(y;q,a) - \frac{y}{\phi(q)}\right| \ll_A \frac{x}{(\log x)^A}$$
for $Q \leq x^{1/2}(\log x)^{-B}$.

This averages over **all** moduli $q \leq Q$. We need control for $q = P_n$ (the primorials) specifically — a sequence of only $\sim \log\log x$ moduli up to $x$.

---

### Key Papers Found

#### 1. Baier & Zhao (2006) — "Bombieri-Vinogradov Type Theorems for Sparse Sets of Moduli"
- **Published**: Acta Arithmetica 125(2), 187-201
- **arXiv**: math/0602116
- **Main result**: BV-type bounds for "well-distributed" sparse sets $S$
- **Critical condition**: $|S(Q)| \gg Q^{3/4}$ in dyadic intervals
- **Problem for primorials**: Primorials grow exponentially $P_n \sim e^n$, so in any dyadic interval $[Q, 2Q]$ there are typically only $O(1)$ primorials. This fails the $Q^{3/4}$ density requirement by a huge margin.
- **Conclusion**: The Baier-Zhao theorem does **not directly apply** to primorials — they're too sparse even for sparse-set theorems.

#### 2. Baker (2012, 2017) — "Primes in APs to Spaced Moduli" I, II, III
- **Published**: Acta Arithmetica 153(2012), 179(2017)
- **Focus**: Polynomial sets $S_f = \{f(k) : k \in \mathbb{N}\}$, $\deg f \geq 2$
- **Best exponent**: $Q < x^{9/20}$ for general polynomial sets, $Q < x^{1/2}$ for prime squares
- **Problem for primorials**: This framework handles sets where $f(k)$ produces polynomially-spaced moduli. Primorials grow *super-exponentially* in $k$, so no polynomial $f$ captures them.

#### 3. Corrigan (2023) — "BV Theorem with Monomial Moduli"
- **Focus**: Moduli $q^k$ for $k \geq 3$
- **Extends** Baier-Zhao's square-moduli approach
- **Not directly applicable** to primorials

#### 4. Maynard (2020) — "Primes in APs to Large Moduli III: Uniform Residue Classes"
- **arXiv**: 2006.08250
- **Breakthrough**: Extends BV beyond $x^{1/2}$ barrier to $x^{1/2+\delta}$
- **Key condition**: Moduli must have "conveniently sized divisors"
- **Relevance**: Primorials have **every** divisor up to $p_n$, so they trivially satisfy this
- **But**: This is about pushing the *range* of $Q$ for dense modulus sets, not about sparse sequences

#### 5. MathOverflow Discussion (2021)
- **Question**: Can we get stronger BV estimates with moduli restricted to sets of size $O(\log\log x)$?
- **Answer**: "No, probably not. When you average, you want to average over more things, not less."
- **Assessment**: This dismissive answer is partially correct for the *standard proof technique*, but doesn't rule out a *different* proof approach that exploits the special structure of primorials.

---

### The Structural Advantage of Primorials

Even though primorials are too sparse for existing sparse-set BV theorems, they have **unique structural properties** that might enable a *different* approach:

1. **Full CRT decomposition**: $P_n = p_1 p_2 \cdots p_n$. Every residue class mod $P_n$ decomposes into independent components mod each $p_i$.

2. **Admissible classes are explicit**: A pair $(a, a+2)$ is admissible mod $P_n$ iff $a \not\equiv 0 \pmod p$ and $a \not\equiv -2 \pmod p$ for all $p \leq p_n$. This is a precise set of forbidden residues — exactly $\prod_{p|P_n}(p-2)$ admissible classes.

3. **The error term $E(x; P_n, a)$** for each admissible class $a$ is, in principle, controlled by the large sieve with modulus $P_n$. The key question is whether the *sum* over the $O(\prod(p-2))$ admissible classes can be bounded.

4. **The Vaughan identity decomposition** of $\Lambda(n)$ into Type I/II sums, when averaged over residues mod $P_n$, might exploit the product structure more efficiently than for arbitrary moduli.

---

### The Gap: What We Actually Need

Our **Lemma 2** (from the twin prime framework) requires:

> For $q = P_n$, the primes in $[P_n, P_n^2]$ are approximately equidistributed across the admissible residue classes mod $P_n$, with error term o(1) relative to the main term.

This is weaker than full BV in some ways (we only need it for *one* specific modulus per scale, not an average over many) but harder in others (standard BV gives nothing for a single modulus).

**We need a single-modulus equidistribution theorem for $P_n$**, not an averaged one. This is fundamentally different from the BV paradigm.

---

### Possible Approaches

1. **Zero-density estimates for $L(s, \chi)$ with $\chi \pmod{P_n}$**: If we can show that no exceptional zeros exist near $s=1$ for characters mod $P_n$, we get strong prime number theorems for each admissible class. The product structure of $P_n$ might make this tractable since $\chi \pmod{P_n}$ decomposes as $\chi_1 \cdots \chi_n$ with $\chi_i \pmod{p_i}$.

2. **Siegel-Walfisz for primorials**: SW already gives good bounds for *fixed* moduli. For $P_n$ itself, the modulus grows with $x$, so standard SW fails. But the *structure* of $P_n$ could allow a refinement.

3. **Large sieve with primorial weights**: The large sieve inequality
$$\sum_{q \leq Q} \sum_{\chi \pmod q} \left|\sum_{n \leq N} a_n \chi(n)\right|^2 \leq (N + Q^2)\sum |a_n|^2$$
might be improvable when the characters are restricted to those mod $P_n$ specifically, since these characters factor into products of characters mod small primes.

4. **The "well-factorable" approach of BFI/Maynard**: Maynard uses well-factorable weights to control error terms. The primorial structure is highly factorable — might this connect?

---

### Open Questions for Future Research

1. Does the product structure of $P_n$ allow a zero-free region for $L(s,\chi \pmod{P_n})$ that's better than what's known for arbitrary moduli?
2. Can the large sieve be refined for the specific character group $(\mathbb{Z}/P_n\mathbb{Z})^\times \cong \prod (\mathbb{Z}/p_i\mathbb{Z})^\times$?
3. Is there a connection between the Vaughan identity decomposition and the CRT decomposition of residues mod $P_n$?
4. What is the *actual* size of the error term $E(P_n^2; P_n, a)$ for admissible $a$? Numerical computation could give evidence.

---

### Connection to Rob's Lemma 2

Lemma 2 states that twin primes appear in admissible classes with density proportional to the singular series. If we can prove equidistribution mod $P_n$ (i.e., that each admissible class receives approximately its fair share of primes/prime pairs), then Lemma 2 follows directly from the combinatorics of admissible classes — which we already understand.

**This is why BV-for-primorials is the "direct route" to actually proving twin primes**: it converts our computational framework (class combinatorics + polynomial certificates) into rigorous analytic number theory.

---

### File References
- Baier-Zhao PDF: https://arxiv.org/pdf/math/0602116
- Baker (2012): Acta Arith. 153, 133-159
- Baker (2017): Acta Arith. 179, 125-?
- Corrigan (2023): https://web.maths.unsw.edu.au/~ccorrigan/nn002a.pdf
- Maynard (2020): arXiv:2006.08250
