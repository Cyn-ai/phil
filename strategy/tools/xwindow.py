"""Rolling-window bootstrap for xtracker post-count brackets near period end.

Usage: python3 strategy/tools/xwindow.py <hourly.txt> <hours_remaining> <current_count> <lo-hi> [<lo-hi> ...]
hourly.txt: whitespace-separated hourly counts for the period so far, oldest first,
COMPLETE hours only (drop the running hour; pass its count inside current_count).

For each bracket prints the share of all rolling windows of the remaining length
whose post count lands the final total inside the bracket (playbook: unshaded
bootstrap, all windows when aligned n < 20). Added 2026-10-02 for the Musk
Sep 25 - Oct 2 weekly; xtracker_boot no longer exists in this repo.

Optional --aligned <series_start_utc_hour> <window_start_utc_hour> also prints the
same table over only the windows starting at the same UTC clock hour as the
remaining window (RETRO-20261003-2226: Musk Oct 1-3, all-windows mean ~16 for
04-16Z, actual 9).
"""
import sys

args = sys.argv[1:]
aligned = None
if "--aligned" in args:
    k = args.index("--aligned")
    aligned = (int(args[k + 1]), int(args[k + 2]))
    del args[k:k + 3]
hours = int(args[1])
cur = int(args[2])
brackets = []
for b in args[3:]:
    lo, hi = b.split("-")
    brackets.append((int(lo), int(hi) if hi else 10**9, b))
with open(args[0]) as f:
    series = [int(x) for x in f.read().split()]
starts = range(len(series) - hours + 1)


def table(label, idx):
    wins = [sum(series[i:i + hours]) for i in idx]
    if not wins:
        print(f"{label}: no windows")
        return
    print(f"{label} windows n={len(wins)} len={hours}h min={min(wins)} max={max(wins)} "
          f"mean={sum(wins) / len(wins):.1f}")
    for lo, hi, name in brackets:
        p = sum(1 for w in wins if lo <= cur + w <= hi) / len(wins)
        print(f"{name}: {p:.3f}")


table("all", starts)
if aligned:
    h0, w0 = aligned
    table(f"aligned@{w0:02d}Z", [i for i in starts if (h0 + i) % 24 == w0])
