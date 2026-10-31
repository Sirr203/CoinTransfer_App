"""Flet user interface for CoinTrans (offline Japanese coin payment optimizer)."""
import os
from datetime import date
import flet as ft
from core import DENOMS, suggest, load_wallet, save_wallet, load_settings, save_settings
from i18n import (
    SUPPORTED_LANGUAGES,
    t,
    format_count_unit,
    format_breakdown_summary,
    detect_device_language,
)
from history import (
    load_history,
    create_entry,
    add_entry,
    delete_entry,
    undo_last_payment,
    clear_history,
    rename_entry,
    get_monthly_summary,
    format_entry_date_group,
    format_month_label,
)
from export import (
    generate_history_workbook,
    filter_entries_by_range,
    resolve_export_directory,
    get_unique_export_filename,
    verify_exported_file,
)

APP_NAME = "CoinTrans"

def fmt(d):
    return f"{d:,}¥"

def main(page: ft.Page):
    page.title = APP_NAME
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    wallet = load_wallet()
    settings = load_settings()
    history_entries = load_history()
    current_lang = settings.get("language") or detect_device_language()
    state = {"result": None}

    # ==========================
    # 1. WALLET TAB
    # ==========================
    total_val_txt = ft.Text("0¥", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_800)
    total_items_txt = ft.Text("", size=13, color=ft.Colors.GREY_700)
    wallet_summary_title_txt = ft.Text("", size=14, color=ft.Colors.TEAL_800, weight=ft.FontWeight.W_500, expand=True)
    count_inputs = {}
    subtotal_txts = {}

    def refresh_summary():
        total_yen = sum(d * n for d, n in wallet.items())
        total_coins = sum(n for d, n in wallet.items() if d < 1000)
        total_notes = sum(n for d, n in wallet.items() if d >= 1000)
        total_val_txt.value = fmt(total_yen)
        total_items_txt.value = format_breakdown_summary(total_notes, total_coins, current_lang)
        page.update()

    def refresh_wallet_ui():
        for d in DENOMS:
            n = wallet[d]
            if count_inputs[d].value != str(n):
                count_inputs[d].value = str(n)
            subtotal_txts[d].value = t("subtotal_format", current_lang, amount=fmt(d * n))
        refresh_summary()

    def adjust(d, delta):
        wallet[d] = max(0, wallet[d] + delta)
        count_inputs[d].value = str(wallet[d])
        subtotal_txts[d].value = t("subtotal_format", current_lang, amount=fmt(d * wallet[d]))
        save_wallet(wallet)
        refresh_summary()

    def on_count_text_change(e, d):
        val = (e.control.value or "").strip()
        if not val:
            n = 0
        else:
            try:
                n = max(0, int(val))
            except ValueError:
                n = wallet[d]
        wallet[d] = n
        save_wallet(wallet)
        subtotal_txts[d].value = t("subtotal_format", current_lang, amount=fmt(d * n))
        refresh_summary()

    wallet_rows = []
    for d in DENOMS:
        subtotal_txts[d] = ft.Text(t("subtotal_format", current_lang, amount=fmt(d * wallet[d])), size=12, color=ft.Colors.GREY_600)
        field = ft.TextField(
            value=str(wallet[d]),
            width=58,
            height=38,
            content_padding=ft.padding.symmetric(vertical=2, horizontal=4),
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_size=16,
            border=ft.InputBorder.OUTLINE,
        )
        field.on_change = lambda e, d=d: on_count_text_change(e, d)
        count_inputs[d] = field

        is_note = d >= 1000
        icon_type = ft.Icons.PAYMENTS_OUTLINED if is_note else ft.Icons.MONETIZATION_ON_OUTLINED

        wallet_rows.append(
            ft.Card(
                elevation=1,
                content=ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    content=ft.Row([
                        ft.Icon(icon_type, color=ft.Colors.TEAL if is_note else ft.Colors.AMBER_800, size=24),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(fmt(d), size=17, weight=ft.FontWeight.W_600),
                                subtotal_txts[d],
                            ], spacing=2),
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            icon_size=24,
                            on_click=lambda e, d=d: adjust(d, -1),
                        ),
                        count_inputs[d],
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            icon_color=ft.Colors.TEAL_600,
                            icon_size=24,
                            on_click=lambda e, d=d: adjust(d, +1),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ),
            )
        )

    settings_btn = ft.IconButton(
        icon=ft.Icons.SETTINGS_OUTLINED,
        icon_color=ft.Colors.TEAL_800,
        icon_size=22,
        tooltip=t("settings_tooltip", current_lang),
    )

    wallet_summary_card = ft.Card(
        elevation=2,
        color=ft.Colors.TEAL_50,
        content=ft.Container(
            padding=16,
            content=ft.Column([
                ft.Row([
                    wallet_summary_title_txt,
                    settings_btn,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                total_val_txt,
                total_items_txt,
            ], spacing=4),
        ),
    )

    wallet_view = ft.ListView([
        wallet_summary_card,
        ft.Container(height=4),
        *wallet_rows,
        ft.Container(height=16),
    ], expand=True, padding=12, visible=True)

    # ==========================
    # 2. PAY TAB
    # ==========================
    bill_in = ft.TextField(
        label=t("bill_label", current_lang),
        hint_text=t("bill_hint", current_lang),
        suffix_text="¥",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_size=30,
        text_align=ft.TextAlign.RIGHT,
        autofocus=False,
        border_radius=10,
    )

    mode_switch = ft.Switch(
        label=t("mode_switch_label", current_lang),
        value=settings.get("prefer_notes", False),
        active_color=ft.Colors.TEAL,
    )
    mode_hint = ft.Text(
        t("mode_hint_notes", current_lang) if mode_switch.value else t("mode_hint_fast", current_lang),
        size=12,
        color=ft.Colors.GREY_600,
    )

    result_container = ft.Column(spacing=12)
    confirm_btn_text = ft.Text(t("confirm_paid", current_lang), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    confirm_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
            confirm_btn_text,
        ], alignment=ft.MainAxisAlignment.CENTER),
        visible=False,
        height=54,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.TEAL,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

    def calc(e=None):
        result_container.controls.clear()
        confirm_btn.visible = False
        state["result"] = None

        raw = (bill_in.value or "").strip().replace(",", "").replace(".", "").replace("¥", "")
        if not raw:
            page.update()
            return
        try:
            bill = int(raw)
            if bill <= 0:
                page.update()
                return
        except ValueError:
            page.update()
            return

        r = suggest(wallet, bill, prefer_notes=mode_switch.value)
        if r is None:
            result_container.controls.append(
                ft.Container(
                    padding=16,
                    border_radius=10,
                    bgcolor=ft.Colors.RED_50,
                    border=ft.border.all(1, ft.Colors.RED_200),
                    content=ft.Row([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED, size=26),
                        ft.Text(
                            t("error_insufficient", current_lang),
                            color=ft.Colors.RED_800,
                            size=15,
                            weight=ft.FontWeight.W_500,
                            expand=True,
                        ),
                    ]),
                )
            )
        else:
            state["result"] = r
            pay_lines = []
            for d, n in r["pay"].items():
                unit_str = format_count_unit(n, is_note=(d >= 1000), lang=current_lang)
                pay_lines.append(
                    ft.Row([
                        ft.Text(f"• {fmt(d)}", size=18, weight=ft.FontWeight.W_600),
                        ft.Text(f"× {unit_str}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_900),
                        ft.Text(f"({fmt(d * n)})", size=14, color=ft.Colors.GREY_600),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

            change_lines = []
            if r["change"]:
                for d, n in r["change"].items():
                    unit_str = format_count_unit(n, is_note=(d >= 1000), lang=current_lang)
                    change_lines.append(
                        ft.Row([
                            ft.Text(f"• {fmt(d)}", size=17, weight=ft.FontWeight.W_600),
                            ft.Text(f"× {unit_str}", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )
            else:
                change_lines.append(ft.Text(t("exact_change_none", current_lang), size=16, color=ft.Colors.GREY_700))

            change_total = sum(d * n for d, n in r["change"].items())

            # Hand Over card (Teal)
            pay_card = ft.Container(
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.TEAL_50,
                border=ft.border.all(1.5, ft.Colors.TEAL_300),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ARROW_UPWARD, color=ft.Colors.TEAL_800),
                        ft.Text(t("give_title", current_lang), size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_800),
                        ft.Text(fmt(r["total_paid"]), size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_900),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=ft.Colors.TEAL_200, height=12),
                    *pay_lines,
                ], spacing=6),
            )

            # Change card (Blue)
            change_card = ft.Container(
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.BLUE_50,
                border=ft.border.all(1.5, ft.Colors.BLUE_200),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.BLUE_800),
                        ft.Text(t("change_title", current_lang), size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                        ft.Text(fmt(change_total), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=ft.Colors.BLUE_200, height=12),
                    *change_lines,
                ], spacing=6),
            )

            result_container.controls.extend([pay_card, change_card])
            confirm_btn.visible = True

        page.update()

    def on_mode_change(e):
        settings["prefer_notes"] = mode_switch.value
        save_settings(settings)
        mode_hint.value = (
            t("mode_hint_notes", current_lang) if mode_switch.value else t("mode_hint_fast", current_lang)
        )
        calc()

    mode_switch.on_change = on_mode_change

    def do_confirm(e):
        nonlocal history_entries
        r = state["result"]
        if not r: return
        raw = (bill_in.value or "").strip().replace(",", "").replace(".", "").replace("¥", "")
        bill_amount = int(raw)

        # 1. Update wallet balance
        for d in DENOMS:
            wallet[d] = r["after"].get(d, 0)
        save_wallet(wallet)

        # 2. Record history entry
        change_total = sum(d * n for d, n in r["change"].items())
        wallet_total_after = sum(d * n for d, n in wallet.items())
        mode_str = "optimize_notes" if mode_switch.value else "fast"
        new_entry = create_entry(
            bill=bill_amount,
            total_paid=r["total_paid"],
            change=change_total,
            pay=r["pay"],
            change_breakdown=r["change"],
            mode=mode_str,
            wallet_total_after=wallet_total_after,
        )
        history_entries = add_entry(history_entries, new_entry)

        # 3. Reset pay UI & update wallet
        refresh_wallet_ui()
        bill_in.value = ""
        result_container.controls.clear()
        confirm_btn.visible = False
        state["result"] = None
        page.update()

    bill_in.on_change = calc
    bill_in.on_submit = calc
    confirm_btn.on_click = do_confirm

    pay_view = ft.ListView([
        bill_in,
        ft.Container(
            padding=ft.padding.symmetric(horizontal=4),
            content=ft.Column([
                mode_switch,
                mode_hint,
            ], spacing=2),
        ),
        ft.Container(height=4),
        result_container,
        ft.Container(height=8),
        confirm_btn,
        ft.Container(height=20),
    ], expand=True, padding=12, visible=False)

    # ==========================
    # 3. HISTORY TAB
    # ==========================
    history_list_column = ft.Column(spacing=10)

    def show_confirm_dialog(title: str, content: str, on_confirm_callback):
        def handle_confirm(ev):
            dlg.open = False
            page.update()
            on_confirm_callback()

        dlg = ft.AlertDialog(
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Text(content),
            actions=[
                ft.TextButton(
                    t("dialog_cancel", current_lang),
                    on_click=lambda ev: close_dialog(dlg),
                ),
                ft.ElevatedButton(
                    t("dialog_confirm", current_lang),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.TEAL, color=ft.Colors.WHITE),
                    on_click=handle_confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def do_undo_payment():
        nonlocal history_entries
        history_entries, restored_wallet = undo_last_payment(history_entries, wallet)
        for d in DENOMS:
            wallet[d] = restored_wallet.get(d, 0)
        save_wallet(wallet)
        refresh_wallet_ui()
        refresh_history_ui()
        page.update()

    def do_delete_single_entry(entry_id: str):
        nonlocal history_entries
        history_entries = delete_entry(history_entries, entry_id)
        refresh_history_ui()
        page.update()

    def do_clear_all_history():
        nonlocal history_entries
        history_entries = clear_history()
        refresh_history_ui()
        page.update()

    def show_rename_dialog(entry: dict):
        name_input = ft.TextField(
            value=entry.get("name", ""),
            label=t("history_rename_label", current_lang),
            max_length=60,
            autofocus=True,
            border_color=ft.Colors.TEAL,
        )

        def handle_save(ev):
            nonlocal history_entries
            close_dialog(dlg)
            history_entries = rename_entry(history_entries, entry.get("id"), name_input.value)
            refresh_history_ui()
            page.update()

        name_input.on_submit = handle_save

        dlg = ft.AlertDialog(
            title=ft.Text(t("history_rename_title", current_lang), weight=ft.FontWeight.BOLD),
            content=ft.Column([
                name_input,
            ], tight=True, spacing=8),
            actions=[
                ft.TextButton(
                    t("dialog_cancel", current_lang),
                    on_click=lambda ev: close_dialog(dlg),
                ),
                ft.ElevatedButton(
                    t("history_rename_save", current_lang),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.TEAL, color=ft.Colors.WHITE),
                    on_click=handle_save,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def show_export_dialog():
        range_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="all", label=t("export_range_all", current_lang)),
                ft.Radio(value="this_month", label=t("export_range_this_month", current_lang)),
                ft.Radio(value="last_month", label=t("export_range_last_month", current_lang)),
            ], spacing=6),
            value="all",
        )

        def handle_export(ev):
            chosen_range = range_radio.value or "all"
            filtered = filter_entries_by_range(history_entries, chosen_range)
            close_dialog(dlg)

            if not filtered:
                empty_dlg = ft.AlertDialog(
                    title=ft.Text(t("export_dialog_title", current_lang), weight=ft.FontWeight.BOLD),
                    content=ft.Text(t("export_empty_message", current_lang)),
                    actions=[
                        ft.TextButton(
                            t("close", current_lang),
                            on_click=lambda ev: close_dialog(empty_dlg),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.overlay.append(empty_dlg)
                empty_dlg.open = True
                page.update()
                return

            export_dir, display_location, is_public = resolve_export_directory()
            filename, file_path = get_unique_export_filename(export_dir)

            try:
                generate_history_workbook(
                    history_entries,
                    lang=current_lang,
                    export_range=chosen_range,
                    output_path=file_path,
                )
                verify_exported_file(file_path)
            except Exception as err:
                err_type = type(err).__name__
                err_dlg = ft.AlertDialog(
                    title=ft.Text(t("export_error_title", current_lang), weight=ft.FontWeight.BOLD),
                    content=ft.Text(t("export_error_message", current_lang, error=f"[{err_type}] {str(err)}")),
                    actions=[
                        ft.TextButton(t("close", current_lang), on_click=lambda ev: close_dialog(err_dlg)),
                    ],
                )
                page.overlay.append(err_dlg)
                err_dlg.open = True
                page.update()
                return

            if not is_public:
                warn_dlg = ft.AlertDialog(
                    title=ft.Text(t("export_warning_title", current_lang), weight=ft.FontWeight.BOLD),
                    content=ft.Column([
                        ft.Text(
                            t(
                                "export_warning_message",
                                current_lang,
                                filename=filename,
                            ),
                            size=14,
                            color=ft.Colors.GREY_800,
                        ),
                    ], tight=True, spacing=8),
                    actions=[
                        ft.ElevatedButton(
                            t("close", current_lang),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.TEAL, color=ft.Colors.WHITE),
                            on_click=lambda ev: close_dialog(warn_dlg),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.overlay.append(warn_dlg)
                warn_dlg.open = True
                page.update()
                return

            success_dlg = ft.AlertDialog(
                title=ft.Text(t("export_success_title", current_lang), weight=ft.FontWeight.BOLD),
                content=ft.Column([
                    ft.Text(
                        t(
                            "export_success_message",
                            current_lang,
                            count=len(filtered),
                            location=display_location,
                            filename=filename,
                        ),
                        size=14,
                        color=ft.Colors.GREY_800,
                    ),
                ], tight=True, spacing=8),
                actions=[
                    ft.ElevatedButton(
                        t("close", current_lang),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.TEAL, color=ft.Colors.WHITE),
                        on_click=lambda ev: close_dialog(success_dlg),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(success_dlg)
            success_dlg.open = True
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(t("export_dialog_title", current_lang), weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(t("export_dialog_subtitle", current_lang), size=13, color=ft.Colors.GREY_700),
                ft.Container(height=8),
                range_radio,
            ], tight=True, spacing=4),
            actions=[
                ft.TextButton(
                    t("dialog_cancel", current_lang),
                    on_click=lambda ev: close_dialog(dlg),
                ),
                ft.ElevatedButton(
                    t("export_button_confirm", current_lang),
                    icon=ft.Icons.FILE_DOWNLOAD,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.TEAL, color=ft.Colors.WHITE),
                    on_click=handle_export,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def refresh_history_ui():
        history_list_column.controls.clear()

        # Monthly summary card
        summary = get_monthly_summary(history_entries)
        month_label = format_month_label(summary["year"], summary["month"], current_lang)

        export_btn = ft.IconButton(
            icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
            icon_color=ft.Colors.TEAL_800,
            tooltip=t("history_export_button", current_lang),
            visible=(len(history_entries) > 0),
            on_click=lambda ev: show_export_dialog(),
        )

        clear_btn = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP_OUTLINED,
            icon_color=ft.Colors.RED_400,
            tooltip=t("history_clear_all", current_lang),
            visible=(len(history_entries) > 0),
            on_click=lambda ev: show_confirm_dialog(
                t("clear_dialog_title", current_lang),
                t("clear_dialog_content", current_lang),
                do_clear_all_history,
            ),
        )

        summary_card = ft.Card(
            elevation=2,
            color=ft.Colors.TEAL_50,
            content=ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            t("history_summary_title", current_lang, month=month_label),
                            size=14,
                            color=ft.Colors.TEAL_800,
                            weight=ft.FontWeight.W_500,
                            expand=True,
                        ),
                        ft.Row([
                            export_btn,
                            clear_btn,
                        ], spacing=0),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(
                        fmt(summary["total_spent"]),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.TEAL_900,
                    ),
                    ft.Text(
                        t("history_summary_count", current_lang, count=summary["payment_count"]),
                        size=13,
                        color=ft.Colors.GREY_700,
                    ),
                ], spacing=4),
            ),
        )
        history_list_column.controls.append(summary_card)

        # Empty state
        if not history_entries:
            empty_view = ft.Container(
                padding=ft.padding.symmetric(vertical=48, horizontal=24),
                alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=64, color=ft.Colors.GREY_400),
                    ft.Text(t("history_empty_title", current_lang), size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                    ft.Text(t("history_empty_subtitle", current_lang), size=13, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            )
            history_list_column.controls.append(empty_view)
            page.update()
            return

        # Discoverability hint
        history_list_column.controls.append(
            ft.Container(
                padding=ft.padding.only(left=8, top=2, bottom=4),
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=ft.Colors.GREY_600),
                    ft.Text(
                        t("history_rename_hint", current_lang),
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                ], spacing=6),
            )
        )

        # Group entries by date
        current_date_group = None
        for idx, entry in enumerate(history_entries):
            is_latest = (idx == 0)
            date_group, time_str = format_entry_date_group(entry.get("timestamp", ""), current_lang)

            if date_group != current_date_group:
                current_date_group = date_group
                history_list_column.controls.append(
                    ft.Container(
                        padding=ft.padding.only(left=4, top=14, bottom=2),
                        content=ft.Text(
                            date_group,
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.TEAL_800,
                        ),
                    )
                )

            # Details for expanded row
            pay_lines = []
            for d_str, count in entry.get("pay", {}).items():
                d = int(d_str)
                unit_str = format_count_unit(count, is_note=(d >= 1000), lang=current_lang)
                pay_lines.append(
                    ft.Text(f"• {fmt(d)} × {unit_str}", size=14, color=ft.Colors.GREY_800)
                )

            change_lines = []
            change_bd = entry.get("change_breakdown", {})
            if change_bd:
                for d_str, count in change_bd.items():
                    d = int(d_str)
                    unit_str = format_count_unit(count, is_note=(d >= 1000), lang=current_lang)
                    change_lines.append(
                        ft.Text(f"• {fmt(d)} × {unit_str}", size=14, color=ft.Colors.BLUE_800)
                    )
            else:
                change_lines.append(
                    ft.Text(t("exact_change_none", current_lang), size=14, color=ft.Colors.GREY_600)
                )

            mode_text = (
                t("history_mode_notes", current_lang)
                if entry.get("mode") == "optimize_notes"
                else t("history_mode_fast", current_lang)
            )

            # Action buttons for expanded view
            action_buttons = []
            if is_latest:
                undo_btn = ft.OutlinedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.UNDO, size=16, color=ft.Colors.AMBER_900),
                        ft.Text(t("history_undo_button", current_lang), size=13, color=ft.Colors.AMBER_900),
                    ], spacing=4),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1, ft.Colors.AMBER_400),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda ev: show_confirm_dialog(
                        t("undo_dialog_title", current_lang),
                        t("undo_dialog_content", current_lang),
                        do_undo_payment,
                    ),
                )
                action_buttons.append(undo_btn)

            edit_btn = ft.IconButton(
                icon=ft.Icons.EDIT_OUTLINED,
                icon_color=ft.Colors.TEAL_700,
                icon_size=20,
                tooltip=t("history_rename_tooltip", current_lang),
                on_click=lambda ev, e=entry: show_rename_dialog(e),
            )
            action_buttons.append(edit_btn)

            del_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=ft.Colors.RED_400,
                icon_size=20,
                tooltip=t("history_delete_button", current_lang),
                on_click=lambda ev, eid=entry.get("id"): do_delete_single_entry(eid),
            )
            action_buttons.append(del_btn)

            expanded_content = ft.Container(
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                bgcolor=ft.Colors.GREY_50,
                border_radius=8,
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            border_radius=6,
                            bgcolor=ft.Colors.TEAL_100,
                            content=ft.Text(mode_text, size=11, color=ft.Colors.TEAL_900, weight=ft.FontWeight.W_500),
                        ),
                        ft.Text(
                            t("history_wallet_after", current_lang, amount=fmt(entry.get("wallet_total_after", 0))),
                            size=12,
                            color=ft.Colors.GREY_600,
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=8, color=ft.Colors.GREY_200),
                    ft.Text(t("give_title", current_lang), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_800),
                    *pay_lines,
                    ft.Container(height=4),
                    ft.Text(t("change_title", current_lang), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                    *change_lines,
                    ft.Divider(height=8, color=ft.Colors.GREY_200),
                    ft.Row(action_buttons, alignment=ft.MainAxisAlignment.END, spacing=8),
                ], spacing=4),
            )

            entry_name = entry.get("name")
            if entry_name:
                title_control = ft.Text(
                    entry_name,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.TEAL_900,
                    no_wrap=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
                subtitle_control = ft.Text(
                    f"{fmt(entry.get('bill', 0))}  •  {time_str}  •  {t('history_change_label', current_lang, amount=fmt(entry.get('change', 0)))}",
                    size=12,
                    color=ft.Colors.GREY_600,
                )
            else:
                title_control = ft.Text(
                    fmt(entry.get("bill", 0)),
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.TEAL_900,
                )
                subtitle_control = ft.Text(
                    f"{time_str}  •  {t('history_change_label', current_lang, amount=fmt(entry.get('change', 0)))}",
                    size=12,
                    color=ft.Colors.GREY_600,
                )

            tile = ft.ExpansionTile(
                leading=ft.Icon(
                    ft.Icons.PAYMENTS_OUTLINED,
                    color=ft.Colors.TEAL_700,
                    size=24,
                ),
                title=title_control,
                subtitle=subtitle_control,
                trailing=ft.Text(
                    t("history_paid_label", current_lang, amount=fmt(entry.get("total_paid", 0))),
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.GREY_800,
                ),
                controls=[expanded_content],
                tile_padding=ft.padding.symmetric(horizontal=12, vertical=0),
                shape=ft.RoundedRectangleBorder(radius=10),
                collapsed_shape=ft.RoundedRectangleBorder(radius=10),
            )

            history_list_column.controls.append(
                ft.Card(
                    elevation=1,
                    content=ft.GestureDetector(
                        content=tile,
                        on_long_press_start=lambda ev, e=entry: show_rename_dialog(e),
                    ),
                )
            )

        page.update()

    history_view = ft.ListView([
        history_list_column,
        ft.Container(height=24),
    ], expand=True, padding=12, visible=False)

    # ==========================
    # 4. NAVIGATION & SAFEARIA
    # ==========================
    def on_nav_change(e):
        idx = e.control.selected_index
        wallet_view.visible = (idx == 0)
        pay_view.visible = (idx == 1)
        history_view.visible = (idx == 2)
        if idx == 0:
            refresh_wallet_ui()
        elif idx == 1:
            calc()
            try:
                bill_in.focus()
            except Exception:
                pass
        elif idx == 2:
            refresh_history_ui()
        page.update()

    nav_destinations = [
        ft.NavigationBarDestination(
            icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
            selected_icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
            label=t("nav_wallet", current_lang),
        ),
        ft.NavigationBarDestination(
            icon=ft.Icons.PAYMENTS_OUTLINED,
            selected_icon=ft.Icons.PAYMENTS,
            label=t("nav_pay", current_lang),
        ),
        ft.NavigationBarDestination(
            icon=ft.Icons.HISTORY_OUTLINED,
            selected_icon=ft.Icons.HISTORY,
            label=t("nav_history", current_lang),
        ),
    ]

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,  # Default to Wallet screen
        destinations=nav_destinations,
        on_change=on_nav_change,
    )

    # ==========================
    # 5. LANGUAGE PICKER & REFRESH
    # ==========================
    def update_all_ui():
        wallet_summary_title_txt.value = t("wallet_summary_title", current_lang)
        settings_btn.tooltip = t("settings_tooltip", current_lang)
        bill_in.label = t("bill_label", current_lang)
        mode_switch.label = t("mode_switch_label", current_lang)
        mode_hint.value = (
            t("mode_hint_notes", current_lang) if mode_switch.value else t("mode_hint_fast", current_lang)
        )
        confirm_btn_text.value = t("confirm_paid", current_lang)
        nav_destinations[0].label = t("nav_wallet", current_lang)
        nav_destinations[1].label = t("nav_pay", current_lang)
        nav_destinations[2].label = t("nav_history", current_lang)
        refresh_wallet_ui()
        calc()
        refresh_history_ui()
        page.update()

    def open_language_picker(e):
        def select_language(code):
            nonlocal current_lang
            current_lang = code
            settings["language"] = current_lang
            save_settings(settings)
            dlg.open = False
            update_all_ui()
            page.update()

        tiles = [
            ft.ListTile(
                title=ft.Text(
                    t("lang_name", code),
                    size=16,
                    weight=ft.FontWeight.BOLD if code == current_lang else ft.FontWeight.NORMAL,
                    color=ft.Colors.TEAL_800 if code == current_lang else ft.Colors.BLACK87,
                ),
                trailing=ft.Icon(ft.Icons.CHECK, color=ft.Colors.TEAL) if code == current_lang else None,
                on_click=lambda ev, c=code: select_language(c),
            )
            for code in SUPPORTED_LANGUAGES
        ]

        dlg = ft.AlertDialog(
            title=ft.Text(t("language_picker_title", current_lang), weight=ft.FontWeight.BOLD),
            content=ft.Column(tiles, tight=True),
            actions=[
                ft.TextButton(
                    t("close", current_lang),
                    on_click=lambda ev: close_dialog(dlg),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def close_dialog(dlg):
        dlg.open = False
        page.update()

    settings_btn.on_click = open_language_picker

    page.add(
        ft.SafeArea(
            content=ft.Stack(
                controls=[wallet_view, pay_view, history_view],
                expand=True,
            ),
            expand=True,
        )
    )

    update_all_ui()

ft.app(target=main)
