# TSP risināšana ar simulēto rūdīšanu (SA)

Autors: Renārs Strūve (rs26073). Optimizācijas algoritms uzrakstīts pašu spēkiem (tikai Python standartbibliotēka; matplotlib tiek izmantots tikai grafikiem).

## Struktūra
- `tsp_sa.py` – problēma (domēns, novērtēšana, gājiens) un SA algoritms
- `gen_instances.py` – ģenerē testa piemērus `instances/` un zināmos optimumus (`references.json`)
- `bench_one.py <piemērs>` – testa palaišanas vienam piemēram → `results/raw_*.json`
- `aggregate.py` – apvieno rezultātus → `results/results.csv`, grafiki
- `instances/` – testa piemēri (formāts: pirmā rinda n, tālāk `x y`); tiek atbalstīts arī TSPLIB `.tsp`

## Palaišana
```
python3 gen_instances.py
for n in rand10 rand13 rand15 grid6x6 circle50 rand50 rand100 grid10x10 rand200 circle200 grid14x14 rand500 circle500; do python3 bench_one.py $n; done
python3 aggregate.py
```
Atsevišķs risinājums:
```python
from tsp_sa import TSP, anneal
t = TSP.load("instances/rand100.txt")
tour, length, hist, T0 = anneal(t, iters=1_000_000, seed=0)
```
Prasības: Python 3.9+, matplotlib (tikai `aggregate.py`).
