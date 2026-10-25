"""Người 2: giao diện Flet. 2 tab: Ví | Trả tiền."""
import flet as ft
from core import DENOMS, suggest, load_wallet, save_wallet

def fmt(d): return f"{d:,}¥"

def main(page: ft.Page):
    page.title = "Xu Optimizer"
    page.padding = 12
    wallet = load_wallet()
    state = {"result": None}

    # ---------- Tab Ví ----------
    total_txt = ft.Text(size=20, weight=ft.FontWeight.BOLD)
    count_txts = {}

    def refresh_wallet():
        total_txt.value = f"Tổng: {fmt(sum(d * n for d, n in wallet.items()))}"
        for d, t in count_txts.items(): t.value = str(wallet[d])
        page.update()

    def adjust(d, delta):
        wallet[d] = max(0, wallet[d] + delta)
        save_wallet(wallet); refresh_wallet()

    rows = []
    for d in DENOMS:
        count_txts[d] = ft.Text(str(wallet[d]), size=20, width=40, text_align=ft.TextAlign.CENTER)
        rows.append(ft.Row([
            ft.Text(fmt(d), size=18, width=90),
            ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, on_click=lambda e, d=d: adjust(d, -1)),
            count_txts[d],
            ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, on_click=lambda e, d=d: adjust(d, +1)),
        ]))
    wallet_view = ft.Column([total_txt, *rows], scroll=ft.ScrollMode.AUTO, expand=True)

    # ---------- Tab Trả tiền ----------
    bill_in = ft.TextField(label="Số tiền hóa đơn (¥)", keyboard_type=ft.KeyboardType.NUMBER,
                           autofocus=True, text_size=24)
    result_col = ft.Column()
    confirm_btn = ft.ElevatedButton("Xác nhận đã trả", visible=False, height=56)

    def calc(e=None):
        result_col.controls.clear(); confirm_btn.visible = False; state["result"] = None
        raw = (bill_in.value or "").strip().replace(",", "").replace(".", "")
        if not raw:
            page.update(); return
        try:
            bill = int(raw)
            if bill <= 0:
                page.update(); return
        except (TypeError, ValueError):
            page.update(); return
        r = suggest(wallet, bill)
        if r is None:
            result_col.controls.append(ft.Text("Không đủ tiền trong ví!", color=ft.Colors.RED, size=18))
        else:
            state["result"] = r
            pay_lines = [f"• {fmt(d)} × {n} {'tờ' if d >= 1000 else 'xu'}" for d, n in r["pay"].items()]
            change_txt = " + ".join(f"{fmt(d)}×{n}" for d, n in r["change"].items()) if r["change"] else "0¥ (không thối lại)"
            result_col.controls += [
                ft.Text(f"👉 TỔNG ĐƯA: {fmt(r['total_paid'])}", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.GREEN_700),
                ft.Text("\n".join(pay_lines), size=20),
                ft.Divider(),
                ft.Text(f"🪙 NHẬN LẠI: {change_txt}", size=18, color=ft.Colors.BLUE_700),
            ]
            confirm_btn.visible = True
        page.update()

    def do_confirm(e):
        r = state["result"]
        if not r: return
        for d in DENOMS: wallet[d] = r["after"].get(d, 0)
        save_wallet(wallet); refresh_wallet()
        bill_in.value = ""; result_col.controls.clear(); confirm_btn.visible = False
        state["result"] = None
        page.update()

    bill_in.on_change = calc
    bill_in.on_submit = calc
    confirm_btn.on_click = do_confirm
    pay_view = ft.Column([bill_in, result_col, confirm_btn], scroll=ft.ScrollMode.AUTO, expand=True)

    tabs = ft.Tabs(selected_index=1, expand=True, tabs=[
        ft.Tab(text="Ví", content=wallet_view),
        ft.Tab(text="Trả tiền", content=pay_view),
    ], on_change=lambda e: calc() if tabs.selected_index == 1 and bill_in.value else None)
    page.add(tabs)
    refresh_wallet()

ft.app(target=main)
