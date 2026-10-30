import re
from core import suggest, DENOMS, load_settings
from i18n import TRANSLATIONS, t, format_count_unit, format_breakdown_summary, detect_device_language

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
assert t("nav_wallet", "vi") == "Ví"
# Fallback to English for non-existent language
assert t("nav_wallet", "fr") == "Wallet"
# Fallback to key itself if not in English
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

assert format_count_unit(1, is_note=True, lang="vi") == "1 tờ"
assert format_count_unit(5, is_note=False, lang="vi") == "5 đồng"

# Test format_breakdown_summary
assert format_breakdown_summary(1, 1, "en") == "Banknotes: 1 bill  |  Coins: 1 coin"
assert format_breakdown_summary(3, 4, "ja") == "紙幣: 3枚  |  硬貨: 4枚"

# Test settings loading with language fallback
settings = load_settings()
assert "language" in settings
assert settings["language"] in ("en", "ja", "vi")

print("All core and i18n tests passed successfully!")
