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
        for name, tok in pmapi.market_tokens(m).items():
            print("  ", name, tok, "bid/ask", pmapi.best_prices(tok))
        print("  desc:", (m.get("description") or "").replace("\n", " "))


if __name__ == "__main__":
    main(sys.argv[1:])
