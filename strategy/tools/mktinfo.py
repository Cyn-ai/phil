#!/usr/bin/env python3
"""Print gamma market facts plus the live CLOB bid/ask per outcome.

Usage: python3 strategy/tools/mktinfo.py <gamma_id> [<gamma_id> ...]

One call gives what research and mech request_context need: endDate,
resolution rules, liquidity, UMA status, and each outcome's token id with
its best bid/ask (fills happen at the ask, not the scan mid).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "core"))
import pmapi  # noqa: E402


def main(ids):
    for mid in ids:
        m = pmapi.gamma_market(mid)
        print("=====", mid, m.get("question"))
        print("end", m.get("endDate"), "closed", m.get("closed"),
              "liq", m.get("liquidity"), "uma", m.get("umaResolutionStatus"))
        print("  outcomePrices", m.get("outcomePrices"))
        for name, tok in pmapi.market_tokens(m).items():
            # A closed market's CLOB book 404s; still print the rules.
            try:
                quote = pmapi.best_prices(tok)
            except RuntimeError as e:
                quote = f"unavailable ({e.__class__.__name__}: book gone)"
            print("  ", name, tok, "bid/ask", quote)
        print("  desc:", (m.get("description") or "").replace("\n", " "))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    main(args)
