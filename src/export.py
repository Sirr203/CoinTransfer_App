"""Payment history Excel export module for CoinTrans (pure Python, zero Flet dependency).

Generates a multi-sheet formatted .xlsx workbook using XlsxWriter:
1. Payments: One row per transaction with real dates, numeric yen, autofilter, and breakdowns.
2. Details: Long/tidy format for pivot tables (payment id, date, kind, denomination, count, subtotal).
3. Summary: Monthly aggregation table with totals, plus denomination usage breakdown.
"""
from __future__ import annotations

import io
import os
from datetime import date, datetime
from typing import Any

import xlsxwriter

from i18n import t

DENOMINATIONS = [10000, 5000, 2000, 1000, 500, 100, 50, 10, 5, 1]


def filter_entries_by_range(
    entries: list[dict[str, Any]],
    export_range: str = "all",
    reference_date: date | None = None,
) -> list[dict[str, Any]]:
    """Filters history entries based on the specified range: 'all', 'this_month', 'last_month'."""
    if not entries:
        return []

    if export_range == "all":
        return list(entries)

    ref = reference_date or date.today()
    this_year = ref.year
    this_month = ref.month

    if this_month == 1:
        last_year = this_year - 1
        last_month = 12
    else:
        last_year = this_year
        last_month = this_month - 1

    filtered: list[dict[str, Any]] = []
    for entry in entries:
        ts = entry.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts)
        except Exception:
            continue

        if export_range == "this_month":
            if dt.year == this_year and dt.month == this_month:
                filtered.append(entry)
        elif export_range == "last_month":
            if dt.year == last_year and dt.month == last_month:
                filtered.append(entry)

    return filtered


def resolve_export_directory() -> tuple[str, str]:
    """Finds the most accessible, user-visible export directory on the platform.

    Returns:
        (actual_directory_path, user_friendly_display_location)
    """
    candidates = [
        ("/storage/emulated/0/Download/CoinTrans", "Downloads/CoinTrans"),
        ("/sdcard/Download/CoinTrans", "Downloads/CoinTrans"),
        (os.path.join(os.path.expanduser("~"), "Downloads", "CoinTrans"), "Downloads/CoinTrans"),
        (os.path.join(os.path.expanduser("~"), "Downloads"), "Downloads"),
        ("/storage/emulated/0/Android/data/com.sirr/files/Download", "Android/data/com.sirr/files/Download"),
    ]

    for dir_path, display_name in candidates:
        try:
            os.makedirs(dir_path, exist_ok=True)
            test_file = os.path.join(dir_path, ".test_write")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return dir_path, display_name
        except Exception:
            continue

    base = os.environ.get("FLET_APP_STORAGE_DATA") or os.path.expanduser("~")
    fallback = os.path.join(base, "exports")
    try:
        os.makedirs(fallback, exist_ok=True)
    except Exception:
        pass
    return fallback, "Downloads/CoinTrans"


def get_unique_export_filename(
    directory: str,
    export_date: date | None = None,
) -> tuple[str, str]:
    """Generates a unique export filename appending -2, -3 if file exists.

    Returns:
        (filename, full_file_path)
    """
    ref_date = export_date or date.today()
    date_str = ref_date.isoformat()
    base_name = f"cointrans_{date_str}.xlsx"
    candidate_path = os.path.join(directory, base_name)
    if not os.path.exists(candidate_path):
        return base_name, candidate_path

    i = 2
    while True:
        candidate_name = f"cointrans_{date_str}-{i}.xlsx"
        candidate_path = os.path.join(directory, candidate_name)
        if not os.path.exists(candidate_path):
            return candidate_name, candidate_path
        i += 1


