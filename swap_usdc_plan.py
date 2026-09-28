#!/usr/bin/env python3
import sys, json
from pathlib import Path

STORE = Path("/Users/liran/.operate/services/sc-2a300821-b4eb-498c-aed6-5deea3b2bcfc/persistent_data")
sys.path.insert(0, str(STORE / ".claude/skills/connect-polymarket/scripts"))
sys.path.insert(0, str(STORE / ".claude/lib"))

import pm_common as pm
import uniswap
import router
import evm

cs = pm.ConnectSigner.from_workspace(STORE)
safe = cs.safe_address
w3 = cs.w3

token_in = pm.USDC      # native USDC 0x3c499...
token_out = pm.USDC_E   # bridged USDC.e 0x2791...

amount = evm.to_base_units(w3, token_in, 5.0)   # 5 USDC -> base units
print("safe:", safe)
print("token_in (native USDC):", token_in)
print("token_out (USDC.e):", token_out)
print("amount base units:", amount)

candidates = uniswap.discover(w3, 137, token_in, token_out)
print("candidate pools:", len(candidates))
for c in candidates:
    print("  pool:", c)

pool, quoted = uniswap.best_route(w3, 137, token_in, token_out, amount, candidates)
print("best pool:", pool)
print("quoted out (base units):", quoted, "=", quoted/1e6, "USDC.e")

minimum = evm.apply_slippage(quoted, 0.005)   # 0.5% slippage
print("minimum out:", minimum, "=", minimum/1e6, "USDC.e")

routed = router.router_swap(
    w3, cs, safe, 137, pool, token_in, token_out, amount, minimum,
    separate_approvals=True,
)
print("num calls:", len(routed.calls))
for i, c in enumerate(routed.calls):
    print(f"  call[{i}] {c['what']}: to={c['to']} data_len={len(c['data'])} value={c.get('value',0)}")
print("permit label:", routed.permit)
print("deadline:", routed.deadline)
