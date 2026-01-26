"""
Auto trading harness using momentum-based portfolio (top-N equal weight).

Default behavior is dry-run: it only prints intended trades.
Use --live to actually place orders (caution: real trades in prod mode).
"""

import argparse
import math
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

from app import (
    DEFAULT_UNIVERSE,
    get_env_config,
    get_or_issue_token,
    fetch_price,
    fetch_balance,
    order_buy,
    order_sell,
)


def as_float(val) -> float:
    try:
        return float(str(val).replace(",", ""))
    except Exception:
        return 0.0


def build_portfolio(env: Dict[str, Any], token: str, universe: List[str], market: str, top_n: int) -> List[Dict[str, Any]]:
    scored = []
    for sym in universe:
        try:
            price_resp = fetch_price(env, token, sym, market)
            out = price_resp.get("output", {})
            change_rate = as_float(out.get("prdy_ctrt"))
            price = as_float(out.get("stck_prpr"))
            scored.append({"symbol": sym, "price": price, "change_rate": change_rate})
        except Exception as e:
            scored.append({"symbol": sym, "price": 0, "change_rate": -1e9, "error": str(e)})
    ranked = sorted(scored, key=lambda x: x.get("change_rate", -1e9), reverse=True)
    return ranked[: top_n]


def parse_holdings(balance: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    holdings_list = balance.get("output1") or []
    holdings = {}
    if isinstance(holdings_list, list):
        for h in holdings_list:
            sym = h.get("pdno")
            if not sym:
                continue
            holdings[sym] = {
                "qty": as_float(h.get("hldg_qty")),
                "avg": as_float(h.get("pchs_avg_pric")),
                "plrt": as_float(h.get("evlu_pfls_rt")),
                "price": as_float(h.get("prpr")),
            }
    return holdings


def parse_totals(balance: Dict[str, Any]) -> Dict[str, float]:
    totals = {}
    block = None
    o2 = balance.get("output2")
    if isinstance(o2, list) and o2:
        block = o2[0]
    elif isinstance(o2, dict):
        block = o2
    if not block:
        return {}
    for k in ["tot_evlu_amt", "evlu_amt_smtl_amt", "pchs_amt_smtl_amt", "dnca_tot_amt", "asst_icdc_erng_rt"]:
        totals[k] = as_float(block.get(k))
    return totals


def compute_orders(targets: List[Dict[str, Any]], holdings: Dict[str, Dict[str, Any]], equity: float) -> List[Dict[str, Any]]:
    orders = []
    if equity <= 0:
        return orders
    top_n = len(targets)
    if top_n == 0:
        return orders
    weight = 1.0 / top_n
    for t in targets:
        sym = t["symbol"]
        price = t.get("price") or 0
        if price <= 0:
            continue
        desired_value = equity * weight
        desired_qty = math.floor(desired_value / price)
        current_qty = holdings.get(sym, {}).get("qty", 0)
        diff = desired_qty - current_qty
        if diff == 0:
            continue
        side = "buy" if diff > 0 else "sell"
        orders.append({"symbol": sym, "side": side, "qty": abs(int(diff)), "price": price})
    # Sell positions not in targets
    target_syms = {t["symbol"] for t in targets}
    for sym, h in holdings.items():
        if sym not in target_syms and h.get("qty", 0) > 0:
            orders.append({"symbol": sym, "side": "sell", "qty": int(h["qty"]), "price": h.get("price", 0)})
    return orders


def run(args: argparse.Namespace) -> None:
    load_dotenv()
    env = get_env_config(args.mode)
    token = get_or_issue_token(env, args.mode)
    if not token:
        raise RuntimeError("Failed to obtain token")

    universe = DEFAULT_UNIVERSE if not args.universe else [s.strip() for s in args.universe.split(",") if s.strip()]
    targets = build_portfolio(env, token, universe, args.market, args.top_n)

    balance = fetch_balance(env, token, args.mode)
    totals = parse_totals(balance)
    equity = totals.get("tot_evlu_amt") or totals.get("evlu_amt_smtl_amt") or 0
    holdings = parse_holdings(balance)

    orders = compute_orders(targets, holdings, equity)

    print("\n=== Portfolio targets (top momentum) ===")
    for t in targets:
        print(f"{t['symbol']}: price={t['price']} change%={t['change_rate']}")
    print("\nEquity:", equity)

    if not orders:
        print("\nNo rebalancing needed.")
        return

    print("\n=== Planned Orders ===")
    for o in orders:
        print(f"{o['side'].upper():4} {o['symbol']} qty={o['qty']} price={o['price']}")

    if args.dry_run:
        print("\nDry-run mode: no orders sent. Use --live to execute.")
        return

    # Execute orders
    for o in orders:
        try:
            if o["side"] == "buy":
                resp = order_buy(env, token, o["symbol"], o["qty"], price=0 if args.order_type == "01" else o["price"], order_type=args.order_type)
            else:
                resp = order_sell(env, token, o["symbol"], o["qty"], price=0 if args.order_type == "01" else o["price"], order_type=args.order_type)
            odno = resp.get("output", {}).get("ODNO")
            print(f"Sent {o['side']} {o['symbol']} qty={o['qty']} -> ODNO={odno}")
        except Exception as e:
            print(f"Order failed for {o['symbol']}: {e}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Auto-trading using momentum top-N equal weight")
    p.add_argument("--mode", choices=["paper", "prod"], default="paper")
    p.add_argument("--market", default="J", help="J=KRX, NX=Nextrade, UN=Unified")
    p.add_argument("--universe", help="Comma-separated symbols; if omitted, use default universe")
    p.add_argument("--top-n", type=int, default=5, help="Number of symbols to hold")
    p.add_argument("--order-type", default="01", choices=["00", "01"], help="00=limit, 01=market (price=0)")
    p.add_argument("--live", action="store_true", help="Execute orders (default: dry-run)")
    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.dry_run = not args.live
    run(args)
