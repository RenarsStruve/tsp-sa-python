"""Apvieno results/raw_*.json -> results.csv / results.json, uzzīmē grafikus."""
import json, csv, statistics, glob
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from tsp_sa import TSP, anneal
ref = json.load(open("instances/references.json"))
order = ["rand10","rand13","rand15","grid6x6","circle50","rand50","rand100","grid10x10","rand200","circle200","grid14x14","rand500","circle500"]
rows = []
for name in order:
    r = json.load(open(f"results/raw_{name}.json")); v = r["vals"]; o = ref[name]["optimum"]
    if o is not None: opt, typ = o, "optimums"
    else: opt, typ = min(v + r["long"]), "labākais atrastais"
    g = [100 * (x - opt) / opt for x in v]
    rows.append(dict(instance=name, n=r["n"], ref_type=typ, reference=round(opt, 3), iterations=r["iters"], runs=len(v),
        best=round(min(v), 3), mean=round(statistics.mean(v), 3), worst=round(max(v), 3),
        best_gap_pct=round(max(0, min(g)), 2), mean_gap_pct=round(max(0, statistics.mean(g)), 2),
        hits=sum(1 for x in g if x < 1e-4), mean_time_s=round(statistics.mean(r["times"]), 2)))
with open("results/results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
json.dump(rows, open("results/results.json", "w"), indent=1)
for x in rows: print(x["instance"], x["n"], x["ref_type"], x["reference"], x["best"], x["mean"], x["mean_gap_pct"], x["hits"], x["mean_time_s"])
t = TSP.load("instances/rand200.txt")
tour, L, hist, _ = anneal(t, 2_000_000, seed=0, log_every=5000)
fig, ax = plt.subplots(figsize=(6, 3.4))
ax.plot([h[0] for h in hist], [h[1] for h in hist], label="pašreizējais", lw=.8); ax.plot([h[0] for h in hist], [h[2] for h in hist], label="labākais", lw=1.4)
ax.set_xlabel("iterācija"); ax.set_ylabel("maršruta garums"); ax.set_title("SA konverģence (rand200)"); ax.legend(); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig("results/convergence_rand200.png", dpi=130); plt.close()
fig, axs = plt.subplots(1, 2, figsize=(9, 4.3))
for a, nm in zip(axs, ("rand200", "grid10x10")):
    t = TSP.load(f"instances/{nm}.txt"); tour, L, _, _ = anneal(t, 2_000_000 if nm == "rand200" else 1_000_000, seed=0)
    xs = [t.coords[i][0] for i in tour + [tour[0]]]; ys = [t.coords[i][1] for i in tour + [tour[0]]]
    a.plot(xs, ys, "-o", ms=2.5, lw=1); a.set_title(f"{nm}: garums {L:.1f}"); a.set_aspect("equal"); a.axis("off")
plt.tight_layout(); plt.savefig("results/tours.png", dpi=130)
