"""Testēšana: katram piemēram 10 palaišanas ar dažādiem sākuma skaitļiem.
Ieraksta results/results.csv, results/results.json un grafikus."""
import json, time, csv, statistics, glob, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from tsp_sa import TSP, anneal

ref = json.load(open("instances/references.json"))
def budget(n):  # iterāciju skaits atkarībā no izmēra
    return 100_000 if n <= 15 else 500_000 if n <= 50 else 1_000_000 if n <= 100 else 2_000_000 if n <= 200 else 4_000_000
RUNS = 10
order = ["rand10","rand13","rand15","grid6x6","circle50","rand50","rand100","grid10x10","rand200","circle200","grid14x14","rand500","circle500"]
# atsauce nejaušiem piemēriem bez zināma optimuma: labākais atrastais no 6 ilgām palaišanām
# (3x lielāks budžets) un visām testa palaišanām (zemāk)
for name in ("rand50","rand100","rand200","rand500"):
    t = TSP.load(f"instances/{name}.txt")
    ref[name]["best_known"] = min(anneal(t, 3*budget(t.n), seed=900+s)[1] for s in range(6))
    print("ilgā atsauce", name, ref[name]["best_known"], flush=True)
raw = {}
for name in order:
    t = TSP.load(f"instances/{name}.txt"); it = budget(t.n)
    vals, times = [], []
    for s in range(RUNS if t.n < 500 else 5):
        t0 = time.perf_counter(); tour, L, _, _ = anneal(t, it, seed=s); times.append(time.perf_counter() - t0); vals.append(L)
    raw[name] = (vals, times, it, t.n)
    print("gatavs", name, flush=True)
rows = []
for name in order:
    vals, times, it, n = raw[name]; r = ref[name]
    if r["optimum"] is not None: opt = r["optimum"]
    else: opt = min(r["best_known"], min(vals))
    gaps = [100 * (v - opt) / opt for v in vals]
    rows.append(dict(instance=name, n=n, ref_type="optimums" if r["optimum"] is not None else "labākais atrastais (atsauce)",
        reference=round(opt, 3), iterations=it, runs=len(vals), best=round(min(vals), 3), mean=round(statistics.mean(vals), 3),
        worst=round(max(vals), 3), best_gap_pct=round(max(0, min(gaps)), 3), mean_gap_pct=round(max(0, statistics.mean(gaps)), 3),
        hits=sum(1 for g in gaps if g < 1e-4), mean_time_s=round(statistics.mean(times), 2)))
    print(rows[-1], flush=True)
with open("results/results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
json.dump(rows, open("results/results.json", "w"), indent=1)
# grafiki: konverģence un maršruti
t = TSP.load("instances/rand200.txt")
tour, L, hist, _ = anneal(t, budget(t.n), seed=0, log_every=5000)
fig, ax = plt.subplots(figsize=(6, 3.6))
ax.plot([h[0] for h in hist], [h[1] for h in hist], label="pašreizējais", lw=.8); ax.plot([h[0] for h in hist], [h[2] for h in hist], label="labākais", lw=1.4)
ax.set_xlabel("iterācija"); ax.set_ylabel("maršruta garums"); ax.set_title("SA konverģence (rand200)"); ax.legend(); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig("results/convergence_rand200.png", dpi=130); plt.close()
fig, axs = plt.subplots(1, 2, figsize=(9, 4.4))
for a, nm in zip(axs, ("rand200", "grid10x10")):
    t = TSP.load(f"instances/{nm}.txt"); tour, L, _, _ = anneal(t, budget(t.n), seed=0)
    xs = [t.coords[i][0] for i in tour + [tour[0]]]; ys = [t.coords[i][1] for i in tour + [tour[0]]]
    a.plot(xs, ys, "-o", ms=2.5, lw=1); a.set_title(f"{nm}: garums {L:.2f}"); a.set_aspect("equal"); a.axis("off")
plt.tight_layout(); plt.savefig("results/tours.png", dpi=130)
