import io
import os
import re
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from core import suggest, DENOMS, load_settings
from i18n import (
    TRANSLATIONS,
    t,
    format_count_unit,
    format_breakdown_summary,
    detect_device_language,
)
from history import (
    create_entry,
    add_entry,
    delete_entry,
    undo_last_payment,
    clear_history,
    get_monthly_summary,
    load_history,
    save_history,
    MAX_HISTORY_ENTRIES,
)
from export import (
    generate_history_workbook,
    filter_entries_by_range,
    _format_breakdown_str,
)

# ==========================================
# 1. Core Algorithm Tests
# ==========================================
# Test 1: Bill 630¥ (Fast mode by default)
w1 = {d: 0 for d in DENOMS}
w1.update({1000: 2, 500: 0, 100: 4, 50: 1, 10: 3, 5: 1, 1: 2})
r1 = suggest(w1, 630, prefer_notes=False)
print("Test 1 (630¥ fast):", r1["pay"], "-> change:", r1["change"])
assert r1["pay"] == {1000: 1, 100: 1, 10: 3}
assert r1["change"] == {500: 1}

# Test 2: Bill 10¥ (Fast mode: pays exact single 10¥ coin)
w2 = {d: 0 for d in DENOMS}
w2.update({1000: 2, 500: 1, 100: 5, 50: 1, 10: 5, 5: 1, 1: 5})
r2_fast = suggest(w2, 10, prefer_notes=False)
print("Test 2 (10¥ fast):", r2_fast["pay"], "-> change:", r2_fast["change"])
assert r2_fast["pay"] == {10: 1}
assert r2_fast["change"] == {}

# Test 3: Bill 10¥ (Note-optimization mode: sheds coins)
r2_notes = suggest(w2, 10, prefer_notes=True)
print("Test 3 (10¥ notes):", r2_notes["pay"], "-> change:", r2_notes["change"])

# Test 4: Insufficient funds returns None
assert suggest({d: 0 for d in DENOMS} | {100: 2}, 630) is None

# ==========================================
# 2. Internationalization (i18n) Tests
# ==========================================
def extract_placeholders(s: str) -> set[str]:
    return set(re.findall(r"\{([a-zA-Z0-9_]+)\}", s))

langs = ["en", "ja", "vi"]
for lang in langs:
    assert lang in TRANSLATIONS, f"Missing language dictionary: {lang}"

en_keys = set(TRANSLATIONS["en"].keys())
ja_keys = set(TRANSLATIONS["ja"].keys())
vi_keys = set(TRANSLATIONS["vi"].keys())

# Check exact key parity across all languages
diff_ja = en_keys.symmetric_difference(ja_keys)
assert not diff_ja, f"Key mismatch between English and Japanese: {diff_ja}"

diff_vi = en_keys.symmetric_difference(vi_keys)
assert not diff_vi, f"Key mismatch between English and Vietnamese: {diff_vi}"

# Check exact placeholder parity for every key
for key in sorted(en_keys):
    en_placeholders = extract_placeholders(TRANSLATIONS["en"][key])
    ja_placeholders = extract_placeholders(TRANSLATIONS["ja"][key])
    vi_placeholders = extract_placeholders(TRANSLATIONS["vi"][key])
    assert en_placeholders == ja_placeholders, (
        f"Placeholder mismatch for '{key}' between English {en_placeholders} and Japanese {ja_placeholders}"
    )
    assert en_placeholders == vi_placeholders, (
        f"Placeholder mismatch for '{key}' between English {en_placeholders} and Vietnamese {vi_placeholders}"
    )

# Test translation function and fallback
assert t("nav_wallet", "en") == "Wallet"
assert t("nav_wallet", "ja") == "財布"
assert t("nav_wallet", "vi") == TRANSLATIONS["vi"]["nav_wallet"]
assert t("nav_wallet", "fr") == "Wallet"
assert t("non_existent_key_xyz", "en") == "non_existent_key_xyz"

