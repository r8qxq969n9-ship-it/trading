"""
Simple CLI harness for Korea Investment Open Trading API (domestic stock).
Flows:
  - token: issue or revoke access tokens
  - price: fetch single stock quote using REST
  - order: place buy/sell orders (cash)
  - inquire: check order status

Configuration: kis_devlp.yaml (same keys as official sample)
Required fields:
  my_app / my_sec              # 실전 appkey/appsecret
  paper_app / paper_sec        # 모의 appkey/appsecret
  my_acct_stock / my_prod      # 계좌 앞 8자리 / 상품코드 2자리
  prod / vps                   # 실전/모의 REST base URL
  my_agent                     # User-Agent string
"""

import argparse
import sys
from pathlib import Path
from typing import Dict

import requests
import yaml


TIMEOUT = 5


class ConfigError(Exception):
    pass


def load_config(path: Path) -> Dict:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    required = [
        "my_app",
        "my_sec",
        "paper_app",
        "paper_sec",
        "my_acct_stock",
        "my_prod",
        "prod",
        "vps",
        "my_agent",
    ]
    missing = [k for k in required if not data.get(k)]
    if missing:
        raise ConfigError(f"Missing config keys: {', '.join(missing)}")
    return data


def select_env(cfg: Dict, mode: str) -> Dict:
    if mode == "prod":
        return {
            "base": cfg["prod"],
            "appkey": cfg["my_app"],
            "appsecret": cfg["my_sec"],
            "account": cfg["my_acct_stock"],
            "product": cfg["my_prod"],
            "agent": cfg["my_agent"],
            "name": "prod",
        }
    if mode == "paper":
        return {
            "base": cfg["vps"],
            "appkey": cfg["paper_app"],
            "appsecret": cfg["paper_sec"],
            "account": cfg.get("my_paper_stock", cfg["my_acct_stock"]),  # 모의 계좌가 없으면 실전 계좌 사용
            "product": cfg["my_prod"],
            "agent": cfg["my_agent"],
            "name": "paper",
        }
    raise ConfigError(f"Unknown mode: {mode}")


def issue_token(env: Dict) -> Dict:
    url = f"{env['base']}/oauth2/tokenP"
    body = {
        "grant_type": "client_credentials",
        "appkey": env["appkey"],
        "appsecret": env["appsecret"],
    }
    resp = requests.post(url, json=body, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def revoke_token(env: Dict, token: str) -> Dict:
    url = f"{env['base']}/oauth2/revokeP"
    body = {
        "token": token,
        "appkey": env["appkey"],
        "appsecret": env["appsecret"],
    }
    resp = requests.post(url, json=body, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def fetch_price(env: Dict, token: str, symbol: str, market: str) -> Dict:
    url = f"{env['base']}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": env["appkey"],
        "appsecret": env["appsecret"],
        "tr_id": "FHKST01010100",
        "custtype": "P",
        "User-Agent": env["agent"],
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": market,
        "FID_INPUT_ISCD": symbol,
    }
    resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def order_buy(env: Dict, token: str, symbol: str, qty: int, price: int = 0, order_type: str = "00") -> Dict:
    """
    매수 주문
    order_type: "00"=지정가, "01"=시장가
    """
    url = f"{env['base']}/uapi/domestic-stock/v1/trading/order-cash"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": env["appkey"],
        "appsecret": env["appsecret"],
        "tr_id": "TTTC0012U",
        "custtype": "P",
        "User-Agent": env["agent"],
    }
    body = {
        "CANO": env["account"],
        "ACNT_PRDT_CD": env["product"],
        "PDNO": symbol,
        "ORD_DVSN": order_type,
        "ORD_QTY": str(qty),
        "ORD_UNPR": str(price) if order_type == "00" else "0",
    }
    resp = requests.post(url, headers=headers, json=body, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def order_sell(env: Dict, token: str, symbol: str, qty: int, price: int = 0, order_type: str = "00") -> Dict:
    """
    매도 주문
    order_type: "00"=지정가, "01"=시장가
    """
    url = f"{env['base']}/uapi/domestic-stock/v1/trading/order-cash"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": env["appkey"],
        "appsecret": env["appsecret"],
        "tr_id": "TTTC0011U",
        "custtype": "P",
        "User-Agent": env["agent"],
    }
    body = {
        "CANO": env["account"],
        "ACNT_PRDT_CD": env["product"],
        "PDNO": symbol,
        "ORD_DVSN": order_type,
        "ORD_QTY": str(qty),
        "ORD_UNPR": str(price) if order_type == "00" else "0",
        "SLL_TYPE": "01",  # 매도주문구분: 01=보통
    }
    resp = requests.post(url, headers=headers, json=body, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def inquire_order(env: Dict, token: str, order_no: str = None) -> Dict:
    """
    주문 조회
    order_no가 제공되면 해당 주문만 조회, 없으면 전체 조회
    """
    url = f"{env['base']}/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": env["appkey"],
        "appsecret": env["appsecret"],
        "tr_id": "TTTC8001R",
        "custtype": "P",
        "User-Agent": env["agent"],
    }
    params = {
        "CANO": env["account"],
        "ACNT_PRDT_CD": env["product"],
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": "",
    }
    if order_no:
        params["INQR_DVSN"] = "02"  # 주문번호로 조회
        params["INQR_DVSN_3"] = order_no
    else:
        params["INQR_DVSN"] = "01"  # 전체 조회
    
    resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def cmd_token(args: argparse.Namespace, env: Dict) -> None:
    if args.revoke:
        if not args.token:
            sys.exit("token is required for revoke")
        data = revoke_token(env, args.token)
        print("revoked:", data)
    else:
        data = issue_token(env)
        print("issued token:")
        print("  access_token:", data.get("access_token"))
        print("  token_type :", data.get("token_type"))
        print("  expires_in:", data.get("expires_in"))


