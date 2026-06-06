// n=8 Twin Prime Class Occupancy Sieve
// Interval: [P8, P8^2] where P8 = 2*3*5*7*11*13*17*19 = 9699690
// Counts twin prime pairs per admissible residue class mod P8
// Compile: g++ -O3 -fopenmp -march=native -o n8_twin_sieve n8_twin_sieve.cpp
// Run:     ./n8_twin_sieve

#include <bits/stdc++.h>
#include <omp.h>
using namespace std;

static const uint64_t P8 = 9699690ULL;           // 2*3*5*7*11*13*17*19
static const uint64_t P8_SQ = 94083986096100ULL; // P8^2
static const uint32_t A8 = 378675;               // prod(p-2) for p in [3,5,7,11,13,17,19]

// Odds-only segmented sieve for one segment
// Returns per-class counts for this segment
vector<uint32_t> sieve_segment(
    uint64_t seg_low, uint64_t seg_high,
    const vector<uint32_t>& odd_primes
) {
    // We only care about odd numbers in [seg_low, seg_high)
    uint64_t first_odd = (seg_low & 1ULL) ? seg_low : seg_low + 1;
    if (first_odd >= seg_high) return vector<uint32_t>(A8, 0);

    uint64_t num_odds = (seg_high - first_odd + 1) / 2;
    uint64_t num_words = (num_odds + 63) / 64;

    // Bit-packed sieve: bit i = 1 means first_odd + 2*i is prime candidate
    vector<uint64_t> sieve(num_words, ~0ULL);

    // Mark composites for each odd prime
    for (uint32_t p : odd_primes) {
        uint64_t p_sq = (uint64_t)p * p;
        if (p_sq >= seg_high) break;

        // First multiple of p >= seg_low
        uint64_t start = ((seg_low + p - 1) / p) * p;
        if (start < p_sq) start = p_sq;
        if ((start & 1ULL) == 0) start += p; // make odd

        if (start >= seg_high) continue;

        // Bit index of start in odd representation
        uint64_t bit_idx = (start - first_odd) / 2;

        // Mark every p-th bit (step of p in odd index = step of 2p in actual numbers)
        for (uint64_t b = bit_idx; b < num_odds; b += p) {
            sieve[b >> 6] &= ~(1ULL << (b & 63));
        }
    }

    // Also need to ensure 1 is not marked prime (only for first segment)
    if (seg_low <= 1 && first_odd == 1) {
        sieve[0] &= ~1ULL;
    }

    // Count twins per class
    vector<uint32_t> local_counts(A8, 0);

    // Fast class lookup: we need p % P8 for each twin
    // Precompute class index for each residue
    static vector<int> class_lookup;
    static vector<uint32_t> admissible_residues;
    static once_flag init_flag;
    call_once(init_flag, []() {
        class_lookup.resize(P8, -1);
        admissible_residues.reserve(A8);
        for (uint64_t r = 0; r < P8; r++) {
            bool ok = true;
            // Twin {0,2}: r must be odd, r mod p != 0, (r+2) mod p != 0
            if ((r & 1ULL) == 0) { ok = false; }
            else {
                uint64_t rr = r;
                for (uint32_t p : {3u, 5u, 7u, 11u, 13u, 17u, 19u}) {
                    if (rr % p == 0 || (rr + 2) % p == 0) { ok = false; break; }
                }
            }
            if (ok) {
                class_lookup[r] = (int)admissible_residues.size();
                admissible_residues.push_back((uint32_t)r);
            }
        }
    });

    // Scan for twins: consecutive set bits in odd representation
    for (uint64_t w = 0; w < num_words; w++) {
        uint64_t word = sieve[w];
        if (word == 0) continue;

        uint64_t next_word = (w + 1 < num_words) ? sieve[w + 1] : 0;

        // Twins fully within this word: bit i and bit i+1 both set
        // word & (word >> 1) has bit i set iff bit i and bit i-1 both set
        // So set bits mark the SECOND prime of each twin; first prime is at i-1
        uint64_t twin_mask = word & (word >> 1);

        // Also check boundary: bit 63 of this word and bit 0 of next word
        if ((word >> 63) & (next_word & 1ULL)) {
            uint64_t p = first_odd + 2 * (64 * w + 63);
            if (p >= seg_low && p + 2 < seg_high) {
                int cls = class_lookup[p % P8];
                if (cls >= 0) local_counts[cls]++;
            }
        }

        while (twin_mask) {
            int b = __builtin_ctzll(twin_mask);
            uint64_t p = first_odd + 2 * (64 * w + b);
            if (p >= seg_low && p + 2 < seg_high) {
                int cls = class_lookup[p % P8];
                if (cls >= 0) local_counts[cls]++;
            }
            twin_mask &= twin_mask - 1;
        }
    }

    return local_counts;
}