# Test formatting placeholders
assert t("wallet_breakdown", "en", notes="2 bills", coins="5 coins") == "Banknotes: 2 bills  |  Coins: 5 coins"
assert t("wallet_breakdown", "ja", notes="2枚", coins="5枚") == "紙幣: 2枚  |  硬貨: 5枚"

# Test unit word singular/plural handling
assert format_count_unit(1, is_note=True, lang="en") == "1 bill"
assert format_count_unit(2, is_note=True, lang="en") == "2 bills"
assert format_count_unit(1, is_note=False, lang="en") == "1 coin"
assert format_count_unit(5, is_note=False, lang="en") == "5 coins"

assert format_count_unit(1, is_note=True, lang="ja") == "1枚"
assert format_count_unit(5, is_note=False, lang="ja") == "5枚"

assert format_count_unit(1, is_note=True, lang="vi") == f"1 {TRANSLATIONS['vi']['unit_bill_single']}"
assert format_count_unit(5, is_note=False, lang="vi") == f"5 {TRANSLATIONS['vi']['unit_coin_plural']}"

# Test format_breakdown_summary
assert format_breakdown_summary(1, 1, "en") == "Banknotes: 1 bill  |  Coins: 1 coin"
assert format_breakdown_summary(3, 4, "ja") == "紙幣: 3枚  |  硬貨: 4枚"

# Test settings loading with language fallback
settings = load_settings()
assert "language" in settings
assert settings["language"] in ("en", "ja", "vi")

# ==========================================
# 3. Payment History Tests
# ==========================================
with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_hist_file = os.path.join(tmp_dir, "test_history.json")

    # Test: Corrupted JSON file returns empty list
    with open(tmp_hist_file, "w", encoding="utf-8") as f:
        f.write("{invalid json content!@@#")
    assert load_history(tmp_hist_file) == []

    # Test: Non-existent file returns empty list
    non_existent = os.path.join(tmp_dir, "non_existent.json")
    assert load_history(non_existent) == []

    # Test: Adding an entry
    entries = []
    entry1 = create_entry(
        bill=630,
        total_paid=1130,
        change=500,
        pay={1000: 1, 100: 1, 10: 3},
        change_breakdown={500: 1},
        mode="fast",
        wallet_total_after=4500,
        timestamp="2026-10-15T14:30:00",
    )
    entries = add_entry(entries, entry1, path=tmp_hist_file)
    assert len(entries) == 1
    loaded = load_history(tmp_hist_file)
    assert len(loaded) == 1
    assert loaded[0]["bill"] == 630
    assert loaded[0]["change"] == 500
    assert loaded[0]["mode"] == "fast"

    # Test: Adding second entry (newest first)
    entry2 = create_entry(
        bill=250,
        total_paid=300,
        change=50,
        pay={100: 3},
        change_breakdown={50: 1},
        mode="optimize_notes",
        wallet_total_after=4250,
        timestamp="2026-10-20T10:00:00",
    )
    entries = add_entry(entries, entry2, path=tmp_hist_file)
    assert len(entries) == 2
    assert entries[0]["bill"] == 250
    assert entries[1]["bill"] == 630

    # Test: Monthly summary calculation
    # Both entry1 and entry2 are in 2026-10
    summary_oct = get_monthly_summary(entries, year=2026, month=10)
    assert summary_oct["total_spent"] == 630 + 250
    assert summary_oct["payment_count"] == 2

    # Month with no transactions
    summary_nov = get_monthly_summary(entries, year=2026, month=11)
    assert summary_nov["total_spent"] == 0
    assert summary_nov["payment_count"] == 0

    # Test: 500-entry cap
    many_entries = []
    for i in range(550):
        e = create_entry(
            bill=100 + i,
            total_paid=100 + i,
            change=0,
            pay={100: 1},
            change_breakdown={},
            mode="fast",
            wallet_total_after=1000,
        )
        many_entries.append(e)
    save_history(many_entries, path=tmp_hist_file)
    capped_entries = load_history(tmp_hist_file)
    assert len(capped_entries) == MAX_HISTORY_ENTRIES
    assert len(capped_entries) == 500

    # Test: Deleting an entry
    entries_to_delete = load_history(tmp_hist_file)
    id_to_delete = entries_to_delete[0]["id"]
    entries_after_del = delete_entry(entries_to_delete, id_to_delete, path=tmp_hist_file)
    assert len(entries_after_del) == 499
    assert all(e["id"] != id_to_delete for e in entries_after_del)

    # Test: Clear all history
    cleared = clear_history(path=tmp_hist_file)
    assert cleared == []
    assert load_history(tmp_hist_file) == []

    # Test: Undo restores the exact wallet
    initial_wallet = {10000: 1, 5000: 1, 1000: 2, 500: 0, 100: 4, 50: 1, 10: 3, 5: 1, 1: 2}
    bill = 630
    sugg = suggest(initial_wallet, bill, prefer_notes=False)
    # Payment: pay {1000: 1, 100: 1, 10: 3}, change {500: 1}
    wallet_after_pay = dict(sugg["after"])
    assert wallet_after_pay != initial_wallet

    hist_entries = []
    hist_entry = create_entry(
        bill=bill,
        total_paid=sugg["total_paid"],
        change=sum(d * n for d, n in sugg["change"].items()),
        pay=sugg["pay"],
        change_breakdown=sugg["change"],
        mode="fast",
        wallet_total_after=sum(d * n for d, n in wallet_after_pay.items()),
    )
    hist_entries = add_entry(hist_entries, hist_entry, path=tmp_hist_file)
    assert len(hist_entries) == 1

    # Execute undo
    restored_entries, restored_wallet = undo_last_payment(hist_entries, wallet_after_pay, path=tmp_hist_file)
    assert restored_entries == []
    assert restored_wallet == initial_wallet
    print("Undo accurately restored wallet to:", restored_wallet)

