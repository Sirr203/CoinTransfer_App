from core import suggest, DENOMS

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
print("All core tests passed successfully!")
