"""
Flask web server for KIS Open Trading API testing
CLI-style web interface for quick API testing
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from universe import load_universe

# Load environment variables
env_file = Path(".env")
if not env_file.exists():
    print("Warning: .env file not found. Using environment variables or defaults.")
load_dotenv()

app = Flask(__name__)
CORS(app)

TIMEOUT = 5
TOKEN_CACHE: Dict[str, Dict[str, Any]] = {}
DEFAULT_UNIVERSE = [
    # Core large caps
    "005930", "000660", "035420", "207940", "051910", "005380", "068270", "028260", "055550", "006400",
    "105560", "096770", "034730", "003550", "011170", "017670", "003670", "010130", "018260", "009150",
    "032830", "034020", "000270", "036570", "012330",
]


def get_cached_token(mode: str) -> Optional[str]:
    """Return cached token if still valid."""
    cache = TOKEN_CACHE.get(mode)
    if not cache:
        return None
    expires_at = cache.get("expires_at")
    if expires_at and expires_at > time.time():
        return cache.get("token")
    return None


def mask_sensitive_data(data: Any, keys: list = None) -> Any:
    """Mask sensitive information in data"""
    if keys is None:
        keys = ["appkey", "appsecret", "token", "access_token", "authorization"]

    if isinstance(data, dict):
        masked = {}
        for k, v in data.items():
            if k.lower() in [key.lower() for key in keys]:
                if isinstance(v, str) and v:
                    masked[k] = v[:4] + "***" if len(v) > 4 else "***"
                else:
                    masked[k] = "***"
            elif isinstance(v, (dict, list)):
                masked[k] = mask_sensitive_data(v, keys)
            else:
                masked[k] = v
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, keys) for item in data]
    return data


def get_env_config(mode: str) -> Dict[str, str]:
    """Get environment configuration for given mode"""
    if mode == "prod":
        appkey = os.getenv("APP_KEY", "")
        appsecret = os.getenv("APP_SECRET", "")
        return {
            "base": os.getenv("BASE_PROD", "https://openapi.koreainvestment.com:9443"),
            "appkey": appkey,
            "appsecret": appsecret,
            "account": os.getenv("ACCT_STOCK", ""),
            "product": os.getenv("PROD_CODE", "01"),
            "agent": os.getenv("USER_AGENT", "MyTradingApp/1.0"),
            "name": "prod",
        }
    elif mode == "paper":
        paper_acct = os.getenv("PAPER_ACCT_STOCK", "")
        appkey = os.getenv("PAPER_APP_KEY", "")
        appsecret = os.getenv("PAPER_APP_SECRET", "")
        return {
            "base": os.getenv("BASE_PAPER", "https://openapivts.koreainvestment.com:29443"),
            "appkey": appkey,
            "appsecret": appsecret,
            "account": paper_acct if paper_acct else os.getenv("ACCT_STOCK", ""),
            "product": os.getenv("PROD_CODE", "01"),
            "agent": os.getenv("USER_AGENT", "MyTradingApp/1.0"),
            "name": "paper",
        }
    else:
        raise ValueError(f"Unknown mode: {mode}")


def issue_token(env: Dict) -> Dict:
    """Issue access token"""
    if not env.get("appkey") or not env.get("appsecret"):
        raise ValueError("appkey or appsecret is missing")
    url = f"{env['base']}/oauth2/tokenP"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": env["agent"],
    }
    body = {
        "grant_type": "client_credentials",
        "appkey": env["appkey"],
        "appsecret": env["appsecret"],
    }
    resp = requests.post(url, headers=headers, json=body, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def revoke_token(env: Dict, token: str) -> Dict:
    """Revoke access token"""
    if not env.get("appkey") or not env.get("appsecret"):
        raise ValueError("appkey or appsecret is missing")
    
    url = f"{env['base']}/oauth2/revokeP"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": env["agent"],
    }
    body = {
        "token": token,
        "appkey": env["appkey"],
        "appsecret": env["appsecret"],
    }
    resp = requests.post(url, headers=headers, json=body, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def get_or_issue_token(env: Dict, mode: str) -> str:
    """Return cached token if valid, else issue new and cache it."""
    cached = get_cached_token(mode)
    if cached:
        return cached
    result = issue_token(env)
    token = result.get("access_token")
    expires_in = result.get("expires_in")
    if token and expires_in:
        # store with small buffer (minus 60s)
        TOKEN_CACHE[mode] = {
            "token": token,
            "expires_at": time.time() + max(int(expires_in) - 60, 0),
        }
    return token


def fetch_price(env: Dict, token: str, symbol: str, market: str) -> Dict:
    """Fetch stock price"""
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

def fetch_balance(env: Dict, token: str, mode: str) -> Dict:
    """Fetch stock balance with evaluation P/L"""
    tr_id = "VTTC8434R" if mode == "paper" else "TTTC8434R"
    url = f"{env['base']}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": env["appkey"],
        "appsecret": env["appsecret"],
        "tr_id": tr_id,
        "custtype": "P",
        "User-Agent": env["agent"],
    }
    params = {
        "CANO": env["account"],
        "ACNT_PRDT_CD": env["product"],
        "AFHR_FLPR_YN": "N",            # 시간외단일가 여부
        "OFL_YN": "",                   # 오프라인 여부
        "INQR_DVSN": "02",              # 01 대출일별, 02 종목별
        "UNPR_DVSN": "01",              # 단가구분 기본값
        "FUND_STTL_ICLD_YN": "N",       # 펀드결제 포함여부
        "FNCG_AMT_AUTO_RDPT_YN": "N",   # 융자금 자동상환 여부
        "PRCS_DVSN": "00",              # 전일매매 포함
        "CTX_AREA_FK100": "",           # 연속조회키 (초기 공란)
        "CTX_AREA_NK100": "",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def parse_float(text: Optional[str]) -> Optional[float]:
    try:
        if text is None:
            return None
        return float(str(text).replace(',', ''))
    except Exception:
        return None


def order_buy(env: Dict, token: str, symbol: str, qty: int, price: int = 0, order_type: str = "00") -> Dict:
    """Place buy order"""
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
    """Place sell order"""
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
        "SLL_TYPE": "01",
    }
    resp = requests.post(url, headers=headers, json=body, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


@app.route("/")
def index():
    """Serve main page"""
    return render_template("index.html")


@app.route("/api/token/issue", methods=["POST"])
def api_token_issue():
    """Issue access token"""
    try:
        data = request.get_json() or {}
        mode = data.get("mode", "paper")

        env = get_env_config(mode)
        if not env.get("appkey") or not env.get("appsecret"):
            return jsonify({
                "success": False,
                "error": f"Missing credentials for {mode} mode. Check PAPER_APP_KEY/PAPER_APP_SECRET (or APP_KEY/APP_SECRET) in .env file"
            }), 400

        cached = get_cached_token(mode)
        if cached:
            print(f"[{mode}] Token reused from cache")
            return jsonify({"success": True, "data": {"access_token": "***cached***"}, "token": cached})

        result = issue_token(env)
        token = result.get("access_token")

        # Mask sensitive data for UI display, but return token separately
        masked_result = mask_sensitive_data(result)

        print(f"[{mode}] Token issued: expires_in={result.get('expires_in')}")
        return jsonify(
            {
                "success": True,
                "data": masked_result,
                "token": token,
                "expires_in": result.get("expires_in"),
            }
        )
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {e.response.status_code}"
        try:
            error_detail = e.response.json()
            error_code = error_detail.get('error_code', '')
            error_desc = error_detail.get('error_description', '')
            
            if e.response.status_code == 403:
                if error_code == 'EGW00002':
                    error_msg += f": {error_desc} (코드: {error_code})"
                    error_msg += "\n가능한 원인:"
                    error_msg += "\n1. IP 화이트리스트 미설정 (한국투자증권 홈페이지에서 설정 필요)"
                    error_msg += "\n2. appkey/appsecret 오류 또는 만료"
                    error_msg += "\n3. API 사용 승인 미완료"
                else:
                    error_msg += f": Authentication failed - {error_desc}"
            elif e.response.status_code == 401:
                error_msg += f": Unauthorized - {error_desc}"
            else:
                error_msg += f" - {error_desc or str(e)}"
        except:
            if e.response.status_code == 403:
                error_msg += ": Authentication failed. Check appkey/appsecret and IP whitelist"
            else:
                error_msg += f" - {str(e)}"
        print(f"Error issuing token: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), e.response.status_code
    except ValueError as e:
        print(f"Error issuing token: {e}")
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        print(f"Error issuing token: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/token/revoke", methods=["POST"])
def api_token_revoke():
    """Revoke access token"""
    try:
        data = request.get_json() or {}
        token = data.get("token")
        mode = data.get("mode", "paper")
        
        if not token:
            return jsonify({"success": False, "error": "token is required"}), 400

        env = get_env_config(mode)
        result = revoke_token(env, token)
        masked_result = mask_sensitive_data(result)
        # clear cache for mode if same token
        cached = TOKEN_CACHE.get(mode, {})
        if cached.get("token") == token:
            TOKEN_CACHE.pop(mode, None)

        print(f"[{mode}] Token revoked")
        return jsonify({"success": True, "data": masked_result})
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {e.response.status_code}"
        if e.response.status_code == 403:
            error_msg += ": Authentication failed"
        else:
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail.get('message', str(e))}"
            except:
                error_msg += f" - {str(e)}"
        print(f"Error revoking token: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), e.response.status_code
    except Exception as e:
        print(f"Error revoking token: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/price", methods=["GET"])
def api_price():
    """Fetch stock price"""
    try:
        symbol = request.args.get("symbol")
        market = request.args.get("market", "J")
        mode = request.args.get("mode", "paper")
        token = request.args.get("token")
        
        if not symbol:
            return jsonify({"success": False, "error": "symbol is required"}), 400
        
        env = get_env_config(mode)
        
        if not token:
            token = get_or_issue_token(env, mode)
            if not token:
                return jsonify({"success": False, "error": "failed to obtain token"}), 500
        
        result = fetch_price(env, token, symbol, market)
        
        # Mask sensitive data in output
        masked_result = mask_sensitive_data(result)
        
        output = result.get("output", {})
        print(f"[{mode}] Price query: {symbol} = {output.get('stck_prpr', 'N/A')}")
        return jsonify({"success": True, "data": masked_result})
    except Exception as e:
        print(f"Error fetching price: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/order", methods=["POST"])
def api_order():
    """Place order (buy or sell)"""
    try:
        data = request.get_json() or {}
        side = data.get("side")  # buy or sell
        symbol = data.get("symbol")
        qty = data.get("qty")
        price = data.get("price", 0)
        order_type = data.get("order_type", "00")  # 00=limit, 01=market
        mode = data.get("mode", "paper")
        token = data.get("token")
        
        if not side or side not in ["buy", "sell"]:
            return jsonify({"success": False, "error": "side must be 'buy' or 'sell'"}), 400
        if not symbol:
            return jsonify({"success": False, "error": "symbol is required"}), 400
        if not qty:
            return jsonify({"success": False, "error": "qty is required"}), 400
        
        env = get_env_config(mode)
        
        # Issue token if not provided
        if not token:
            token = get_or_issue_token(env, mode)
            if not token:
                return jsonify({"success": False, "error": "failed to obtain token"}), 500
        
        # Place order
        if side == "buy":
            result = order_buy(env, token, symbol, int(qty), int(price), order_type)
        else:
            result = order_sell(env, token, symbol, int(qty), int(price), order_type)

        # Mask sensitive data
        masked_result = mask_sensitive_data(result)

        output = result.get("output", {})
        order_no = output.get("ODNO", "N/A")
        print(f"[{mode}] Order placed: {side} {symbol} x{qty} -> {order_no}")
        return jsonify({"success": True, "data": masked_result})
    except Exception as e:
        print(f"Error placing order: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/balance", methods=["GET"])
def api_balance():
    """Fetch balance and P/L"""
    try:
        mode = request.args.get("mode", "paper")
        token = request.args.get("token")

        env = get_env_config(mode)

        if not token:
            token = get_or_issue_token(env, mode)
            if not token:
                return jsonify({"success": False, "error": "failed to obtain token"}), 500

        result = fetch_balance(env, token, mode)
        masked_result = mask_sensitive_data(result)

        # Extract totals block (output2 if list/dict, else output1)
        output2 = masked_result.get("output2")
        totals_block: Dict[str, str] = {}
        if isinstance(output2, list) and output2:
            totals_block = output2[0] if isinstance(output2[0], dict) else {}
        elif isinstance(output2, dict):
            totals_block = output2
        else:
            o1 = masked_result.get("output1")
            if isinstance(o1, list) and o1 and isinstance(o1[0], dict):
                totals_block = o1[0]
            elif isinstance(o1, dict):
                totals_block = o1

        key_fields = [
            "tot_evlu_amt",        # 총평가금액
            "evlu_pfls_smtl_amt",  # 평가손익합계금액
            "asst_icdc_erng_rt",   # 자산증감수익율
            "dnca_tot_amt",        # 예수금총금액
            "pchs_amt_smtl_amt",   # 매입금액합계금액
            "evlu_amt_smtl_amt",   # 평가금액합계금액
        ]
        summary = {k: totals_block[k] for k in key_fields if k in totals_block}

        print(f"[{mode}] Balance fetched")
        return jsonify({"success": True, "data": masked_result, "summary": summary})
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """
    Simple quant-style recommendation: rank symbols by intraday change rate (prdy_ctrt).
    Input JSON: { "symbols": ["005930","000660"], "market": "J", "mode": "paper" }
    """
    try:
        data = request.get_json() or {}
        symbols = data.get("symbols") or []
        market = data.get("market", "J")
        mode = data.get("mode", "paper")

        if isinstance(symbols, str):
            symbols = [s.strip() for s in symbols.split(",") if s.strip()]
        if not symbols:
            return jsonify({"success": False, "error": "symbols list is required"}), 400

        env = get_env_config(mode)
        token = get_or_issue_token(env, mode)
        if not token:
            return jsonify({"success": False, "error": "failed to obtain token"}), 500

        results = []
        for sym in symbols:
            try:
                price_resp = fetch_price(env, token, sym, market)
                out = price_resp.get("output", {})
                change_rate = parse_float(out.get("prdy_ctrt")) or 0.0
                price = out.get("stck_prpr")
                results.append(
                    {
                        "symbol": sym,
                        "price": price,
                        "change_rate": change_rate,
                        "raw": mask_sensitive_data(price_resp),
                    }
                )
            except Exception as e:
                results.append({"symbol": sym, "error": str(e)})

        ranked = sorted(results, key=lambda x: x.get("change_rate", -1e9), reverse=True)
        summary = [{"symbol": r["symbol"], "price": r.get("price"), "change_rate": r.get("change_rate")} for r in ranked]

        print(f"[{mode}] Recommend computed for {len(symbols)} symbols")
        return jsonify({"success": True, "summary": summary, "data": ranked})
    except Exception as e:
        print(f"Error computing recommendations: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/portfolio", methods=["POST"])
def api_portfolio():
    """
    Build a simple momentum-based portfolio.
    Input JSON:
      symbols: list or comma string (ignored if use_system is true)
      market: J/NX/UN
      mode: paper/prod
      top_n: how many symbols to select (default 5)
      alloc: 'equal' (currently only equal weight supported)
      use_system: bool, default true -> use DEFAULT_UNIVERSE
      universe_limit: int, when use_system true, number of symbols to fetch (default 200)
    """
    try:
        data = request.get_json() or {}
        symbols = data.get("symbols")
        market = data.get("market", "J")
        mode = data.get("mode", "paper")
        top_n = int(data.get("top_n", 5))
        alloc = data.get("alloc", "equal")
        use_system = data.get("use_system", True)
        universe_limit = int(data.get("universe_limit", 200))

        if use_system or not symbols:
            symbols = load_universe(limit=universe_limit)
        elif isinstance(symbols, str):
            symbols = [s.strip() for s in symbols.split(",") if s.strip()]

        if not symbols:
            return jsonify({"success": False, "error": "symbols universe is empty"}), 400

        top_n = max(1, min(top_n, len(symbols)))

        env = get_env_config(mode)
        token = get_or_issue_token(env, mode)
        if not token:
            return jsonify({"success": False, "error": "failed to obtain token"}), 500

        scored = []
        for sym in symbols:
            try:
                price_resp = fetch_price(env, token, sym, market)
                out = price_resp.get("output", {})
                change_rate = parse_float(out.get("prdy_ctrt")) or 0.0
                price = out.get("stck_prpr")
                scored.append(
                    {
                        "symbol": sym,
                        "price": price,
                        "change_rate": change_rate,
                        "raw": mask_sensitive_data(price_resp),
                    }
                )
            except Exception as e:
                scored.append({"symbol": sym, "error": str(e), "change_rate": -1e9})

        ranked = sorted(scored, key=lambda x: x.get("change_rate", -1e9), reverse=True)
        picks = ranked[:top_n]

        if alloc == "equal":
            weight = round(1.0 / top_n, 4)
            for p in picks:
                p["weight"] = weight
        else:
            for p in picks:
                p["weight"] = None

        summary = [{"symbol": p["symbol"], "price": p.get("price"), "change_rate": p.get("change_rate"), "weight": p.get("weight")} for p in picks]

        print(f"[{mode}] Portfolio built from {len(symbols)} -> top {top_n}")
        return jsonify({"success": True, "summary": summary, "data": picks})
    except Exception as e:
        print(f"Error building portfolio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5173))
    print(f"Starting KIS API test server on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    app.run(host="0.0.0.0", port=port, debug=True)
