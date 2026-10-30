"""Internationalization (i18n) module for CoinTrans.

Supports English (default), Japanese, and Vietnamese.
Pure Python, zero external dependencies.
"""
import os

SUPPORTED_LANGUAGES = ["en", "ja", "vi"]

TRANSLATIONS = {
    "en": {
        # Language display name
        "lang_name": "English",

        # Units
        "unit_bill_single": "bill",
        "unit_bill_plural": "bills",
        "unit_coin_single": "coin",
        "unit_coin_plural": "coins",

        # Navigation
        "nav_wallet": "Wallet",
        "nav_pay": "Pay",
        "nav_history": "History",

        # Wallet screen
        "wallet_summary_title": "Total Wallet Balance",
        "wallet_breakdown": "Banknotes: {notes}  |  Coins: {coins}",
        "settings_tooltip": "Language Settings",
        "language_picker_title": "Select Language",
        "close": "Close",
        "subtotal_format": "= {amount}",

        # Pay screen
        "bill_label": "Invoice Amount",
        "bill_hint": "0",
        "mode_switch_label": "Optimize banknotes (coin cleanup)",
        "mode_hint_fast": "Default: Fewest bills & coins (fast)",
        "mode_hint_notes": "Active: Prioritize spending loose coins",
        "error_insufficient": "Not enough money in your wallet!",
        "give_title": "GIVE TO CASHIER",
        "change_title": "CHANGE",
        "exact_change_none": "¥0 (Exact amount, no change)",
        "confirm_paid": "Confirm Payment",

        # History screen
        "history_title": "Payment History",
        "history_summary_title": "This Month ({month})",
        "history_summary_spent": "Total Spent: {amount}",
        "history_summary_count": "{count} payment(s)",
        "history_clear_all": "Clear All",
        "history_empty_title": "No payment history yet",
        "history_empty_subtitle": "Confirmed payments will be recorded here",
        "history_today": "Today",
        "history_yesterday": "Yesterday",
        "history_mode_fast": "Fast Mode",
        "history_mode_notes": "Optimize Notes",
        "history_wallet_after": "Wallet after: {amount}",
        "history_undo_button": "Undo Payment",
        "history_delete_button": "Delete",
        "history_bill_label": "Bill: {amount}",
        "history_paid_label": "Paid: {amount}",
        "history_change_label": "Change: {amount}",

        # Dialogs
        "undo_dialog_title": "Undo Last Payment?",
        "undo_dialog_content": "This will reverse the paid coins and change back into your wallet.",
        "clear_dialog_title": "Clear All History?",
        "clear_dialog_content": "All payment records will be permanently deleted. Wallet balance will not change.",
        "dialog_confirm": "Confirm",
        "dialog_cancel": "Cancel",
    },
    "ja": {
        # Language display name
        "lang_name": "日本語",

        # Units
        "unit_bill_single": "枚",
        "unit_bill_plural": "枚",
        "unit_coin_single": "枚",
        "unit_coin_plural": "枚",

        # Navigation
        "nav_wallet": "財布",
        "nav_pay": "支払い",
        "nav_history": "履歴",

        # Wallet screen
        "wallet_summary_title": "財布の残高合計",
        "wallet_breakdown": "紙幣: {notes}  |  硬貨: {coins}",
        "settings_tooltip": "言語設定",
        "language_picker_title": "言語を選択",
        "close": "閉じる",
        "subtotal_format": "= {amount}",

        # Pay screen
        "bill_label": "請求額",
        "bill_hint": "0",
        "mode_switch_label": "紙幣優先（硬貨を減らす）",
        "mode_hint_fast": "デフォルト: 出し入れ枚数を最小化（最速）",
        "mode_hint_notes": "適用中: 硬貨をまとめて多く渡す",
        "error_insufficient": "財布の残高が足りません",
        "give_title": "レジに渡す",
        "change_title": "お釣り",
        "exact_change_none": "0円（お釣りなし）",
        "confirm_paid": "支払い完了",

        # History screen
        "history_title": "支払い履歴",
        "history_summary_title": "今月の支出 ({month})",
        "history_summary_spent": "総支出: {amount}",
        "history_summary_count": "{count}回の支払い",
        "history_clear_all": "履歴を全削除",
        "history_empty_title": "支払い履歴はありません",
        "history_empty_subtitle": "支払いを完了するとここに記録されます",
        "history_today": "今日",
        "history_yesterday": "昨日",
        "history_mode_fast": "最速モード",
        "history_mode_notes": "紙幣優先モード",
        "history_wallet_after": "支払い後の残高: {amount}",
        "history_undo_button": "支払いを元に戻す",
        "history_delete_button": "削除",
        "history_bill_label": "請求額: {amount}",
        "history_paid_label": "支払額: {amount}",
        "history_change_label": "お釣り: {amount}",

        # Dialogs
        "undo_dialog_title": "直前の支払いを元に戻しますか？",
        "undo_dialog_content": "支払った金額とお釣りを財布の残高に戻し、この履歴を削除します。",
        "clear_dialog_title": "すべての履歴を削除しますか？",
        "clear_dialog_content": "すべての支払い記録が削除されます。財布の残高は変更されません。",
        "dialog_confirm": "実行",
        "dialog_cancel": "キャンセル",
    },
    "vi": {
        # Language display name
        "lang_name": "Tiếng Việt",

        # Units
        "unit_bill_single": "tờ",
        "unit_bill_plural": "tờ",
        "unit_coin_single": "đồng",
        "unit_coin_plural": "đồng",

        # Navigation
        "nav_wallet": "Ví",
        "nav_pay": "Trả tiền",
        "nav_history": "Lịch sử",

        # Wallet screen
        "wallet_summary_title": "Tổng số dư trong ví",
        "wallet_breakdown": "Tiền giấy: {notes}  |  Tiền xu: {coins}",
        "settings_tooltip": "Cài đặt ngôn ngữ",
        "language_picker_title": "Chọn ngôn ngữ",
        "close": "Đóng",
        "subtotal_format": "= {amount}",

        # Pay screen
        "bill_label": "Số tiền hóa đơn",
        "bill_hint": "0",
        "mode_switch_label": "Tối ưu tiền giấy (dọn xu)",
        "mode_hint_fast": "Mặc định: Đưa & nhận ít tờ/xu nhất (nhanh)",
        "mode_hint_notes": "Đang bật: Ưu tiên tống khứ xu để dọn ví",
        "error_insufficient": "Không đủ tiền trong ví để trả hóa đơn này!",
        "give_title": "ĐƯA CHO THU NGÂN",
        "change_title": "NHẬN LẠI",
        "exact_change_none": "0¥ (Trả vừa đủ, không thối)",
        "confirm_paid": "Xác nhận đã trả",

        # History screen
        "history_title": "Lịch sử giao dịch",
        "history_summary_title": "Chi tiêu tháng {month}",
        "history_summary_spent": "Tổng chi tiêu: {amount}",
        "history_summary_count": "{count} giao dịch",
        "history_clear_all": "Xóa toàn bộ",
        "history_empty_title": "Chưa có lịch sử giao dịch",
        "history_empty_subtitle": "Các giao dịch đã thanh toán sẽ hiển thị tại đây",
        "history_today": "Hôm nay",
        "history_yesterday": "Hôm qua",
        "history_mode_fast": "Chế độ nhanh",
        "history_mode_notes": "Tối ưu tiền giấy",
        "history_wallet_after": "Số dư sau khi trả: {amount}",
        "history_undo_button": "Hoàn tác giao dịch",
        "history_delete_button": "Xóa",
        "history_bill_label": "Hóa đơn: {amount}",
        "history_paid_label": "Đã đưa: {amount}",
        "history_change_label": "Thối lại: {amount}",

        # Dialogs
        "undo_dialog_title": "Hoàn tác giao dịch gần nhất?",
        "undo_dialog_content": "Thao tác này sẽ hoàn lại tiền đưa và tiền thối vào ví của bạn.",
        "clear_dialog_title": "Xóa toàn bộ lịch sử?",
        "clear_dialog_content": "Toàn bộ lịch sử sẽ bị xóa vĩnh viễn. Số dư trong ví sẽ không thay đổi.",
        "dialog_confirm": "Xác nhận",
        "dialog_cancel": "Hủy",
    },
}

