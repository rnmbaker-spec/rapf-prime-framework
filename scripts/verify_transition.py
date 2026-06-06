import math
import numpy as np
from tqdm import tqdm

def is_prime(n):
    """Check if a number is prime"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def generate_primes(limit):
    """Generate all primes up to given limit using Sieve of Eratosthenes"""
    sieve = [True] * (limit + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(math.sqrt(limit)) + 1):
        if sieve[i]:
            sieve[i*i : limit+1 : i] = [False]*len(range(i*i, limit+1, i))
    return [i for i, is_prime in enumerate(sieve) if is_prime]

def count_small_prime_factors(n, primes, S):
    """Count distinct prime factors of n that are ≤ S"""
    count = 0
    for p in primes:
        if p > S:
            break
        if n % p == 0:
            count += 1
    return count

def compute_score_marg(omega, S):
    """Compute the margin score using polynomial inclusion-exclusion"""
    score = 0.0
    sign = -1
    for j in range(3, omega + 1):
        comb = math.comb(omega, j)
        term = comb / (S ** j)
        score += sign * term
        sign *= -1  # Alternate signs
    return score

def main():
    # Test parameters
    X = 140000000  # 140M
    alpha = math.log(X)
    S = (math.log(X) / 3) ** 3  # ~218 as calculated in verification plan
    h_range = int(math.log(X))  # 1 to log(X)
    
    print(f"Verification Parameters:")
    print(f"X = {X}")
    print(f"α(X) = {alpha:.2f}")
    print(f"S(X) = {S:.2f}")
    print(f"h range = 1 to {h_range}")
    print(f"Protocol tolerance = 1/log X = {1/math.log(X):.4f}")
    print(f"Margin error bound = 5000/(log X)^6 = {5000/(math.log(X)**6):.6f}")
    print("\nCalculating...")

    # Generate primes up to S(X)
    primes = generate_primes(int(S) + 1)
    
    results = []
    
    # Check candidates X ± h
    for direction in [-1, 1]:
        for h in tqdm(range(1, h_range + 1)):
            n = X + direction * h
            if n <= 0:
                continue
                
            # Calculate ω_S(n)
            omega = count_small_prime_factors(n, primes, S)
            
            # Compute Score_marg(u) = Σ_{j≥3} (-1)^j * C(ω,j)/S^j
            score_marg = compute_score_marg(omega, S)
            
            # Compute envelope bound
            y = omega / S
            env_bound = math.exp(y) * y**3 / 6
            
            results.append({
                'n': n,
                'h': h,
                'direction': direction,
                'omega': omega,
                'score_marg': score_marg,
                'env_bound': env_bound
            })

    # Analyze results
    print("\nVerification Results:")
    max_score_marg = max(abs(r['score_marg']) for r in results)
    max_env_bound = max(r['env_bound'] for r in results)
    
    print(f"Maximum |Score_marg(u)| over tested candidates: {max_score_marg:.6f}")
    print(f"Maximum envelope bound over tested candidates: {max_env_bound:.6f}")
    print(f"Theoretical bound: {5000/(math.log(X)**6):.6f}")
    print(f"Protocol tolerance: {1/math.log(X):.4f}")
    
    # Verify all margin scores are within protocol tolerance
    all_in_bound = all(abs(r['score_marg']) <= 5000/(math.log(X)**6) for r in results)
    print(f"\nAll margin errors within theoretical bound: {'✓ Yes' if all_in_bound else '✗ No'}")
    
    # Find maximum error
    worst_case = max(results, key=lambda x: abs(x['score_marg']))
    print(f"\nWorst margin error: {abs(worst_case['score_marg']):.6f}")
    print(f"At n = {worst_case['n']} = X {worst_case['direction']} {worst_case['h']}")
    print(f"ω_S(n) = {worst_case['omega']}")
    
    # Save results to file
    import json
    with open('/home/rebecca/topics/math-research/transition_verification/results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()