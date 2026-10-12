"""Ģenerē testa piemērus mapē instances/ un ieraksta zināmos optimumus references.json."""
import random, math, json, itertools
ref = {}
def save(name, pts, opt=None, kind=""):
    with open(f"instances/{name}.txt", "w") as f:
        f.write(f"{len(pts)}\n")
        for x, y in pts: f.write(f"{x:.6f} {y:.6f}\n")
    ref[name] = {"n": len(pts), "kind": kind, "optimum": opt}
def held_karp(pts):
    n = len(pts); d = [[math.dist(a, b) for b in pts] for a in pts]; INF = float("inf")
    dp = [[INF] * n for _ in range(1 << n)]; dp[1][0] = 0.0
    for m in range(1 << n):
        if not m & 1: continue
        for j in range(n):
            v = dp[m][j]
            if v == INF: continue
            for k in range(n):
                if m >> k & 1: continue
                nm = m | 1 << k; nv = v + d[j][k]
                if nv < dp[nm][k]: dp[nm][k] = nv
    full = (1 << n) - 1
    return min(dp[full][j] + d[j][0] for j in range(1, n))
for n in (10, 13, 15):
    rng = random.Random(100 + n)
    pts = [(rng.random() * 100, rng.random() * 100) for _ in range(n)]
    save(f"rand{n}", pts, held_karp(pts), "nejaušs, optimums ar Held-Karp DP")
for m in (6, 10, 14):
    pts = [(float(x), float(y)) for x in range(m) for y in range(m)]
    save(f"grid{m}x{m}", pts, float(m * m), "režģis, zināms optimums = n")
for n in (50, 200, 500):
    pts = [(100 * math.cos(2 * math.pi * k / n), 100 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    random.Random(n).shuffle(pts)
    save(f"circle{n}", pts, 2 * n * 100 * math.sin(math.pi / n), "riņķa līnija, optimums = daudzstūra perimetrs")
for n in (50, 100, 200, 500):
    rng = random.Random(500 + n)
    pts = [(rng.random() * 1000, rng.random() * 1000) for _ in range(n)]
    save(f"rand{n}", pts, None, "nejaušs, bez zināma optimuma")
json.dump(ref, open("instances/references.json", "w"), indent=1)
print({k: (v["n"], v["optimum"]) for k, v in ref.items()})
