from core import suggest, DENOMS

# Test 1: Hóa đơn 630¥ (mặc định nhanh)
w1 = {d: 0 for d in DENOMS}
w1.update({1000: 2, 500: 0, 100: 4, 50: 1, 10: 3, 5: 1, 1: 2})
r1 = suggest(w1, 630, prefer_notes=False)
print("Test 1 (630¥ quick):", r1["pay"], "-> change:", r1["change"])
assert r1["pay"] == {1000: 1, 100: 1, 10: 3}
assert r1["change"] == {500: 1}

# Test 2: Hóa đơn 10¥ (mặc định nhanh: chỉ đưa 1 xu 10¥)
w2 = {d: 0 for d in DENOMS}
w2.update({1000: 2, 500: 1, 100: 5, 50: 1, 10: 5, 5: 1, 1: 5})
r2_quick = suggest(w2, 10, prefer_notes=False)
print("Test 2 (10¥ quick):", r2_quick["pay"], "-> change:", r2_quick["change"])
assert r2_quick["pay"] == {10: 1}
assert r2_quick["change"] == {}

# Test 3: Hóa đơn 10¥ với chế độ tối ưu tiền giấy (dọn xu)
r2_notes = suggest(w2, 10, prefer_notes=True)
print("Test 3 (10¥ notes):", r2_notes["pay"], "-> change:", r2_notes["change"])

# Test 4: Không đủ tiền
assert suggest({d: 0 for d in DENOMS} | {100: 2}, 630) is None
print("All core tests passed successfully!")
