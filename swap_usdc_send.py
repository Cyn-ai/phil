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
amount = evm.to_base_units(w3, token_in, 5.0)

candidates = uniswap.discover(w3, 137, token_in, token_out)
pool, quoted = uniswap.best_route(w3, 137, token_in, token_out, amount, candidates)
minimum = evm.apply_slippage(quoted, 0.005)

print(f"swap 5.0 USDC -> ~{quoted/1e6:.6f} USDC.e (min {minimum/1e6:.6f}) via pool fee={pool.get('fee')}")
routed = router.router_swap(
    w3, cs, safe, 137, pool, token_in, token_out, amount, minimum,
    separate_approvals=True,
)

for i, c in enumerate(routed.calls):
    label = c["what"]
    print(f"[{i+1}/{len(routed.calls)}] {label} ...", flush=True)
    tx_hash = cs.safe_transaction(c["to"], c["data"], value=int(c.get("value", 0)))
    print(f"    tx {tx_hash}", flush=True)
    rc = cs.wait_receipt(tx_hash, timeout=300)
    if rc["status"] != 1:
        print(f"    !! receipt status={rc['status']} — STOPPING before next call")
        sys.exit(1)
    print(f"    confirmed", flush=True)

print("ALL CALLS CONFIRMED")
# verify final balances
usdc_bal = pm.erc20_balance_of(w3, token_in, safe) / 1e6
usdce_bal = pm.erc20_balance_of(w3, token_out, safe) / 1e6
print(f"safe native USDC: {usdc_bal}")
print(f"safe USDC.e:      {usdce_bal}")
