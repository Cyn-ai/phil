"""Rolling-window bootstrap for xtracker post-count brackets near period end.

Usage: python3 strategy/tools/xwindow.py <hourly.txt> <hours_remaining> <current_count> <lo-hi> [<lo-hi> ...]
hourly.txt: whitespace-separated hourly counts for the period so far, oldest first,
COMPLETE hours only (drop the running hour; pass its count inside current_count).

For each bracket prints the share of all rolling windows of the remaining length
whose post count lands the final total inside the bracket (playbook: unshaded
bootstrap, all windows when aligned n < 20). Added 2026-10-02 for the Musk
Sep 25 - Oct 2 weekly; xtracker_boot no longer exists in this repo.
"""
import sys

hours = int(sys.argv[2])
cur = int(sys.argv[3])
brackets = []
for b in sys.argv[4:]:
    lo, hi = b.split("-")
    brackets.append((int(lo), int(hi) if hi else 10**9, b))
with open(sys.argv[1]) as f:
    series = [int(x) for x in f.read().split()]
wins = [sum(series[i:i + hours]) for i in range(len(series) - hours + 1)]
print(f"windows n={len(wins)} len={hours}h min={min(wins)} max={max(wins)} "
      f"mean={sum(wins) / len(wins):.1f}")
for lo, hi, name in brackets:
    p = sum(1 for w in wins if lo <= cur + w <= hi) / len(wins)
    print(f"{name}: {p:.3f}")
