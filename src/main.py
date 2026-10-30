"""Flet user interface for CoinTrans (offline Japanese coin payment optimizer)."""
import flet as ft
from core import DENOMS, suggest, load_wallet, save_wallet, load_settings, save_settings
from i18n import (
    SUPPORTED_LANGUAGES,
    t,
    format_count_unit,
    format_breakdown_summary,
    detect_device_language,
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
        r = state["result"]
        if not r: return
        for d in DENOMS:
            wallet[d] = r["after"].get(d, 0)
        save_wallet(wallet)
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
    # 3. NAVIGATION & SAFEARIA
    # ==========================
    def on_nav_change(e):
        idx = e.control.selected_index
        wallet_view.visible = (idx == 0)
        pay_view.visible = (idx == 1)
        if idx == 0:
            refresh_wallet_ui()
        else:
            calc()
            try:
                bill_in.focus()
            except Exception:
                pass
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
    ]

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,  # Default to Wallet screen
        destinations=nav_destinations,
        on_change=on_nav_change,
    )

    # ==========================
    # 4. LANGUAGE PICKER & REFRESH
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
        refresh_wallet_ui()
        calc()
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
                    name,
                    size=16,
                    weight=ft.FontWeight.BOLD if code == current_lang else ft.FontWeight.NORMAL,
                    color=ft.Colors.TEAL_800 if code == current_lang else ft.Colors.BLACK87,
                ),
                trailing=ft.Icon(ft.Icons.CHECK, color=ft.Colors.TEAL) if code == current_lang else None,
                on_click=lambda ev, c=code: select_language(c),
            )
            for code, name in SUPPORTED_LANGUAGES
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
                controls=[wallet_view, pay_view],
                expand=True,
            ),
            expand=True,
        )
    )

    update_all_ui()

ft.app(target=main)
