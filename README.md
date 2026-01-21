# TP2 — Analyse des performances (Boss / Minions avec multiprocessing)

## Prerequis

### outils C++ (TP4)

```bash
sudo apt update
sudo apt install -y build-essential cmake libeigen3-dev
```

### dans le dossier du repo

```bash
uv sync
```

## Pour tester

### Terminal 1

```bash
uv run python queue_manager.py
```

### Terminal 2

```bash
uv run python minion.py
```

### Terminal 3

```bash
uv run python minion.py
```

### Terminal 4

```bash
uv run python boss.py --minions 2 --tasks 10 --size 300 --step 50
```

## Protocole expérimental

Pour comparer les performances, nous utilisons un script de benchmark qui :

1. démarre un **QueueManager** (serveur) qui expose `task_queue` et `result_queue`
2. démarre **N minions** (workers) qui consomment les tâches et exécutent `Task.work()`
3. exécute le **Boss** qui envoie `T` tâches, récupère `T` résultats, puis envoie `N` signaux d’arrêt (`None`)
4. mesure le **temps total (wall time)** et calcule le débit (**throughput** en tâches/seconde)

Chaque configuration est répétée plusieurs fois (repeats) et on calcule la moyenne et l’écart-type.

---

## Résultats — Série 1 (10 tâches, tailles 300 → 750, pas 50, 3 répétitions)

| minions | tasks | size | step | repeats | wall_mean(s) |  wall_sd | throughput(task/s) | throughput_sd | mean_task_time(s) | max_task_time(s) | sum_task_time(s) |
| ------- | ----- | ---- | ---- | ------- | -----------: | -------: | -----------------: | ------------: | ----------------: | ---------------: | ---------------: |
| 1       | 10    | 300  | 50   | 3       |     0.524681 | 0.028159 |             19.112 |         0.990 |          0.005761 |         0.010485 |         0.057614 |
| 2       | 10    | 300  | 50   | 3       |     0.485471 | 0.011231 |             20.610 |         0.485 |          0.007641 |         0.014955 |         0.076405 |
| 4       | 10    | 300  | 50   | 3       |     0.489810 | 0.007130 |             20.420 |         0.295 |          0.007548 |         0.014621 |         0.075483 |

### Analyse (Série 1)

- Le passage de **1 à 2 minions** réduit le temps total moyen (≈ 0.525s → 0.485s) et augmente légèrement le débit (≈ 19.1 → 20.6 tâches/s).
- Le passage à **4 minions** n’apporte pas de gain supplémentaire (wall time ≈ 0.490s, très proche de 2 minions).
- Sur un petit nombre de tâches et des tailles modérées, le **coût de gestion/communication** (queues, sérialisation, synchronisation) devient comparable au temps de calcul, ce qui limite le bénéfice de paralléliser davantage.

---

## Résultats — Série 2 (40 tâches, tailles 600 → 1575, pas 25, 3 répétitions)

| minions | tasks | size | step | repeats | wall_mean(s) |  wall_sd | throughput(task/s) | throughput_sd | mean_task_time(s) | max_task_time(s) | sum_task_time(s) |
| ------- | ----- | ---- | ---- | ------- | -----------: | -------: | -----------------: | ------------: | ----------------: | ---------------: | ---------------: |
| 1       | 40    | 600  | 25   | 3       |     3.741979 | 0.475967 |             10.851 |         1.270 |          0.037472 |         0.096232 |         1.498899 |
| 2       | 40    | 600  | 25   | 3       |     2.686039 | 0.023018 |             14.893 |         0.128 |          0.047770 |         0.128747 |         1.910817 |
| 4       | 40    | 600  | 25   | 3       |     2.839947 | 0.155501 |             14.126 |         0.755 |          0.054369 |         0.125382 |         2.174753 |
| 8       | 40    | 600  | 25   | 3       |     2.977199 | 0.052528 |             13.440 |         0.239 |          0.056770 |         0.128411 |         2.270795 |

### Analyse (Série 2)

- Le gain est net entre **1 et 2 minions** :
  - wall time moyen ≈ **3.74s → 2.69s** (accélération visible)
  - throughput ≈ **10.85 → 14.89 tâches/s**
- Au-delà (**4 et 8 minions**), les performances se dégradent :
  - 4 minions : wall ≈ 2.84s (moins bon que 2)
  - 8 minions : wall ≈ 2.98s (encore moins bon)

## Conclusion

- Le parallélisme apporte un bénéfice clair jusqu’à **2 minions**, qui est la configuration la plus performante sur les essais réalisés.

# lancer les tests

```bash
uv run python -m unittest -v
```

# vérifier qualité/format

```bash
uv run pre-commit run -a
```

## TP 4

```bash
uv run python proxy.py --port 8000
```

```bash
cmake -B build -S .
cmake --build build -j
./build/low_level 400
```

## TP4 — Validation et mesures de performance (Proxy HTTP Python + client C++)

### Commandes utilisées

**Terminal 1 (proxy Python)**

```bash
uv run python proxy.py --port 8000
./build/low_level 200
./build/low_level 400
./build/low_level 800
```

| Taille n | proxy_time (s) | residual_norm |
| -------: | -------------: | ------------: |
|      200 |    0.000366465 |   5.08077e-13 |
|      400 |     0.00233888 |   1.14833e-12 |
|      800 |       0.014518 |   9.43684e-12 |

### Analyse

- **Correction** : les valeurs de `residual_norm` sont très petites (de l’ordre de **10^-12**), ce qui confirme :
  - la compatibilité du format JSON entre C++ et Python ;
  - la reconstruction correcte de `Task` côté proxy ;
  - la cohérence du calcul de la solution `x`.

- **Performance** : `proxy_time` augmente fortement avec la taille `n` :
  - la résolution d’un système linéaire dense a une complexité proche de **O(n^3)** ;
  - la hausse observée entre **200 -> 400 -> 800** est cohérente avec un coût de calcul dominant ;
  - la sérialisation/désérialisation JSON et le transport HTTP ajoutent un surcoût, mais lorsque `n` augmente, le temps de calcul devient prépondérant.

- **Conclusion** : le proxy HTTP permet une communication fiable C++ <-> Python via JSON, et le temps de traitement est majoritairement lié à la taille du système linéaire.