# ==========================================
# 4. Excel Export Tests
# ==========================================
sample_oct = {
    "id": "entry-october-1",
    "timestamp": "2026-10-15T14:30:00",
    "bill": 630,
    "total_paid": 1130,
    "change": 500,
    "pay": {"1000": 1, "100": 1, "10": 3},
    "change_breakdown": {"500": 1},
    "mode": "fast",
    "wallet_total_after": 4500,
}
sample_sep = {
    "id": "entry-september-1",
    "timestamp": "2026-09-20T10:15:00",
    "bill": 1200,
    "total_paid": 2000,
    "change": 800,
    "pay": {"1000": 2},
    "change_breakdown": {"500": 1, "100": 3},
    "mode": "optimize_notes",
    "wallet_total_after": 3300,
}
test_entries = [sample_oct, sample_sep]
ref_date = date(2026, 10, 31)

# Range filter tests
assert len(filter_entries_by_range(test_entries, "all", ref_date)) == 2
assert len(filter_entries_by_range(test_entries, "this_month", ref_date)) == 1
assert filter_entries_by_range(test_entries, "this_month", ref_date)[0]["id"] == "entry-october-1"
assert len(filter_entries_by_range(test_entries, "last_month", ref_date)) == 1
assert filter_entries_by_range(test_entries, "last_month", ref_date)[0]["id"] == "entry-september-1"
assert filter_entries_by_range([], "all") == []

# Empty range returns None
assert generate_history_workbook([], lang="en") is None
assert generate_history_workbook([sample_oct], lang="en", export_range="last_month", reference_date=ref_date) is None