def cmd_price(args: argparse.Namespace, env: Dict) -> None:
    token = args.token
    if not token:
        token_data = issue_token(env)
        token = token_data.get("access_token")
        if not token:
            sys.exit("failed to obtain token")
    data = fetch_price(env, token, args.symbol, args.market)
    output = data.get("output", {})
    print("price result:")
    print("  rt_cd :", data.get("rt_cd"))
    print("  msg_cd:", data.get("msg_cd"))
    print("  msg1  :", data.get("msg1"))
    if output:
        # 주요 필드만 요약
        for key in ["stck_prpr", "prdy_vrss", "prdy_ctrt", "stck_oprc", "stck_hgpr", "stck_lwpr"]:
            if key in output:
                print(f"  {key}: {output[key]}")
    else:
        print("  raw output:", output)


def cmd_order(args: argparse.Namespace, env: Dict) -> None:
    token = args.token
    if not token:
        token_data = issue_token(env)
        token = token_data.get("access_token")
        if not token:
            sys.exit("failed to obtain token")
    
    if args.side == "buy":
        data = order_buy(env, token, args.symbol, args.qty, args.price, args.order_type)
    elif args.side == "sell":
        data = order_sell(env, token, args.symbol, args.qty, args.price, args.order_type)
    else:
        sys.exit(f"unknown side: {args.side}")
    
    print("order result:")
    print("  rt_cd :", data.get("rt_cd"))
    print("  msg_cd:", data.get("msg_cd"))
    print("  msg1  :", data.get("msg1"))
    output = data.get("output", {})
    if output:
        print("  order_no (ODNO):", output.get("ODNO"))
        print("  order_time (ORD_TMD):", output.get("ORD_TMD"))
        print("  raw output:", output)
    else:
        print("  raw response:", data)


def cmd_inquire(args: argparse.Namespace, env: Dict) -> None:
    token = args.token
    if not token:
        token_data = issue_token(env)
        token = token_data.get("access_token")
        if not token:
            sys.exit("failed to obtain token")
    
    data = inquire_order(env, token, args.order_no)
    print("inquire result:")
    print("  rt_cd :", data.get("rt_cd"))
    print("  msg_cd:", data.get("msg_cd"))
    print("  msg1  :", data.get("msg1"))
    output = data.get("output", [])
    if output:
        print(f"  found {len(output)} order(s):")
        for idx, order in enumerate(output[:5], 1):  # 최대 5개만 출력
            print(f"  [{idx}]")
            for key in ["ODNO", "ORD_TMD", "ORD_DVSN", "PDNO", "ORD_QTY", "ORD_UNPR", "ORD_STAT_CD"]:
                if key in order:
                    print(f"      {key}: {order[key]}")
        if len(output) > 5:
            print(f"  ... and {len(output) - 5} more order(s)")
    else:
        print("  no orders found")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="KIS Open API CLI tester (domestic stock)")
    p.add_argument("--config", default="kis_devlp.yaml", help="path to kis_devlp.yaml")
    p.add_argument("--mode", choices=["paper", "prod"], default="paper", help="environment selector")
    sub = p.add_subparsers(dest="command", required=True)

    p_token = sub.add_parser("token", help="issue or revoke token")
    p_token.add_argument("--revoke", action="store_true", help="revoke token instead of issuing")
    p_token.add_argument("--token", help="token value (required for revoke)")

    p_price = sub.add_parser("price", help="fetch single stock price")
    p_price.add_argument("--symbol", required=True, help="KRX symbol code (e.g., 005930)")
    p_price.add_argument(
        "--market",
        default="J",
        help="FID_COND_MRKT_DIV_CODE (J=KRX, NX=넥스트레이드, UN=통합)",
    )
    p_price.add_argument("--token", help="existing access token (optional)")

    p_order = sub.add_parser("order", help="place buy/sell order")
    p_order.add_argument("--side", choices=["buy", "sell"], required=True, help="buy or sell")
    p_order.add_argument("--symbol", required=True, help="KRX symbol code (e.g., 005930)")
    p_order.add_argument("--qty", type=int, required=True, help="order quantity")
    p_order.add_argument("--price", type=int, default=0, help="order price (required for limit order)")
    p_order.add_argument("--order-type", default="00", choices=["00", "01"], help="00=limit, 01=market")
    p_order.add_argument("--token", help="existing access token (optional)")

    p_inquire = sub.add_parser("inquire", help="inquire order status")
    p_inquire.add_argument("--order-no", help="order number (optional, if not provided, list all orders)")
    p_inquire.add_argument("--token", help="existing access token (optional)")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        cfg = load_config(Path(args.config))
        env = select_env(cfg, args.mode)
    except ConfigError as e:
        sys.exit(f"config error: {e}")

    if args.command == "token":
        cmd_token(args, env)
    elif args.command == "price":
        cmd_price(args, env)
    elif args.command == "order":
        cmd_order(args, env)
    elif args.command == "inquire":
        cmd_inquire(args, env)
    else:
        parser.error(f"unknown command {args.command}")


if __name__ == "__main__":
    main()
