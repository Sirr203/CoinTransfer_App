"""Người 1: thuật toán tối ưu + lưu ví (thuần Python, không phụ thuộc Flet)."""
import json, os

DENOMS = [10000, 5000, 1000, 500, 100, 50, 10, 5, 1]
W_COIN, W_NOTE, W_HAND = 10, 2, 1   # "nặng" của xu / tiền giấy / mỗi tờ-xu phải đưa
MAX_EXTRA = 10000                   # không đưa dư quá mức này

def _w(d): return W_NOTE if d >= 1000 else W_COIN

def make_change(c):
    """Quầy thu ngân trả lại theo greedy (ít tờ/xu nhất)."""
    out = {}
    for d in DENOMS:
        out[d], c = divmod(c, d)
    return {d: n for d, n in out.items() if n}

def _change_weight(c):
    return sum(_w(d) * n for d, n in make_change(c).items())

def suggest(wallet, bill):
    """wallet: {mệnh giá: số lượng}. Trả về dict {pay, change, after} hoặc None nếu không đủ tiền.
    Tối thiểu hoá: 'độ nặng' ví sau giao dịch + chút phạt cho số tờ/xu phải đưa."""
    total = sum(d * n for d, n in wallet.items())
    if bill <= 0 or total < bill:
        return None
    smax = min(total, bill + MAX_EXTRA)
    NEG = float("-inf")
    dp = [NEG] * (smax + 1); dp[0] = 0
    choices = []
    for d in DENOMS:
        n = wallet.get(d, 0); v = _w(d) - W_HAND   # lợi ích khi đưa 1 tờ/xu này đi
        new = [NEG] * (smax + 1); ch = [0] * (smax + 1)
        for s in range(smax + 1):
            for k in range(0, min(n, s // d) + 1):
                p = dp[s - k * d]
                if p != NEG and p + k * v > new[s]:
                    new[s] = p + k * v; ch[s] = k
        dp = new; choices.append(ch)
    best_s, best_cost = None, None
    for s in range(bill, smax + 1):
        if dp[s] == NEG: continue
        cost = -dp[s] + _change_weight(s - bill)
        if best_cost is None or cost < best_cost:
            best_s, best_cost = s, cost
    if best_s is None:
        return None
    pay, s = {}, best_s
    for i in range(len(DENOMS) - 1, -1, -1):
        k = choices[i][s]
        if k: pay[DENOMS[i]] = k
        s -= k * DENOMS[i]
    change = make_change(best_s - bill)
    after = dict(wallet)
    for d, k in pay.items(): after[d] -= k
    for d, k in change.items(): after[d] = after.get(d, 0) + k
    return {"pay": dict(sorted(pay.items(), reverse=True)), "total_paid": best_s,
            "change": change, "after": after}

def confirm(wallet, result):
    return {d: n for d, n in result["after"].items()}

# ---- Lưu trữ JSON nội bộ ----
def _path():
    base = os.environ.get("FLET_APP_STORAGE_DATA", os.path.expanduser("~"))
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "wallet.json")

def load_wallet():
    try:
        with open(_path(), encoding="utf-8") as f:
            data = json.load(f)
        return {d: int(data.get(str(d), 0)) for d in DENOMS}
    except Exception:
        return {d: 0 for d in DENOMS}

def save_wallet(wallet):
    tmp = _path() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({str(d): n for d, n in wallet.items()}, f)
    os.replace(tmp, _path())   # ghi nguyên tử, tránh hỏng file
