"""Payment optimization algorithm and wallet persistence (pure Python, Flet-independent)."""
import json, os

DENOMS = [10000, 5000, 1000, 500, 100, 50, 10, 5, 1]
W_COIN, W_NOTE, W_HAND = 10, 2, 1   # Penalty weights for note-optimization mode (coin cleanup)
MAX_EXTRA = 10000                   # Do not consider overpaying beyond this surplus

def _w(d): return W_NOTE if d >= 1000 else W_COIN

def make_change(c):
    """Greedy change calculation by the cash register (fewest bills/coins)."""
    out = {}
    for d in DENOMS:
        out[d], c = divmod(c, d)
    return {d: n for d, n in out.items() if n}

def _change_weight(c):
    return sum(_w(d) * n for d, n in make_change(c).items())

def _change_count(c):
    return sum(make_change(c).values())

def suggest(wallet, bill, prefer_notes=False):
    """Suggests an optimal payment combination.
    wallet: {denomination: count}
    bill: invoice amount
    prefer_notes:
      - False (Default - Fast): Minimize total bills/coins handed + received.
      - True (Optimize Notes): Shed loose coins to receive higher-denomination bills/coins.
    """
    total = sum(d * n for d, n in wallet.items())
    if bill <= 0 or total < bill:
        return None
    smax = min(total, bill + MAX_EXTRA)

    if prefer_notes:
        # Note-optimization mode: Minimize post-transaction wallet weight
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
        # Fast mode: Minimize (items handed over + change items received)
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
            # Primary cost: total items handed + received; secondary: minimum change surplus
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

# ---- Internal JSON Storage ----
def _path(filename="wallet.json"):
    base = os.environ.get("FLET_APP_STORAGE_DATA")
    if not base or not os.path.exists(base):
        base = os.path.expanduser("~")
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        pass
    return os.path.join(base, filename)

def load_wallet():
    try:
        with open(_path("wallet.json"), encoding="utf-8") as f:
            data = json.load(f)
        return {d: int(data.get(str(d), 0)) for d in DENOMS}
    except Exception:
        return {d: 0 for d in DENOMS}

def save_wallet(wallet):
    try:
        target = _path("wallet.json")
        tmp = target + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({str(d): n for d, n in wallet.items()}, f)
        os.replace(tmp, target)
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
        target = _path("settings.json")
        tmp = target + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(settings, f)
        os.replace(tmp, target)
    except Exception:
        pass
