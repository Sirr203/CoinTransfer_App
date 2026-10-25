from core import suggest, DENOMS
w = {d: 0 for d in DENOMS}
w.update({1000: 2, 500: 0, 100: 4, 50: 1, 10: 3, 5: 1, 1: 2})
r = suggest(w, 630); print(r)
w2 = {d: 0 for d in DENOMS}; w2.update({1000: 1, 100: 6, 50: 1, 10: 4, 5: 1, 1: 3})
print(suggest(w2, 630))
print(suggest({d: 0 for d in DENOMS} | {100: 2}, 630))
