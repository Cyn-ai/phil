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

token_in = pm.USDC
token_out = pm.USDC_E

# current balances
usdc = pm.erc20_balance_of(w3, token_in, safe) / 1e6
usdce = pm.erc20_balance_of(w3, token_out, safe) / 1e6
print(f"BEFORE: safe native USDC={usdc}  USDC.e={usdce}")

amount = evm.to_base_units(w3, token_in, usdc)   # swap the whole native USDC balance

candidates = uniswap.discover(w3, 137, token_in, token_out)
# prefer v3 (most battle-tested); fall back to v2; skip v4
v3 = [c for c in candidates if c.get("version") == "v3"]
v2 = [c for c in candidates if c.get("version") == "v2"]
chosen = v3 if v3 else v2
print("candidates v3:", [c.get("address") for c in v3])
print("candidates v2:", [c.get("address") for c in v2])

pool, quoted = uniswap.best_route(w3, 137, token_in, token_out, amount, chosen)
print("chosen pool:", pool.get("version"), "fee", pool.get("fee"), pool.get("address"))
print(f"quoted out: {quoted/1e6:.6f} USDC.e")

minimum = evm.apply_slippage(quoted, 0.005)
routed = router.router_swap(
    w3, cs, safe, 137, pool, token_in, token_out, amount, minimum,
    separate_approvals=True,
)
print(f"{len(routed.calls)} calls: " + ", ".join(c['what'] for c in routed.calls))

for i, c in enumerate(routed.calls):
    print(f"[{i+1}/{len(routed.calls)}] {c['what']} ...", flush=True)
    tx_hash = cs.safe_transaction(c["to"], c["data"], value=int(c.get("value", 0)))
    print(f"    tx {tx_hash}", flush=True)
    rc = cs.wait_receipt(tx_hash, timeout=300)
    if rc["status"] != 1:
        print(f"    !! receipt status={rc['status']} — STOPPING")
        sys.exit(1)
    print(f"    confirmed", flush=True)

print("ALL CALLS CONFIRMED")
usdc = pm.erc20_balance_of(w3, token_in, safe) / 1e6
usdce = pm.erc20_balance_of(w3, token_out, safe) / 1e6
print(f"AFTER: safe native USDC={usdc}  USDC.e={usdce}")
