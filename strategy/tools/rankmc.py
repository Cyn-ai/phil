"""Monte Carlo finishing-position probabilities for a multi-candidate race.

Usage: python3 strategy/tools/rankmc.py --cand NAME:MEAN:BLOC ... \
         [--bloc-sd 3.0] [--bloc-shift BLOC:MEAN ...] [--cand-sd 2.0] [--n 200000]

Each candidate's share = MEAN + bloc swing (shared within a bloc, N(shift, bloc_sd))
+ idiosyncratic N(0, cand_sd). Prints P(finish position k) per candidate.
Inputs are poll means you must source in the forecast note; the sds are
assumptions and should be stated there too (unvalidated-method until graded).
"""
import argparse
import random


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", action="append", required=True)
    ap.add_argument("--bloc-sd", type=float, default=3.0)
    ap.add_argument("--bloc-shift", action="append", default=[])
    ap.add_argument("--cand-sd", type=float, default=2.0)
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    random.seed(a.seed)
    cands = []
    for c in a.cand:
        name, mean, bloc = c.split(":")
        cands.append((name, float(mean), bloc))
    shifts = {}
    for s in a.bloc_shift:
        b, m = s.split(":")
        shifts[b] = float(m)
    blocs = sorted({c[2] for c in cands})
    k = len(cands)
    counts = {c[0]: [0] * k for c in cands}
    for _ in range(a.n):
        sw = {b: random.gauss(shifts.get(b, 0.0), a.bloc_sd) for b in blocs}
        vals = [(m + sw[b] + random.gauss(0, a.cand_sd), name) for name, m, b in cands]
        vals.sort(reverse=True)
        for pos, (_, name) in enumerate(vals):
            counts[name][pos] += 1
    for name, _, _ in cands:
        ps = " ".join(f"p{i + 1}={counts[name][i] / a.n:.3f}" for i in range(min(k, 4)))
        print(f"{name:12s} {ps}")


if __name__ == "__main__":
    main()