int main(int argc, char** argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    const uint64_t SEG_SIZE = 500000000ULL; // 500M numbers per segment
    uint64_t num_segments = (P8_SQ - P8 + SEG_SIZE - 1) / SEG_SIZE;

    cout << "=== n=8 Twin Prime Class Sieve ===" << endl;
    cout << "P8 = " << P8 << endl;
    cout << "Interval: [" << P8 << ", " << P8_SQ << "]" << endl;
    cout << "Interval size: " << (P8_SQ - P8) << " (" << (P8_SQ - P8) / 1e12 << " trillion)" << endl;
    cout << "Admissible classes: " << A8 << endl;
    cout << "Segment size: " << SEG_SIZE << endl;
    cout << "Number of segments: " << num_segments << endl;
    cout << "Threads: " << omp_get_max_threads() << endl;
    cout << endl;

    // Generate small odd primes up to P8
    cout << "Generating small primes up to P8..." << flush;
    auto t0 = chrono::steady_clock::now();

    int sieve_limit = (int)P8;
    vector<char> is_prime(sieve_limit + 1, true);
    is_prime[0] = is_prime[1] = false;
    for (int i = 2; i * i <= sieve_limit; i++) {
        if (is_prime[i]) {
            for (long long j = 1LL * i * i; j <= sieve_limit; j += i)
                is_prime[(size_t)j] = false;
        }
    }

    vector<uint32_t> odd_primes;
    for (int i = 3; i <= sieve_limit; i += 2) {
        if (is_prime[i]) odd_primes.push_back(i);
    }

    auto t1 = chrono::steady_clock::now();
    cout << " " << odd_primes.size() << " odd primes in "
         << chrono::duration<double>(t1 - t0).count() << "s" << endl;

    // Global class counts
    vector<atomic<uint32_t>> global_counts(A8);
    for (auto& c : global_counts) c = 0;
    atomic<uint64_t> total_twins{0};

    // Progress tracking
    atomic<uint64_t> completed_segments{0};
    atomic<uint64_t> last_reported{0};

    cout << "\nStarting sieve..." << endl;
    auto t_start = chrono::steady_clock::now();

    #pragma omp parallel for schedule(dynamic, 1)
    for (uint64_t seg_idx = 0; seg_idx < num_segments; seg_idx++) {
        uint64_t seg_low = P8 + seg_idx * SEG_SIZE;
        uint64_t seg_high = min(seg_low + SEG_SIZE, P8_SQ + 1);

        auto local = sieve_segment(seg_low, seg_high, odd_primes);

        uint64_t seg_twins = 0;
        for (uint32_t i = 0; i < A8; i++) {
            if (local[i] > 0) {
                global_counts[i] += local[i];
                seg_twins += local[i];
            }
        }
        total_twins += seg_twins;

        uint64_t done = ++completed_segments;

        // Report every 1% or every 100 segments
        uint64_t report_every = max(num_segments / 100, (uint64_t)100);
        if (done >= last_reported + report_every) {
            uint64_t prev = last_reported.exchange(done);
            if (prev != done) { // only one thread reports
                auto now = chrono::steady_clock::now();
                double elapsed = chrono::duration<double>(now - t_start).count();
                double pct = 100.0 * done / num_segments;
                double rate = done / max(elapsed, 0.001);
                double eta = (num_segments - done) / max(rate, 0.001);

                // Find current min class
                uint32_t min_c = UINT32_MAX;
                for (const auto& c : global_counts) {
                    uint32_t val = c.load();
                    if (val < min_c) min_c = val;
                }

                cout << fixed << setprecision(1);
                cout << "  " << done << "/" << num_segments
                     << " (" << pct << "%) | twins: " << total_twins.load()
                     << " | min_class: " << min_c
                     << " | rate: " << rate << " seg/s"
                     << " | ETA: " << (eta / 3600.0) << "h" << endl;
            }
        }
    }

    auto t_end = chrono::steady_clock::now();
    double elapsed_total = chrono::duration<double>(t_end - t_start).count();

    // Compute statistics
    vector<uint32_t> counts(A8);
    uint64_t total = 0;
    uint32_t min_c = UINT32_MAX, max_c = 0;
    for (uint32_t i = 0; i < A8; i++) {
        counts[i] = global_counts[i].load();
        total += counts[i];
        if (counts[i] < min_c) min_c = counts[i];
        if (counts[i] > max_c) max_c = counts[i];
    }

    double mean = (double)total / A8;
    double variance = 0;
    for (uint32_t c : counts) {
        variance += ((double)c - mean) * ((double)c - mean);
    }
    variance /= A8;
    double cv = sqrt(variance) / mean * 100.0;
    double m_avg = (double)min_c / mean;

    uint32_t empties = 0;
    for (uint32_t c : counts) if (c == 0) empties++;

    cout << "\n" << string(60, '=') << endl;
    cout << "COMPLETE!" << endl;
    cout << "Elapsed: " << elapsed_total / 3600.0 << " hours" << endl;
    cout << "Total twin pairs: " << total << endl;
    cout << "Admissible classes: " << A8 << endl;
    cout << "Min class: " << min_c << endl;
    cout << "Max class: " << max_c << endl;
    cout << "Mean per class: " << mean << endl;
    cout << "CV: " << cv << "%" << endl;
    cout << "m(8)/Avg: " << m_avg << endl;
    cout << "Empty classes: " << empties << endl;
    cout << string(60, '=') << endl;

    // Save results
    string outpath = "/home/rebecca/n8_results.json";
    ofstream fout(outpath);
    fout << "{\n";
    fout << "  \"n\": 8,\n";
    fout << "  \"P8\": " << P8 << ",\n";
    fout << "  \"interval_start\": " << P8 << ",\n";
    fout << "  \"interval_end\": " << P8_SQ << ",\n";
    fout << "  \"total_twins\": " << total << ",\n";
    fout << "  \"admissible_classes\": " << A8 << ",\n";
    fout << "  \"min_class\": " << min_c << ",\n";
    fout << "  \"max_class\": " << max_c << ",\n";
    fout << "  \"mean_per_class\": " << mean << ",\n";
    fout << "  \"cv_percent\": " << cv << ",\n";
    fout << "  \"m_avg_ratio\": " << m_avg << ",\n";
    fout << "  \"empty_classes\": " << empties << ",\n";
    fout << "  \"elapsed_seconds\": " << elapsed_total << "\n";
    fout << "}\n";
    fout.close();
    cout << "Results saved to " << outpath << endl;

    return 0;
}
