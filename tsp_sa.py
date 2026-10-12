"""TSP risināšana ar simulēto rūdīšanu (Simulated Annealing).
Visa optimizācijas loģika uzrakstīta pašu spēkiem (bez gatavām optimizācijas bibliotēkām).
"""
import math, random, time

# ---------------- Domēns: problēmas instance ----------------
class TSP:
    def __init__(self, coords, name="instance"):
        self.name = name
        self.coords = coords
        self.n = len(coords)
        # pilna attālumu matrica (Eiklīda attālumi)
        self.d = [[math.hypot(a[0]-b[0], a[1]-b[1]) for b in coords] for a in coords]

    @staticmethod
    def load(path):
        """Nolasa vienkāršu formātu: pirmā rinda n, tālāk 'x y' katrā rindā;
        vai TSPLIB (.tsp) ar NODE_COORD_SECTION."""
        name = path.split('/')[-1].rsplit('.', 1)[0]
        lines = [l.strip() for l in open(path) if l.strip()]
        if any(l.startswith('NODE_COORD_SECTION') for l in lines):
            i = [k for k, l in enumerate(lines) if l.startswith('NODE_COORD_SECTION')][0] + 1
            pts = []
            while i < len(lines) and lines[i] != 'EOF':
                p = lines[i].split(); pts.append((float(p[1]), float(p[2]))); i += 1
        else:
            pts = [tuple(map(float, l.split()[:2])) for l in lines[1:]]
        return TSP(pts, name)

# ---------------- Novērtēšana ----------------
def tour_length(tsp, tour):
    d = tsp.d
    return sum(d[tour[i]][tour[(i + 1) % tsp.n]] for i in range(tsp.n))

# ---------------- Gājiens: 2-opt ar K tuvāko kaimiņu sarakstu ----------------
# Izvēlas pilsētu a un nejaušu tās tuvāko kaimiņu c; nomaina divas šķautnes ar (a,c) un
# otru pāri, apgriežot maršruta daļu (vienmēr īsāko no abām pusēm).
def knn_lists(tsp, K):
    n, d = tsp.n, tsp.d
    return [sorted((v for v in range(n) if v != u), key=lambda v: d[u][v])[:K] for u in range(n)]

def nearest_neighbour(tsp, rng):
    n, d = tsp.n, tsp.d
    cur = rng.randrange(n); tour = [cur]; seen = {cur}
    while len(tour) < n:
        nxt = min((v for v in range(n) if v not in seen), key=lambda v: d[cur][v])
        tour.append(nxt); seen.add(nxt); cur = nxt
    return tour

def reverse_path(tour, pos, i, j, n):
    """Apgriež ciklisko ceļu no pozīcijas i līdz j (ieskaitot); apgriež īsāko pusi."""
    length = (j - i) % n + 1
    if 2 * length > n:                      # apgriežot papildinājumu, iegūst to pašu ciklu
        i, j = (j + 1) % n, (i - 1) % n
        length = n - length
    for _ in range(length // 2):
        ci, cj = tour[i], tour[j]
        tour[i], tour[j] = cj, ci
        pos[cj] = i; pos[ci] = j
        i += 1
        if i == n: i = 0
        j -= 1
        if j < 0: j = n - 1

# ---------------- Algoritms: SA ----------------
def anneal(tsp, iters, seed=0, init="random", t_end_ratio=1e-4, K=10, log_every=0):
    rng = random.Random(seed)
    n, d = tsp.n, tsp.d
    K = min(K, n - 1)
    nb = knn_lists(tsp, K)
    tour = list(range(n))
    if init == "nn": tour = nearest_neighbour(tsp, rng)
    else: rng.shuffle(tour)
    pos = [0] * n
    for k, c in enumerate(tour): pos[c] = k
    cur = tour_length(tsp, tour); best, best_tour = cur, tour[:]

    def propose(a):
        c = nb[a][rng.randrange(K)]
        i, j = pos[a], pos[c]
        if rng.random() < 0.5:              # variants A: (a,succ a) un (c,succ c)
            b, e = tour[(i + 1) % n], tour[(j + 1) % n]
            return c, d[a][c] + d[b][e] - d[a][b] - d[c][e], (i + 1) % n, j
        pa, pc = tour[i - 1], tour[j - 1]    # variants B: (pred a,a) un (pred c,c)
        return c, d[a][c] + d[pa][pc] - d[pa][a] - d[pc][c], i, (j - 1) % n

    # sākuma temperatūra: vidējais pasliktinājums, ar ~80% pieņemšanas varbūtību
    ups = []
    for _ in range(3000):
        c, dl, _, _ = propose(rng.randrange(n))
        if dl > 1e-12: ups.append(dl)
    avg_up = sum(ups) / len(ups) if ups else 1.0
    T0 = -avg_up / math.log(0.8)
    T = T0
    alpha = t_end_ratio ** (1.0 / iters)            # ģeometriskā dzesēšana pa soļiem
    hist = []
    rand, exp, randrange = rng.random, math.exp, rng.randrange
    for it in range(iters):
        a = randrange(n)
        c, dl, p, q = propose(a)
        if dl <= 0 or rand() < exp(-dl / T):
            if c != tour[p] or dl != 0:      # novērš nulles gājienus
                reverse_path(tour, pos, p, q, n)
                cur += dl
                if cur < best - 1e-12:
                    best = cur; best_tour = tour[:]
        T *= alpha
        if log_every and it % log_every == 0: hist.append((it, cur, best))
    best = tour_length(tsp, best_tour)               # pārrēķins, lai izslēgtu uzkrāto kļūdu
    return best_tour, best, hist, T0
