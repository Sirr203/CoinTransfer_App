"""Payment history tracking and monthly summary analytics (pure Python, Flet-independent)."""
import json
import os
import uuid
from datetime import datetime, date
from i18n import t

MAX_HISTORY_ENTRIES = 500

def _get_history_path():
    base = os.environ.get("FLET_APP_STORAGE_DATA")
    if not base or not os.path.exists(base):
        base = os.path.expanduser("~")
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        pass
    return os.path.join(base, "history.json")

def load_history(path=None) -> list[dict]:
    """Loads payment history entries from JSON. Returns [] if missing or corrupted."""
    filepath = path or _get_history_path()
    try:
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data[:MAX_HISTORY_ENTRIES]
            return []
    except Exception:
        return []

def save_history(entries: list[dict], path=None) -> None:
    """Atomically writes history entries to disk, capping at MAX_HISTORY_ENTRIES."""
    filepath = path or _get_history_path()
    try:
        capped = entries[:MAX_HISTORY_ENTRIES]
        tmp_path = filepath + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(capped, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, filepath)
    except Exception:
        pass

def create_entry(
    bill: int,
    total_paid: int,
    change: int,
    pay: dict,
    change_breakdown: dict,
    mode: str,
    wallet_total_after: int,
    timestamp: str = None,
    entry_id: str = None,
) -> dict:
    """Creates a validated payment history entry dictionary."""
    return {
        "id": entry_id or str(uuid.uuid4()),
        "timestamp": timestamp or datetime.now().isoformat(),
        "bill": int(bill),
        "total_paid": int(total_paid),
        "change": int(change),
        "pay": {str(k): int(v) for k, v in pay.items()},
        "change_breakdown": {str(k): int(v) for k, v in change_breakdown.items()},
        "mode": str(mode),  # "fast" or "optimize_notes"
        "wallet_total_after": int(wallet_total_after),
    }

def add_entry(entries: list[dict], entry: dict, path=None) -> list[dict]:
    """Prepends a new history entry, caps at 500, saves to disk, and returns updated list."""
    updated = [entry] + list(entries)
    updated = updated[:MAX_HISTORY_ENTRIES]
    save_history(updated, path=path)
    return updated

def delete_entry(entries: list[dict], entry_id: str, path=None) -> list[dict]:
    """Deletes a single entry by id without altering wallet state. Saves and returns updated list."""
    updated = [e for e in entries if e.get("id") != entry_id]
    save_history(updated, path=path)
    return updated

def undo_last_payment(entries: list[dict], wallet: dict, path=None) -> tuple[list[dict], dict]:
    """Reverses the most recent payment on the wallet, removes the entry, saves, and returns (entries, wallet)."""
    if not entries:
        return entries, wallet

    last_entry = entries[0]
    restored_wallet = dict(wallet)

    # Reverse pay: add back coins/notes handed over
    for d_str, count in last_entry.get("pay", {}).items():
        d = int(d_str)
        restored_wallet[d] = restored_wallet.get(d, 0) + count

    # Reverse change: subtract coins/notes received back
    for d_str, count in last_entry.get("change_breakdown", {}).items():
        d = int(d_str)
        restored_wallet[d] = max(0, restored_wallet.get(d, 0) - count)

    remaining_entries = entries[1:]
    save_history(remaining_entries, path=path)
    return remaining_entries, restored_wallet

def clear_history(path=None) -> list[dict]:
    """Clears all history entries and saves empty list."""
    save_history([], path=path)
    return []

def get_monthly_summary(entries: list[dict], year: int = None, month: int = None) -> dict:
    """Calculates total spent and payment count for a given year and month (defaults to current)."""
    now = datetime.now()
    target_year = year if year is not None else now.year
    target_month = month if month is not None else now.month

    total_spent = 0
    count = 0

    for entry in entries:
        ts = entry.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts)
            if dt.year == target_year and dt.month == target_month:
                total_spent += entry.get("bill", 0)
                count += 1
        except Exception:
            continue

    return {
        "year": target_year,
        "month": target_month,
        "total_spent": total_spent,
        "payment_count": count,
    }

def format_entry_date_group(iso_timestamp: str, lang: str = "en") -> tuple[str, str]:
    """Returns (group_header, time_str) for an entry ISO timestamp.
    group_header is localized: 'Today', 'Yesterday', or formatted date.
    time_str is 'HH:MM'.
    """
    try:
        dt = datetime.fromisoformat(iso_timestamp)
    except Exception:
        return iso_timestamp[:10], ""

    time_str = dt.strftime("%H:%M")
    entry_date = dt.date()
    today = date.today()
    days_diff = (today - entry_date).days

    if days_diff == 0:
        return t("history_today", lang), time_str
    if days_diff == 1:
        return t("history_yesterday", lang), time_str

    if lang == "ja":
        return dt.strftime("%Y年%m月%d日"), time_str
    if lang == "vi":
        return dt.strftime("%d/%m/%Y"), time_str
    return dt.strftime("%b %d, %Y"), time_str

def format_month_label(year: int, month: int, lang: str = "en") -> str:
    """Formats month for the summary card title."""
    if lang == "ja":
        return f"{year}年{month}月"
    if lang == "vi":
        return f"{month:02d}/{year}"
    try:
        d = date(year, month, 1)
        return d.strftime("%b %Y")
    except Exception:
        return f"{month:02d}/{year}"

