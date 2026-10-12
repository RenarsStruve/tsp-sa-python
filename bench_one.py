"""Viens piemērs: testa palaišanas (+ ilgās atsauces palaišanas nejaušiem piemēriem). Raksta results/raw_<nosaukums>.json"""
import sys, json, time
from tsp_sa import TSP, anneal
def budget(n):
    return 100_000 if n <= 15 else 500_000 if n <= 50 else 1_000_000 if n <= 100 else 2_000_000 if n <= 200 else 4_000_000
name = sys.argv[1]; t = TSP.load(f"instances/{name}.txt"); it = budget(t.n)
runs = 10 if t.n < 500 else 5
vals, times = [], []
for s in range(runs):
    t0 = time.perf_counter(); _, L, _, _ = anneal(t, it, seed=s); times.append(time.perf_counter() - t0); vals.append(L)
long = []
if name.startswith("rand") and t.n >= 50:
    long = [anneal(t, 3 * it, seed=900 + s)[1] for s in range(4)]
json.dump(dict(name=name, n=t.n, iters=it, vals=vals, times=times, long=long), open(f"results/raw_{name}.json", "w"))
print("done", name)
