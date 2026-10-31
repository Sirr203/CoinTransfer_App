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
        "history_export_button": "Export to Excel",
        "history_rename_hint": "Tip: Long-press an entry to rename it",
        "history_rename_title": "Rename Payment",
        "history_rename_label": "Custom name (e.g. Lunch, Groceries)",
        "history_rename_save": "Save",
        "history_rename_tooltip": "Rename",

        # Dialogs
        "undo_dialog_title": "Undo Last Payment?",
        "undo_dialog_content": "This will reverse the paid coins and change back into your wallet.",
        "clear_dialog_title": "Clear All History?",
        "clear_dialog_content": "All payment records will be permanently deleted. Wallet balance will not change.",
        "dialog_confirm": "Confirm",
        "dialog_cancel": "Cancel",

        # Excel Export
        "export_dialog_title": "Export Payment History",
        "export_dialog_subtitle": "Select time range to export to Excel (.xlsx):",
        "export_range_all": "All Time",
        "export_range_this_month": "This Month",
        "export_range_last_month": "Last Month",
        "export_button_confirm": "Export",
        "export_empty_message": "No payment history found for the selected time range.",
        "export_success_title": "Export Successful",
        "export_success_message": "Exported {count} transaction(s) to:\n{location}\n\nFile: {filename}\n\nYou can access it using your phone's Files app.",
        "export_warning_title": "Storage Restricted",
        "export_warning_message": "The file was created ({filename}), but could not be saved to your public Downloads folder due to Android system storage restrictions.\n\nThe file is stored in private app storage and cannot be accessed with standard file managers.",
        "export_error_title": "Export Failed",
        "export_error_message": "Failed to create export file: {error}",

        # Excel Sheets & Columns
        "export_sheet_payments": "Payments",
        "export_sheet_details": "Details",
        "export_sheet_summary": "Summary",
        "export_col_date": "Date",
        "export_col_time": "Time",
        "export_col_name": "Name",
        "export_col_bill": "Bill Amount",
        "export_col_total_paid": "Total Paid",
        "export_col_change": "Change",
        "export_col_mode": "Calculation Mode",
        "export_col_wallet_after": "Wallet Balance After",
        "export_col_paid_breakdown": "Paid Breakdown",
        "export_col_change_breakdown": "Change Breakdown",
        "export_col_payment_id": "Payment ID",
        "export_col_kind": "Kind",
        "export_kind_paid": "Paid",
        "export_kind_change": "Change",
        "export_col_denom": "Denomination",
        "export_col_count": "Count",
        "export_col_subtotal": "Subtotal",
        "export_summary_monthly_title": "Monthly Spending Summary",
        "export_col_month": "Month",
        "export_col_num_payments": "Payments Count",
        "export_col_total_bill": "Total Bill",
        "export_col_avg_bill": "Average Bill",
        "export_total_row": "Total",
        "export_summary_denom_title": "Denomination Usage Breakdown",
        "export_col_handed_count": "Handed Over (Count)",
        "export_col_handed_subtotal": "Handed Over (Subtotal)",
        "export_col_received_count": "Received (Count)",
        "export_col_received_subtotal": "Received (Subtotal)",
        "export_col_net_count": "Net Coin Change",
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
        "history_export_button": "Excel出力",
        "history_rename_hint": "ヒント: 履歴を長押しして名前を変更",
        "history_rename_title": "支払いの名前を変更",
        "history_rename_label": "名前（例：ランチ、スーパー）",
        "history_rename_save": "保存",
        "history_rename_tooltip": "名前を変更",

        # Dialogs
        "undo_dialog_title": "直前の支払いを元に戻しますか？",
        "undo_dialog_content": "支払った金額とお釣りを財布の残高に戻し、この履歴を削除します。",
        "clear_dialog_title": "すべての履歴を削除しますか？",
        "clear_dialog_content": "すべての支払い記録が削除されます。財布の残高は変更されません。",
        "dialog_confirm": "実行",
        "dialog_cancel": "キャンセル",

        # Excel Export
        "export_dialog_title": "支払い履歴の書き出し",
        "export_dialog_subtitle": "Excelファイル（.xlsx）に出力する期間を選択してください：",
        "export_range_all": "全期間",
        "export_range_this_month": "今月",
        "export_range_last_month": "先月",
        "export_button_confirm": "書き出し",
        "export_empty_message": "選択した期間の支払い履歴はありません。",
        "export_success_title": "書き出し完了",
        "export_success_message": "{count}件の取引を出力しました：\n{location}\n\nファイル名: {filename}\n\n端末の「ファイル」アプリから確認できます。",
        "export_warning_title": "保存先の制限",
        "export_warning_message": "ファイル（{filename}）は作成されましたが、Androidの保存先制限のため「ダウンロード」フォルダに保存できませんでした。\n\nアプリ専用領域に保存されているため、通常のファイル管理アプリからはアクセスできません。",
        "export_error_title": "書き出し失敗",
        "export_error_message": "ファイルを出力できませんでした: {error}",

        # Excel Sheets & Columns
        "export_sheet_payments": "支払い一覧",
        "export_sheet_details": "明細",
        "export_sheet_summary": "集計",
        "export_col_date": "日付",
        "export_col_time": "時刻",
        "export_col_name": "名前",
        "export_col_bill": "請求額",
        "export_col_total_paid": "支払額",
        "export_col_change": "お釣り",
        "export_col_mode": "計算モード",
        "export_col_wallet_after": "支払い後の残高",
        "export_col_paid_breakdown": "支払いの内訳",
        "export_col_change_breakdown": "お釣りの内訳",
        "export_col_payment_id": "支払いID",
        "export_col_kind": "区分",
        "export_kind_paid": "支払い",
        "export_kind_change": "お釣り",
        "export_col_denom": "金種",
        "export_col_count": "枚数",
        "export_col_subtotal": "小計",
        "export_summary_monthly_title": "月別支出集計",
        "export_col_month": "年月",
        "export_col_num_payments": "支払い件数",
        "export_col_total_bill": "請求額合計",
        "export_col_avg_bill": "平均請求額",
        "export_total_row": "総合計",
        "export_summary_denom_title": "金種別利用状況",
        "export_col_handed_count": "渡した枚数",
        "export_col_handed_subtotal": "渡した金額",
        "export_col_received_count": "受け取った枚数",
        "export_col_received_subtotal": "受け取った金額",
        "export_col_net_count": "増減枚数",
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
        "history_export_button": "Xuất ra Excel",
        "history_rename_hint": "Mẹo: Nhấn giữ một giao dịch để đổi tên",
        "history_rename_title": "Đổi tên giao dịch",
        "history_rename_label": "Tên giao dịch (vd: Ăn trưa, Siêu thị)",
        "history_rename_save": "Lưu",
        "history_rename_tooltip": "Đổi tên",

        # Dialogs
        "undo_dialog_title": "Hoàn tác giao dịch gần nhất?",
        "undo_dialog_content": "Thao tác này sẽ hoàn lại tiền đưa và tiền thối vào ví của bạn.",
        "clear_dialog_title": "Xóa toàn bộ lịch sử?",
        "clear_dialog_content": "Toàn bộ lịch sử sẽ bị xóa vĩnh viễn. Số dư trong ví sẽ không thay đổi.",
        "dialog_confirm": "Xác nhận",
        "dialog_cancel": "Hủy",

        # Excel Export
        "export_dialog_title": "Xuất lịch sử giao dịch",
        "export_dialog_subtitle": "Chọn khoảng thời gian xuất ra tệp Excel (.xlsx):",
        "export_range_all": "Tất cả",
        "export_range_this_month": "Tháng này",
        "export_range_last_month": "Tháng trước",
        "export_button_confirm": "Xuất tệp",
        "export_empty_message": "Không tìm thấy lịch sử thanh toán trong khoảng thời gian đã chọn.",
        "export_success_title": "Xuất tệp thành công",
        "export_success_message": "Đã xuất {count} giao dịch vào:\n{location}\n\nTệp: {filename}\n\nBạn có thể mở tệp này bằng ứng dụng Tệp (Files) trên điện thoại.",
        "export_warning_title": "Giới hạn vị trí lưu",
        "export_warning_message": "Tệp ({filename}) đã được tạo nhưng không thể lưu vào thư mục Tải về công khai do giới hạn quyền của hệ thống Android.\n\nTệp nằm trong bộ nhớ riêng của ứng dụng và không thể truy cập bằng trình quản lý tệp thông thường.",
        "export_error_title": "Lỗi xuất tệp",
        "export_error_message": "Không thể tạo tệp xuất: {error}",

        # Excel Sheets & Columns
        "export_sheet_payments": "Giao dịch",
        "export_sheet_details": "Chi tiết",
        "export_sheet_summary": "Tổng hợp",
        "export_col_date": "Ngày",
        "export_col_time": "Giờ",
        "export_col_name": "Tên",
        "export_col_bill": "Số tiền hóa đơn",
        "export_col_total_paid": "Đã trả",
        "export_col_change": "Tiền thối",
        "export_col_mode": "Chế độ tính",
        "export_col_wallet_after": "Số dư ví sau trả",
        "export_col_paid_breakdown": "Chi tiết tiền đưa",
        "export_col_change_breakdown": "Chi tiết tiền thối",
        "export_col_payment_id": "Mã giao dịch",
        "export_col_kind": "Loại",
        "export_kind_paid": "Đưa",
        "export_kind_change": "Thối lại",
        "export_col_denom": "Mệnh giá",
        "export_col_count": "Số lượng",
        "export_col_subtotal": "Thành tiền",
        "export_summary_monthly_title": "Tổng hợp chi tiêu theo tháng",
        "export_col_month": "Tháng",
        "export_col_num_payments": "Số giao dịch",
        "export_col_total_bill": "Tổng hóa đơn",
        "export_col_avg_bill": "Hóa đơn trung bình",
        "export_total_row": "Tổng cộng",
        "export_summary_denom_title": "Chi tiết sử dụng mệnh giá",
        "export_col_handed_count": "Số lượng đưa",
        "export_col_handed_subtotal": "Tổng tiền đưa",
        "export_col_received_count": "Số lượng nhận",
        "export_col_received_subtotal": "Tổng tiền nhận",
        "export_col_net_count": "Chênh lệch số lượng",
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
