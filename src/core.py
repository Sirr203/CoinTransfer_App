"""Thuật toán tối ưu + đọc/ghi dữ liệu ví (thuần Python, không phụ thuộc Flet)."""
import json, os

DENOMS = [10000, 5000, 1000, 500, 100, 50, 10, 5, 1]
W_COIN, W_NOTE, W_HAND = 10, 2, 1   # Trọng số cho chế độ dọn xu (tối ưu tiền giấy)
MAX_EXTRA = 10000                   # Không đưa dư quá mức này

def _w(d): return W_NOTE if d >= 1000 else W_COIN

def make_change(c):
    """Quầy thu ngân trả lại theo greedy (ít tờ/xu nhất)."""
    out = {}
    for d in DENOMS:
        out[d], c = divmod(c, d)
    return {d: n for d, n in out.items() if n}

def _change_weight(c):
    return sum(_w(d) * n for d, n in make_change(c).items())

def _change_count(c):
    return sum(make_change(c).values())

def suggest(wallet, bill, prefer_notes=False):
    """Gợi ý cách trả tiền.
    wallet: {mệnh giá: số lượng}
    bill: số tiền hóa đơn
    prefer_notes:
      - False (Mặc định - Nhanh): Đưa và nhận lại ít tờ/xu nhất. Hóa đơn 10¥ đưa đúng 1 xu 10¥.
      - True (Tối ưu tiền giấy / Dọn xu): Ưu tiên tống khứ xu lẻ, đổi xu thành tiền giấy.
    """
    total = sum(d * n for d, n in wallet.items())
    if bill <= 0 or total < bill:
        return None
    smax = min(total, bill + MAX_EXTRA)

    if prefer_notes:
        # Chế độ dọn xu (logic cũ tối ưu độ nặng ví)
        NEG = float("-inf")
        dp = [NEG] * (smax + 1); dp[0] = 0
        choices = []
        for d in DENOMS:
            n = wallet.get(d, 0); v = _w(d) - W_HAND
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

        if best_s is None: return None
        pay, s = {}, best_s
        for i in range(len(DENOMS) - 1, -1, -1):
            k = choices[i][s]
            if k: pay[DENOMS[i]] = k
            s -= k * DENOMS[i]
    else:
        # Chế độ Mặc định (Nhanh): Tối thiểu hóa (số tờ/xu đưa đi + số tờ/xu nhận lại)
        INF = float("inf")
        dp = [INF] * (smax + 1); dp[0] = 0
        choices = []
        for d in DENOMS:
            n = wallet.get(d, 0)
            new = [INF] * (smax + 1); ch = [0] * (smax + 1)
            for s in range(smax + 1):
                for k in range(0, min(n, s // d) + 1):
                    p = dp[s - k * d]
                    if p != INF and p + k < new[s]:
                        new[s] = p + k; ch[s] = k
            dp = new; choices.append(ch)

        best_s, best_cost = None, None
        for s in range(bill, smax + 1):
            if dp[s] == INF: continue
            pay_items = dp[s]
            change_items = _change_count(s - bill)
            # Chi phí chính: tổng số tờ/xu đưa + nhận; phụ: tiền thừa ít nhất
            cost = (pay_items + change_items) * 100000 + (s - bill)
            if best_cost is None or cost < best_cost:
                best_s, best_cost = s, cost

        if best_s is None: return None
        pay, s = {}, best_s
        for i in range(len(DENOMS) - 1, -1, -1):
            k = choices[i][s]
            if k: pay[DENOMS[i]] = k
            s -= k * DENOMS[i]

    change = make_change(best_s - bill)
    after = dict(wallet)
    for d, k in pay.items(): after[d] -= k
    for d, k in change.items(): after[d] = after.get(d, 0) + k
    return {
        "pay": dict(sorted(pay.items(), reverse=True)),
        "total_paid": best_s,
        "change": change,
        "after": after,
    }

# ---- Lưu trữ JSON nội bộ ----
def _path(filename="wallet.json"):
    base = os.environ.get("FLET_APP_STORAGE_DATA", os.path.expanduser("~"))
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, filename)

def load_wallet():
    try:
        with open(_path("wallet.json"), encoding="utf-8") as f:
            data = json.load(f)
        return {d: int(data.get(str(d), 0)) for d in DENOMS}
    except Exception:
        return {d: 0 for d in DENOMS}

def save_wallet(wallet):
    tmp = _path("wallet.json") + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({str(d): n for d, n in wallet.items()}, f)
    os.replace(tmp, _path("wallet.json"))

def load_settings():
    try:
        with open(_path("settings.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"prefer_notes": False}

def save_settings(settings):
    try:
        tmp = _path("settings.json") + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(settings, f)
        os.replace(tmp, _path("settings.json"))
    except Exception:
        pass

def load_settings():
    try:
        with open(_path("settings.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"prefer_notes": False}

def save_settings(settings):
    try:
        tmp = _path("settings.json") + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(settings, f)
        os.replace(tmp, _path("settings.json"))
    except Exception:
        pass

