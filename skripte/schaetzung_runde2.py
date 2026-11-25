#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prüfungen der zweiten Gutachtenrunde (25.11.2026).

1. Inflationsgedächtnis: Höchstrate und Mittel der letzten zehn Jahre als zusätzliche Regressoren.
2. Modellfreier Vergleich: Median ruhiger Jahre (Rate < 3 %), auch 1953-1969 gegen 1999-2025.
3. Langfristverhältnis ab/vor Bruch für Raten 0 bis 5 % mit 90-%-Band (Ziehungen aus der HAC-Kovarianz).
4. Residuen 2023-2026 des Hauptmodells (Persistenz nach 2022).
5. Breusch-Godfrey-Test; Konfidenzmenge des Bruchjahrs nach dem Likelihood-Quotienten (Eo & Morley 2015).
6. Verbreitung: Anteil der Sitzungen mit mindestens einem Treffer.
Aufruf: python schaetzung_runde2.py
"""
import csv, os, statistics as st
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schaetzung_revision import P, RATE, ecm, lies, DATEN

J = np.arange(1951, 2026)


def daten(A, bruch=1999, ohne=(), extra=None, start=1951):
    JJ = np.array([j for j in range(start, 2026) if j not in ohne])
    y = np.log([A[j] for j in JJ]); yl = np.log([A[j - 1] for j in JJ])
    pi = np.array([RATE[j] for j in JJ]); B = (JJ >= bruch).astype(float)
    cols = [B, yl, pi, B * pi]
    if extra is not None:
        cols.append(np.array([extra(j) for j in JJ]))
    return JJ, y, sm.add_constant(np.column_stack(cols))


def hac(y, X):
    return sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})


max10 = lambda j: max(RATE[k] for k in range(max(1950, j - 10), j))
mit10 = lambda j: st.mean(RATE[k] for k in range(max(1950, j - 10), j))

if __name__ == "__main__":
    print("1. Inflationsgedächtnis (Bruch 1999)")
    for name, f in (("Höchstrate letzte 10 Jahre", max10), ("Mittel letzte 10 Jahre", mit10)):
        _, y, X = daten(P, extra=f)
        m = hac(y, X)
        c, cB, phi, b, bB, g = m.params
        lr = lambda reg, p, mem: np.exp((c + cB * reg + (b + bB * reg) * p + g * mem) / (1 - phi))
        print(f"   {name}: Koeff {g:.3f} (p={m.pvalues[5]:.3f}); Niveau ab Bruch {cB:.3f} (p={m.pvalues[1]:.3f}); "
              f"Rate ab Bruch {bB:.3f} (p={m.pvalues[4]:.3f}); Langfrist bei 2 %, Gedächtnis 3 %: {lr(0,2,3):.0f} → {lr(1,2,3):.0f}")
    _, y, X = daten(P, extra=max10, ohne=tuple(range(2021, 2024)))
    m = hac(y, X); print(f"   Höchstrate, ohne 2021-23: Niveau ab Bruch {m.params[1]:.3f} (p={m.pvalues[1]:.3f})")

    print("\n2. Median ruhiger Jahre (Rate < 3 %)")
    ruhig = lambda a, b: [P[j] for j in range(a, b + 1) if RATE[j] < 3]
    for a, b, c_, d in ((1951, 1998, 1999, 2025), (1953, 1969, 1999, 2025), (1953, 1969, 1999, 2020), (1983, 1989, 1999, 2020)):
        v, n = ruhig(a, b), ruhig(c_, d)
        print(f"   {a}-{b}: {st.median(v):.0f} (n={len(v)})  gegen {c_}-{d}: {st.median(n):.0f} (n={len(n)})  Verhältnis {st.median(n)/st.median(v):.2f}")
    v = [RATE[j] for j in range(1953, 1970) if RATE[j] < 3]; n = [RATE[j] for j in range(1999, 2026) if RATE[j] < 3]
    print(f"   mittlere Rate dieser Jahre: {st.mean(v):.1f} gegen {st.mean(n):.1f}")

    print("\n3. Langfristverhältnis ab/vor Bruch, 90-%-Band")
    rng = np.random.default_rng(5)
    for name, kw in (("Bruch 1999", {}), ("ohne 1951-52, 2021-23", {"ohne": (1951, 1952, 2021, 2022, 2023)})):
        _, y, X = daten(P, **kw); m = hac(y, X)
        draws = rng.multivariate_normal(m.params, m.cov_params(), 5000)
        zeile = []
        for p in (0, 1, 2, 3, 4, 5):
            r = np.exp((draws[:, 1] + draws[:, 4] * p) / (1 - draws[:, 2]))
            zeile.append(f"{p} %: {np.median(r):.2f} [{np.percentile(r,5):.2f}-{np.percentile(r,95):.2f}]")
        print(f"   {name}: " + "; ".join(zeile))

    print("\n4. Residuen nach 2022 (Hauptmodell bis 2025, 2026 vorhergesagt)")
    JJ, y, X = daten(P); m = sm.OLS(y, X).fit()
    for j in (2023, 2024, 2025):
        i = list(JJ).index(j); print(f"   {j}: beobachtet {P[j]:.0f}, angepasst {np.exp(m.fittedvalues[i]):.0f}, Residuum {m.resid[i]:+.2f}")
    x26 = np.array([1, 1, np.log(P[2025]), 2.6, 2.6]); print(f"   2026: beobachtet {P[2026]:.0f}, vorhergesagt {np.exp(x26 @ m.params):.0f}")
    print(f"   Langfristwert ab Bruch bei 2,2 %: {np.exp((m.params[0]+m.params[1]+(m.params[3]+m.params[4])*2.2)/(1-m.params[2])):.0f}")
    print(f"   Residuen 2015-2020 Mittel {np.mean([m.resid[list(JJ).index(j)] for j in range(2015,2021)]):+.2f}")

    print("\n5. Diagnostik")
    for lags in (1, 2, 3):
        lm, p, _, _ = acorr_breusch_godfrey(m, nlags=lags); print(f"   Breusch-Godfrey {lags} Lags: p = {p:.3f}")
    ssr = {}
    for b in range(1975, 2006):
        _, yy, XX = daten(P, bruch=b); ssr[b] = sm.OLS(yy, XX).fit().ssr
    bmin = min(ssr, key=ssr.get); n = len(J)
    menge = [b for b in ssr if n * np.log(ssr[b] / ssr[bmin]) <= 7.35]
    print(f"   Bruchjahr mit kleinster Residuenquadratsumme {bmin}; LR-Konfidenzmenge 95 %: {menge}")

    print("\n6. Anteil der Sitzungen mit mindestens einem Treffer")
    pr = lies("plenum_protokolle.csv")
    ant = {}
    for j in range(1950, 2026):
        z = [r for r in pr if int(r["jahr"]) == j]
        ant[j] = np.mean([int(r["treffer_preisniveau"]) > 0 for r in z])
    for a, b in ((1953, 1969), (1951, 1998), (1999, 2025), (1999, 2020)):
        v = [ant[j] for j in range(a, b + 1) if RATE[j] < 3]
        print(f"   ruhige Jahre {a}-{b}: Median {st.median(v):.0%}")
    print(f"   1973 {ant[1973]:.0%}, 2022 {ant[2022]:.0%}, 2019 {ant[2019]:.0%}")
