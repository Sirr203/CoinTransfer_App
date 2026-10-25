"""Giao diện Flet 0.28 cho ứng dụng Xu Gọn."""
import flet as ft
from core import DENOMS, suggest, load_wallet, save_wallet, load_settings, save_settings

APP_NAME = "Xu Gọn"

def fmt(d):
    return f"{d:,}¥"

def main(page: ft.Page):
    page.title = APP_NAME
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    wallet = load_wallet()
    settings = load_settings()
    state = {"result": None}

    # ==========================
    # 1. TAB VÍ
    # ==========================
    total_val_txt = ft.Text("0¥", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_800)
    total_items_txt = ft.Text("0 tờ/xu", size=13, color=ft.Colors.GREY_700)
    count_inputs = {}
    subtotal_txts = {}

    def refresh_wallet_ui():
        total_yen = sum(d * n for d, n in wallet.items())
        total_coins = sum(n for d, n in wallet.items() if d < 1000)
        total_notes = sum(n for d, n in wallet.items() if d >= 1000)
        total_val_txt.value = fmt(total_yen)
        total_items_txt.value = f"Tiền giấy: {total_notes} tờ  |  Tiền xu: {total_coins} đồng"
        for d in DENOMS:
            n = wallet[d]
            if count_inputs[d].value != str(n):
                count_inputs[d].value = str(n)
            subtotal_txts[d].value = f"= {fmt(d * n)}"
        page.update()

    def adjust(d, delta):
        wallet[d] = max(0, wallet[d] + delta)
        save_wallet(wallet)
        refresh_wallet_ui()

    def on_count_text_change(e, d):
        val = e.control.value.strip()
        if not val:
            n = 0
        else:
            try:
                n = max(0, int(val))
            except ValueError:
                n = wallet[d]
        wallet[d] = n
        save_wallet(wallet)
        subtotal_txts[d].value = f"= {fmt(d * n)}"
        total_yen = sum(dm * c for dm, c in wallet.items())
        total_coins = sum(c for dm, c in wallet.items() if dm < 1000)
        total_notes = sum(c for dm, c in wallet.items() if dm >= 1000)
        total_val_txt.value = fmt(total_yen)
        total_items_txt.value = f"Tiền giấy: {total_notes} tờ  |  Tiền xu: {total_coins} đồng"
        page.update()

    wallet_rows = []
    for d in DENOMS:
        subtotal_txts[d] = ft.Text(f"= {fmt(d * wallet[d])}", size=12, color=ft.Colors.GREY_600)
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
                        ft.Column([
                            ft.Text(fmt(d), size=17, weight=ft.FontWeight.W_600),
                            subtotal_txts[d],
                        ], spacing=2, expand=True),
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

    wallet_summary_card = ft.Card(
        elevation=2,
        color=ft.Colors.TEAL_50,
        content=ft.Container(
            padding=16,
            content=ft.Column([
                ft.Text("Tổng số dư trong ví", size=13, color=ft.Colors.TEAL_700),
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
    ], expand=True, padding=12)

    # ==========================
    # 2. TAB TRẢ TIỀN
    # ==========================
    bill_in = ft.TextField(
        label="Số tiền hóa đơn",
        hint_text="0",
        suffix_text="¥",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_size=30,
        text_align=ft.TextAlign.RIGHT,
        autofocus=False,
        border_radius=10,
    )

    mode_switch = ft.Switch(
        label="Tối ưu tiền giấy (dọn xu)",
        value=settings.get("prefer_notes", False),
        active_color=ft.Colors.TEAL,
    )
    mode_hint = ft.Text(
        "Mặc định: Đưa & nhận ít tờ/xu nhất (nhanh)" if not mode_switch.value else "Đang bật: Ưu tiên tống khứ xu để dọn ví",
        size=12,
        color=ft.Colors.GREY_600,
    )

    result_container = ft.Column(spacing=12)
    confirm_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
            ft.Text("Xác nhận đã trả", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
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
                        ft.Text("Không đủ tiền trong ví để trả hóa đơn này!", color=ft.Colors.RED_800, size=15, weight=ft.FontWeight.W_500, expand=True),
                    ]),
                )
            )
        else:
            state["result"] = r
            pay_lines = []
            for d, n in r["pay"].items():
                unit = "tờ" if d >= 1000 else "đồng"
                pay_lines.append(
                    ft.Row([
                        ft.Text(f"• {fmt(d)}", size=18, weight=ft.FontWeight.W_600),
                        ft.Text(f"× {n} {unit}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_900),
                        ft.Text(f"({fmt(d * n)})", size=14, color=ft.Colors.GREY_600),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

            change_lines = []
            if r["change"]:
                for d, n in r["change"].items():
                    unit = "tờ" if d >= 1000 else "đồng"
                    change_lines.append(
                        ft.Row([
                            ft.Text(f"• {fmt(d)}", size=17, weight=ft.FontWeight.W_600),
                            ft.Text(f"× {n} {unit}", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )
            else:
                change_lines.append(ft.Text("0¥ (Trả vừa đủ, không thối)", size=16, color=ft.Colors.GREY_700))

            change_total = sum(d * n for d, n in r["change"].items())

            # Khối ĐƯA (Teal)
            pay_card = ft.Container(
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.TEAL_50,
                border=ft.border.all(1.5, ft.Colors.TEAL_300),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ARROW_UPWARD, color=ft.Colors.TEAL_800),
                        ft.Text("ĐƯA CHO THU NGÂN", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_800),
                        ft.Text(fmt(r["total_paid"]), size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_900),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=ft.Colors.TEAL_200, height=12),
                    *pay_lines,
                ], spacing=6),
            )

            # Khối NHẬN LẠI (Blue)
            change_card = ft.Container(
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.BLUE_50,
                border=ft.border.all(1.5, ft.Colors.BLUE_200),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.BLUE_800),
                        ft.Text("NHẬN LẠI", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
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
        mode_hint.value = "Đang bật: Ưu tiên tống khứ xu để dọn ví" if mode_switch.value else "Mặc định: Đưa & nhận ít tờ/xu nhất (nhanh)"
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
    ], expand=True, padding=12)

    # ==========================
    # 3. ĐIỀU HƯỚNG & SAFEARIA
    # ==========================
    content_area = ft.Container(content=wallet_view, expand=True)

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == 0:
            content_area.content = wallet_view
            refresh_wallet_ui()
        else:
            content_area.content = pay_view
            calc()
            bill_in.focus()
        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,  # Mặc định mở ra là màn Ví
        destinations=[
            ft.NavigationDestination(
                icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                selected_icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                label="Ví",
            ),
            ft.NavigationDestination(
                icon=ft.Icons.PAYMENTS_OUTLINED,
                selected_icon=ft.Icons.PAYMENTS,
                label="Trả tiền",
            ),
        ],
        on_change=on_nav_change,
    )

    page.add(
        ft.SafeArea(
            content=content_area,
            expand=True,
        )
    )

    refresh_wallet_ui()

ft.app(target=main)