def _format_breakdown_str(breakdown: dict[str, int]) -> str:
    """Formats denomination dictionary into compact text, e.g. '1000x1, 100x2'."""
    if not breakdown:
        return "-"
    parts = []
    # Sort descending by denomination
    sorted_items = sorted(
        ((int(k), int(v)) for k, v in breakdown.items() if int(v) > 0),
        key=lambda x: x[0],
        reverse=True,
    )
    for denom, count in sorted_items:
        parts.append(f"{denom}x{count}")
    return ", ".join(parts) if parts else "-"


def generate_history_workbook(
    entries: list[dict[str, Any]],
    lang: str = "en",
    export_range: str = "all",
    output_path: str | None = None,
    reference_date: date | None = None,
) -> bytes | str | None:
    """Generates an Excel workbook (.xlsx) from history entries.

    Args:
        entries: List of history entry dicts.
        lang: Target language code ('en', 'ja', 'vi').
        export_range: 'all', 'this_month', or 'last_month'.
        output_path: Optional file path to write to. If None, returns bytes.
        reference_date: Optional reference date for month calculations (defaults to today).

    Returns:
        File path if output_path was given, or bytes if output_path was None.
        Returns None if no entries match the selected range.
    """
    filtered = filter_entries_by_range(entries, export_range, reference_date)
    if not filtered:
        return None

    # Prepare output buffer or file
    output_buffer = None
    target: Any = output_path
    if output_path is None:
        output_buffer = io.BytesIO()
        target = output_buffer

    workbook = xlsxwriter.Workbook(target, {"remove_timezone": True})

    # Styles & Formats
    header_fmt = workbook.add_format({
        "bold": True,
        "bg_color": "#00897B",  # Teal 600
        "font_color": "#FFFFFF",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
    })
    sub_header_fmt = workbook.add_format({
        "bold": True,
        "bg_color": "#E0F2F1",  # Teal 50
        "font_color": "#004D40",  # Teal 900
        "align": "left",
        "valign": "vcenter",
        "border": 1,
    })
    bold_fmt = workbook.add_format({"bold": True})
    total_row_fmt = workbook.add_format({
        "bold": True,
        "top": 1,
        "bottom": 6,  # Double line
        "bg_color": "#F5F5F5",
    })
    total_currency_fmt = workbook.add_format({
        "bold": True,
        "top": 1,
        "bottom": 6,
        "num_format": "#,##0",
        "bg_color": "#F5F5F5",
    })
    currency_fmt = workbook.add_format({"num_format": "#,##0"})
    int_fmt = workbook.add_format({"num_format": "#,##0", "align": "right"})
    date_fmt = workbook.add_format({"num_format": "yyyy-mm-dd", "align": "center"})
    time_fmt = workbook.add_format({"align": "center"})
    text_center_fmt = workbook.add_format({"align": "center"})

    # Localized Sheet Names (max 31 chars, no invalid chars : \ / ? * [ ])
    sheet_payments_title = t("export_sheet_payments", lang)[:31]
    sheet_details_title = t("export_sheet_details", lang)[:31]
    sheet_summary_title = t("export_sheet_summary", lang)[:31]

    # =========================================================================
    # SHEET 1: PAYMENTS
    # =========================================================================
    ws_payments = workbook.add_worksheet(sheet_payments_title)
    ws_payments.freeze_panes(1, 0)

    payments_headers = [
        t("export_col_date", lang),
        t("export_col_time", lang),
        t("export_col_name", lang),
        t("export_col_bill", lang),
        t("export_col_total_paid", lang),
        t("export_col_change", lang),
        t("export_col_mode", lang),
        t("export_col_wallet_after", lang),
        t("export_col_paid_breakdown", lang),
        t("export_col_change_breakdown", lang),
    ]

    for col_idx, h in enumerate(payments_headers):
        ws_payments.write(0, col_idx, h, header_fmt)

    # Sort filtered entries chronologically (oldest to newest) for standard accounting order
    chronological_entries = sorted(
        filtered,
        key=lambda e: e.get("timestamp", ""),
    )

    for row_idx, entry in enumerate(chronological_entries, start=1):
        ts = entry.get("timestamp", "")
        dt_val = None
        time_str = ""
        try:
            parsed = datetime.fromisoformat(ts)
            dt_val = date(parsed.year, parsed.month, parsed.day)
            time_str = parsed.strftime("%H:%M")
        except Exception:
            pass

        bill = entry.get("bill", 0)
        total_paid = entry.get("total_paid", 0)
        change = entry.get("change", 0)
        mode = entry.get("mode", "fast")
        mode_label = (
            t("history_mode_notes", lang)
            if mode == "optimize_notes"
            else t("history_mode_fast", lang)
        )
        wallet_after = entry.get("wallet_total_after", 0)
        paid_text = _format_breakdown_str(entry.get("pay", {}))
        change_text = _format_breakdown_str(entry.get("change_breakdown", {}))
        custom_name = entry.get("name") or ""

        if dt_val:
            ws_payments.write_datetime(row_idx, 0, dt_val, date_fmt)
        else:
            ws_payments.write(row_idx, 0, ts[:10], date_fmt)

        ws_payments.write(row_idx, 1, time_str, time_fmt)
        ws_payments.write(row_idx, 2, custom_name)
        ws_payments.write_number(row_idx, 3, bill, currency_fmt)
        ws_payments.write_number(row_idx, 4, total_paid, currency_fmt)
        ws_payments.write_number(row_idx, 5, change, currency_fmt)
        ws_payments.write(row_idx, 6, mode_label, text_center_fmt)
        ws_payments.write_number(row_idx, 7, wallet_after, currency_fmt)
        ws_payments.write(row_idx, 8, paid_text)
        ws_payments.write(row_idx, 9, change_text)

    # Autofilter across all payments columns
    num_payment_rows = len(chronological_entries)
    ws_payments.autofilter(0, 0, num_payment_rows, len(payments_headers) - 1)

    # Set column widths
    ws_payments.set_column(0, 0, 13)  # Date
    ws_payments.set_column(1, 1, 9)   # Time
    ws_payments.set_column(2, 2, 22)  # Name
    ws_payments.set_column(3, 5, 13)  # Bill, Paid, Change
    ws_payments.set_column(6, 6, 18)  # Mode
    ws_payments.set_column(7, 7, 16)  # Wallet After
    ws_payments.set_column(8, 9, 25)  # Breakdowns

    # =========================================================================
    # SHEET 2: DETAILS (Long/tidy format for Pivot Tables)
    # =========================================================================
    ws_details = workbook.add_worksheet(sheet_details_title)
    ws_details.freeze_panes(1, 0)

    details_headers = [
        t("export_col_payment_id", lang),
        t("export_col_date", lang),
        t("export_col_name", lang),
        t("export_col_kind", lang),
        t("export_col_denom", lang),
        t("export_col_count", lang),
        t("export_col_subtotal", lang),
    ]

    for col_idx, h in enumerate(details_headers):
        ws_details.write(0, col_idx, h, header_fmt)

    kind_paid_label = t("export_kind_paid", lang)
    kind_change_label = t("export_kind_change", lang)

    detail_row_idx = 1
    for entry in chronological_entries:
        entry_id = entry.get("id", "")
        custom_name = entry.get("name") or ""
        ts = entry.get("timestamp", "")
        dt_val = None
        try:
            parsed = datetime.fromisoformat(ts)
            dt_val = date(parsed.year, parsed.month, parsed.day)
        except Exception:
            pass

        # Paid items
        for denom in DENOMINATIONS:
            count = int(entry.get("pay", {}).get(str(denom), 0))
            if count > 0:
                subtotal = denom * count
                ws_details.write(detail_row_idx, 0, entry_id)
                if dt_val:
                    ws_details.write_datetime(detail_row_idx, 1, dt_val, date_fmt)
                else:
                    ws_details.write(detail_row_idx, 1, ts[:10], date_fmt)
                ws_details.write(detail_row_idx, 2, custom_name)
                ws_details.write(detail_row_idx, 3, kind_paid_label, text_center_fmt)
                ws_details.write_number(detail_row_idx, 4, denom, currency_fmt)
                ws_details.write_number(detail_row_idx, 5, count, int_fmt)
                ws_details.write_number(detail_row_idx, 6, subtotal, currency_fmt)
                detail_row_idx += 1

        # Change items
        for denom in DENOMINATIONS:
            count = int(entry.get("change_breakdown", {}).get(str(denom), 0))
            if count > 0:
                subtotal = denom * count
                ws_details.write(detail_row_idx, 0, entry_id)
                if dt_val:
                    ws_details.write_datetime(detail_row_idx, 1, dt_val, date_fmt)
                else:
                    ws_details.write(detail_row_idx, 1, ts[:10], date_fmt)
                ws_details.write(detail_row_idx, 2, custom_name)
                ws_details.write(detail_row_idx, 3, kind_change_label, text_center_fmt)
                ws_details.write_number(detail_row_idx, 4, denom, currency_fmt)
                ws_details.write_number(detail_row_idx, 5, count, int_fmt)
                ws_details.write_number(detail_row_idx, 6, subtotal, currency_fmt)
                detail_row_idx += 1

    if detail_row_idx > 1:
        ws_details.autofilter(0, 0, detail_row_idx - 1, len(details_headers) - 1)

    ws_details.set_column(0, 0, 38)  # Payment ID UUID
    ws_details.set_column(1, 1, 13)  # Date
    ws_details.set_column(2, 2, 22)  # Name
    ws_details.set_column(3, 3, 12)  # Kind
    ws_details.set_column(4, 4, 14)  # Denomination
    ws_details.set_column(5, 5, 10)  # Count
    ws_details.set_column(6, 6, 14)  # Subtotal

    # =========================================================================
    # SHEET 3: SUMMARY
    # =========================================================================
    ws_summary = workbook.add_worksheet(sheet_summary_title)
    ws_summary.freeze_panes(2, 0)

    # Monthly aggregation
    monthly_data: dict[str, dict[str, int]] = {}
    denom_paid: dict[int, int] = {d: 0 for d in DENOMINATIONS}
    denom_change: dict[int, int] = {d: 0 for d in DENOMINATIONS}

    for entry in chronological_entries:
        ts = entry.get("timestamp", "")
        month_key = ts[:7] if len(ts) >= 7 else "Unknown"

        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "count": 0,
                "bill": 0,
                "paid": 0,
                "change": 0,
            }

        bill = entry.get("bill", 0)
        paid = entry.get("total_paid", 0)
        chg = entry.get("change", 0)

        monthly_data[month_key]["count"] += 1
        monthly_data[month_key]["bill"] += bill
        monthly_data[month_key]["paid"] += paid
        monthly_data[month_key]["change"] += chg

        for d_str, count in entry.get("pay", {}).items():
            d = int(d_str)
            if d in denom_paid:
                denom_paid[d] += int(count)

        for d_str, count in entry.get("change_breakdown", {}).items():
            d = int(d_str)
            if d in denom_change:
                denom_change[d] += int(count)

    # Section 1: Monthly Summary Table
    ws_summary.merge_range(0, 0, 0, 5, t("export_summary_monthly_title", lang), sub_header_fmt)

    monthly_headers = [
        t("export_col_month", lang),
        t("export_col_num_payments", lang),
        t("export_col_total_bill", lang),
        t("export_col_total_paid", lang),
        t("export_col_total_change", lang),
        t("export_col_avg_bill", lang),
    ]
    for col_idx, h in enumerate(monthly_headers):
        ws_summary.write(1, col_idx, h, header_fmt)

    sum_row = 2
    total_all_count = 0
    total_all_bill = 0
    total_all_paid = 0
    total_all_change = 0

    for m_key in sorted(monthly_data.keys()):
        stat = monthly_data[m_key]
        c = stat["count"]
        b = stat["bill"]
        p = stat["paid"]
        ch = stat["change"]
        avg = round(b / c) if c > 0 else 0

        total_all_count += c
        total_all_bill += b
        total_all_paid += p
        total_all_change += ch

        ws_summary.write(sum_row, 0, m_key, text_center_fmt)
        ws_summary.write_number(sum_row, 1, c, int_fmt)
        ws_summary.write_number(sum_row, 2, b, currency_fmt)
        ws_summary.write_number(sum_row, 3, p, currency_fmt)
        ws_summary.write_number(sum_row, 4, ch, currency_fmt)
        ws_summary.write_number(sum_row, 5, avg, currency_fmt)
        sum_row += 1

    # Totals row for monthly table
    overall_avg = round(total_all_bill / total_all_count) if total_all_count > 0 else 0
    ws_summary.write(sum_row, 0, t("export_total_row", lang), total_row_fmt)
    ws_summary.write_number(sum_row, 1, total_all_count, total_currency_fmt)
    ws_summary.write_number(sum_row, 2, total_all_bill, total_currency_fmt)
    ws_summary.write_number(sum_row, 3, total_all_paid, total_currency_fmt)
    ws_summary.write_number(sum_row, 4, total_all_change, total_currency_fmt)
    ws_summary.write_number(sum_row, 5, overall_avg, total_currency_fmt)

    # Section 2: Denomination Usage Breakdown
    denom_start_row = sum_row + 3
    ws_summary.merge_range(
        denom_start_row, 0, denom_start_row, 5,
        t("export_summary_denom_title", lang),
        sub_header_fmt,
    )

    denom_headers = [
        t("export_col_denom", lang),
        t("export_col_handed_count", lang),
        t("export_col_handed_subtotal", lang),
        t("export_col_received_count", lang),
        t("export_col_received_subtotal", lang),
        t("export_col_net_count", lang),
    ]
    for col_idx, h in enumerate(denom_headers):
        ws_summary.write(denom_start_row + 1, col_idx, h, header_fmt)

    d_row = denom_start_row + 2
    total_handed_count = 0
    total_handed_subtotal = 0
    total_received_count = 0
    total_received_subtotal = 0

    for d in DENOMINATIONS:
        h_cnt = denom_paid.get(d, 0)
        h_sub = h_cnt * d
        r_cnt = denom_change.get(d, 0)
        r_sub = r_cnt * d
        net_cnt = r_cnt - h_cnt

        total_handed_count += h_cnt
        total_handed_subtotal += h_sub
        total_received_count += r_cnt
        total_received_subtotal += r_sub

        ws_summary.write_number(d_row, 0, d, currency_fmt)
        ws_summary.write_number(d_row, 1, h_cnt, int_fmt)
        ws_summary.write_number(d_row, 2, h_sub, currency_fmt)
        ws_summary.write_number(d_row, 3, r_cnt, int_fmt)
        ws_summary.write_number(d_row, 4, r_sub, currency_fmt)
        ws_summary.write_number(d_row, 5, net_cnt, int_fmt)
        d_row += 1

    # Totals row for denomination table
    ws_summary.write(d_row, 0, t("export_total_row", lang), total_row_fmt)
    ws_summary.write_number(d_row, 1, total_handed_count, total_currency_fmt)
    ws_summary.write_number(d_row, 2, total_handed_subtotal, total_currency_fmt)
    ws_summary.write_number(d_row, 3, total_received_count, total_currency_fmt)
    ws_summary.write_number(d_row, 4, total_received_subtotal, total_currency_fmt)
    ws_summary.write_number(d_row, 5, total_received_count - total_handed_count, total_currency_fmt)

    ws_summary.set_column(0, 0, 16)
    ws_summary.set_column(1, 5, 18)

    workbook.close()

    if output_path is not None:
        return output_path

    if output_buffer is not None:
        return output_buffer.getvalue()

    return None