# Workbook generation across all supported languages
for lang_code in ["en", "ja", "vi"]:
    wb_bytes = generate_history_workbook(test_entries, lang=lang_code, export_range="all")
    assert wb_bytes is not None and len(wb_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(wb_bytes)) as z:
        # Check sheet names in workbook.xml
        wb_xml = ET.fromstring(z.read("xl/workbook.xml"))
        ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        sheet_names = [s.attrib["name"] for s in wb_xml.findall(".//main:sheet", ns)]
        expected_sheets = [
            t("export_sheet_payments", lang_code)[:31],
            t("export_sheet_details", lang_code)[:31],
            t("export_sheet_summary", lang_code)[:31],
        ]
        assert sheet_names == expected_sheets, f"Sheets mismatch for {lang_code}: {sheet_names} vs {expected_sheets}"

        # Inspect Sheet 1 (Payments): header row + 2 data rows = 3 rows
        sheet1_xml = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rows = sheet1_xml.findall(".//main:row", ns)
        assert len(rows) == 3, f"Expected 3 rows in payments sheet, found {len(rows)}"

        # Inspect Sheet 2 (Details):
        # sample_oct: pay (3 rows), change (1 row) = 4
        # sample_sep: pay (1 row), change (2 rows) = 3
        # Total = header row + 7 detail rows = 8 rows
        sheet2_xml = ET.fromstring(z.read("xl/worksheets/sheet2.xml"))
        detail_rows = sheet2_xml.findall(".//main:row", ns)
        assert len(detail_rows) == 8, f"Expected 8 rows in details sheet, found {len(detail_rows)}"

        # Inspect Sheet 3 (Summary): has monthly summary and denomination tables
        sheet3_xml = ET.fromstring(z.read("xl/worksheets/sheet3.xml"))
        summary_rows = sheet3_xml.findall(".//main:row", ns)
        assert len(summary_rows) > 10, "Summary sheet should contain multiple rows for monthly and denomination blocks"

# File path export test
with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
    tmp_export_path = tmp_file.name

try:
    ret_path = generate_history_workbook(test_entries, lang="en", export_range="all", output_path=tmp_export_path)
    assert ret_path == tmp_export_path
    assert os.path.exists(tmp_export_path)
    assert os.path.getsize(tmp_export_path) > 1000
    print("Excel export file generated successfully at:", tmp_export_path)
finally:
    if os.path.exists(tmp_export_path):
        os.remove(tmp_export_path)

print("Excel export tests passed successfully!")

# ==========================================
# 5. Vietnamese Character Purity Check
# ==========================================
# Verify that no Vietnamese diacritics exist outside the 'vi' dictionary
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
checked_extensions = (".py", ".toml", ".md", ".yml", ".json")

# Build set of Vietnamese characters using codepoints to avoid literal characters in this test file
vietnamese_codepoints = [
    0x00E0, 0x00E1, 0x00E2, 0x00E3, 0x00E8, 0x00E9, 0x00EA, 0x00EC, 0x00ED, 0x00F2,
    0x00F3, 0x00F4, 0x00F5, 0x00F9, 0x00FA, 0x00FD, 0x0102, 0x0103, 0x0110, 0x0111,
    0x0128, 0x0129, 0x0168, 0x0169, 0x01A0, 0x01A1, 0x01AF, 0x01B0,
]
vietnamese_codepoints.extend(range(0x1EA0, 0x1EFA))
vietnamese_chars = {chr(cp) for cp in vietnamese_codepoints}

violations = []
for root, _, files in os.walk(repo_root):
    if ".git" in root or "__pycache__" in root or ".venv" in root:
        continue
    for fname in files:
        if fname.endswith(checked_extensions):
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, repo_root).replace("\\", "/")
            if rel_path == "src/test_core.py":
                continue
            with open(fpath, "r", encoding="utf-8") as fh:
                in_vi_dict = False
                for line_no, line in enumerate(fh, 1):
                    if rel_path == "src/i18n.py":
                        if '"vi": {' in line:
                            in_vi_dict = True
                        elif in_vi_dict and line.strip().startswith("},"):
                            in_vi_dict = False
                        if in_vi_dict:
                            continue

                    found = [c for c in line if c in vietnamese_chars]
                    if found:
                        violations.append((rel_path, line_no, "".join(found), line.strip()))

assert len(violations) == 0, f"Found Vietnamese outside 'vi' dictionary: {violations}"
print("Vietnamese purity test passed: Zero Vietnamese characters outside 'vi' dictionary!")

print("All core, i18n, and history tests passed successfully!")
