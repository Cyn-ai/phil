"""Settled-forecast dump for retros — AGENT-EDITABLE (strategy/tools/).

Added 2026-10-03 (RETRO-20261003-0350) when one tick settled 29 forecasts
at once and grading needed each row's est / mid / book / note / dBrier side
by side. Read-only over journal/forecasts.jsonl.

usage: python3 strategy/tools/settled.py --since 2026-10-02T11:50:00Z [--note-chars 700]
"""
import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="settled_ts lower bound (ISO Z)")
    ap.add_argument("--note-chars", type=int, default=700)
    a = ap.parse_args()
    tot_a = tot_m = 0.0
    n = 0
    with open("journal/forecasts.jsonl") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    for r in rows:
        if r.get("status") not in ("won", "lost") or r.get("settled_ts", "") <= a.since:
            continue
        y = 1.0 if r["status"] == "won" else 0.0
        e, m = r["est_prob"], r.get("market_prob_at_record")
        ba = (e - y) ** 2
        bm = (m - y) ** 2 if m is not None else float("nan")
        tot_a += ba
        tot_m += bm
        n += 1
        print(f'{r["id"]} rec={r["ts"][:16]} {r["category"]} {r["skip_reason"]} '
              f'est={e} mid={m} book={r.get("best_bid_at_record")}/{r.get("best_ask_at_record")} '
              f'{r["status"].upper()} dB={ba - bm:+.4f} sup={r.get("supersedes")}')
        print("   Q:", r["question"], "| outcome:", r["outcome"])
        print("   N:", (r.get("note") or "")[: a.note_chars])
    if n:
        print(f"n={n} brier_agent={tot_a / n:.4f} brier_market={tot_m / n:.4f} delta={(tot_a - tot_m) / n:+.4f}")


if __name__ == "__main__":
    main()
