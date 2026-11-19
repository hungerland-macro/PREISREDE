#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schätzungen der Note "Wann das Parlament über Preise spricht".

Tabelle 1: log-Niveau mit Vorjahreswert; Veränderung getrennt nach Anstieg und
Rückgang der Rate, mit Bruch 1990. Tabelle 2: Schwelle über ein Gitter.
Robustheit: ohne 2022, Bruch 2000, Index aller privaten Haushalte ab 1963.
HAC-Standardfehler mit drei Lags. Aufruf: python schaetzung.py
"""

import csv
import os

import numpy as np
import statsmodels.api as sm

DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")


def lies(name):
    with open(os.path.join(DATEN, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


P = {int(r["jahr"]): float(r["preisniveau_je_mio_woerter"].replace(",", "."))
     for r in lies("plenum_jahr.csv")}
INFL = lies("inflation.csv")
RATE = {int(r["jahr"]): float(r["vpi_rate"]) for r in INFL}
RATE_ALLE = dict(RATE)
RATE_ALLE.update({int(r["jahr"]): float(r["alle_priv_hh_frueheres_bundesgebiet"])
                  for r in INFL if r["alle_priv_hh_frueheres_bundesgebiet"]})


def hac(y, X):
    return sm.OLS(y, sm.add_constant(X)).fit(cov_type="HAC", cov_kwds={"maxlags": 3})


def zeile(name, m, i):
    print(f"   {name:36s} {m.params[i]:7.3f}  (p = {m.pvalues[i]:.3f})")


def tabelle1(rate, bruch=1990, ohne=None):
    J = np.arange(1950, 2026)
    ly = np.log([P[j] for j in J])
    pi = np.array([rate[j] for j in J])
    m1 = hac(ly[1:], np.column_stack([pi[1:], ly[:-1]]))
    d, dp = np.diff(ly), np.diff(pi)
    auf, ab = np.where(dp > 0, dp, 0), np.where(dp < 0, dp, 0)
    s = (J[1:] >= bruch).astype(float)
    X = np.column_stack([auf, ab, auf * s, ab * s, s])
    k = np.ones(len(d), bool) if ohne is None else J[1:] != ohne
    m2 = hac(d[k], X[k])
    m0 = hac(d, np.column_stack([auf, ab]))
    return m1, m2, m0


def schwelle(J, rate, anteil=0.15):
    J = list(J)
    y = np.log([P[j] for j in J])
    yl = np.log([P[j - 1] for j in J])
    pi = np.array([rate[j] for j in J])
    n, mind = len(J), int(anteil * len(J))
    best = None
    for t in np.round(np.arange(0.5, 7.01, 0.1), 1):
        oben = pi >= t - 1e-9
        if oben.sum() < mind or n - oben.sum() < mind:
            continue
        X = sm.add_constant(np.column_stack([pi, oben * (pi - t), yl]))
        m = sm.OLS(y, X).fit()
        if best is None or m.ssr < best[0]:
            best = (m.ssr, t, int(oben.sum()), X)
    _, t, k, X = best
    m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    return t, k, n, m.params[1], m.params[1] + m.params[2], m.pvalues[2]


if __name__ == "__main__":
    J = np.arange(1950, 2026)
    y = np.array([P[j] for j in J])
    pi = np.array([RATE[j] for j in J])
    print(f"Korrelation gleichzeitig {np.corrcoef(y, pi)[0, 1]:.2f}, "
          f"mit Vorjahresrate {np.corrcoef(y[1:], pi[:-1])[0, 1]:.2f}")

    m1, m2, m0 = tabelle1(RATE)
    print(f"\nTabelle 1, Spalte 1 (n = {int(m1.nobs)}, R² = {m1.rsquared:.2f})")
    zeile("Inflationsrate", m1, 1)
    zeile("Aufmerksamkeit im Vorjahr, log", m1, 2)
    print(f"   langfristig {m1.params[1] / (1 - m1.params[2]):.3f}")
    print(f"\nAsymmetrie ohne Bruch: Differenz p = "
          f"{float(np.ravel(m0.t_test('x1 - x2 = 0').pvalue)[0]):.3f}")
    print(f"\nTabelle 1, Spalte 2 (n = {int(m2.nobs)}, R² = {m2.rsquared:.2f})")
    for i, name in enumerate(["Anstieg der Rate", "Rückgang der Rate",
                              "Anstieg, zusätzlich ab 1990", "Rückgang, zusätzlich ab 1990",
                              "Niveau ab 1990"], 1):
        zeile(name, m2, i)

    print("\nRobustheit Anstieg ab Bruch")
    for lab, kw in [("ohne 2022", {"ohne": 2022}), ("Bruch 2000", {"bruch": 2000}),
                    ("Bruch 2000 ohne 2022", {"bruch": 2000, "ohne": 2022})]:
        zeile(lab, tabelle1(RATE, **kw)[1], 3)
    zeile("Index aller privaten Haushalte", tabelle1(RATE_ALLE)[1], 3)

    print("\nTabelle 2: Schwelle")
    for von, bis in [(1951, 2025), (1951, 1989), (1990, 2025)]:
        t, k, n, u, o, p = schwelle(range(von, bis + 1), RATE)
        print(f"   {von}-{bis}: {t:.1f} %, {k} von {n} Jahren ab Schwelle, "
              f"unterhalb {u:.3f}, oberhalb {o:.3f}, p Zusatzterm {p:.3f}")