def t(key: str, lang: str = "en", **params) -> str:
    """Translates a key into the specified language with fallback to English."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    template = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
    if params:
        try:
            return template.format(**params)
        except (KeyError, IndexError):
            return template
    return template

def format_count_unit(count: int, is_note: bool, lang: str = "en") -> str:
    """Formats count with language-specific unit words (including English singular/plural)."""
    if is_note:
        unit_key = "unit_bill_single" if count == 1 else "unit_bill_plural"
    else:
        unit_key = "unit_coin_single" if count == 1 else "unit_coin_plural"
    unit_str = t(unit_key, lang)
    if lang == "ja":
        return f"{count}{unit_str}"
    return f"{count} {unit_str}"

def format_breakdown_summary(notes_count: int, coins_count: int, lang: str = "en") -> str:
    """Formats the wallet summary breakdown line."""
    notes_str = format_count_unit(notes_count, is_note=True, lang=lang)
    coins_str = format_count_unit(coins_count, is_note=False, lang=lang)
    return t("wallet_breakdown", lang, notes=notes_str, coins=coins_str)

def detect_device_language() -> str:
    """Detects system language code, returning 'en', 'ja', or 'vi'."""
    try:
        import locale
        loc = locale.getdefaultlocale()[0]
        if not loc:
            loc = locale.getlocale()[0]
        if loc:
            code = loc.split("_")[0].lower()
            if code in ("en", "ja", "vi"):
                return code
    except Exception:
        pass
    for env_var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(env_var, "")
        if val:
            code = val.split("_")[0].split(".")[0].lower()
            if code in ("en", "ja", "vi"):
                return code
    return "en"
