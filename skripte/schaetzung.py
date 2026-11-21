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


def sup_f(y, yl, pi, gitter, mind):
    """F-Statistik je Schwelle gegen das lineare Modell; Maximum über das Gitter."""
    X0 = sm.add_constant(np.column_stack([pi, yl]))
    ssr0 = sm.OLS(y, X0).fit().ssr
    beste = 0.0
    for t in gitter:
        oben = pi >= t - 1e-9
        if oben.sum() < mind or len(y) - oben.sum() < mind:
            continue
        X1 = np.column_stack([X0, oben * (pi - t)])
        ssr1 = sm.OLS(y, X1).fit().ssr
        beste = max(beste, (ssr0 - ssr1) / (ssr1 / (len(y) - X1.shape[1])))
    return beste


def bootstrap_schwelle(J, reihe, rate, n_boot=2000, seed=1):
    """p-Wert der Schwelle nach Hansen (1996): Residuen-Bootstrap unter dem
    linearen Modell, Regressoren fest, sup-F über dasselbe Gitter."""
    J = list(J)
    y = np.log([reihe[j] for j in J])
    yl = np.log([reihe[j - 1] for j in J])
    pi = np.array([rate[j] for j in J])
    gitter = np.round(np.arange(0.5, 7.01, 0.1), 1)
    mind = int(0.15 * len(J))
    f_obs = sup_f(y, yl, pi, gitter, mind)
    X0 = sm.add_constant(np.column_stack([pi, yl]))
    m0 = sm.OLS(y, X0).fit()
    rng = np.random.default_rng(seed)
    treffer = 0
    for _ in range(n_boot):
        yb = m0.fittedvalues + rng.choice(m0.resid, len(y), replace=True)
        treffer += sup_f(yb, yl, pi, gitter, mind) >= f_obs
    return f_obs, treffer / n_boot


def ohne_mittelbar():
    """Plenumsreihe ohne Inflationsausgleich... und Inflation Reduction Act."""
    pfad = os.path.join(DATEN, "validierung_jahr.csv")
    return {int(r["jahr"]): float(r["preisniveau_ohne_mittelbar_je_mio"])
            for r in csv.DictReader(open(pfad, encoding="utf-8"), delimiter=";")}


if __name__ == "__main__":
    print("\nSchwelle 1990-2025, Bootstrap-p-Wert (Hansen 1996, 2000 Ziehungen)")
    f, p = bootstrap_schwelle(range(1990, 2026), P, RATE)
    print(f"   sup-F {f:.2f}, p = {p:.3f}")
    Q = ohne_mittelbar()
    print("\nReihe ohne Inflationsausgleich-Komposita")
    print(f"   Spitzen: 1973 {Q[1973]:.0f}, 2022 {Q[2022]:.0f}, 2023 {Q[2023]:.0f}, 2025 {Q[2025]:.0f}")
    P.clear(); P.update(Q)
    m1, m2, _ = tabelle1(RATE)
    zeile("Inflationsrate (Spalte 1)", m1, 1)
    zeile("Anstieg, zusätzlich ab 1990 (Spalte 2)", m2, 3)
    t, k, n, u, o, ps = schwelle(range(1990, 2026), RATE)
    print(f"   Schwelle ab 1990: {t:.1f} %, oberhalb {o:.3f}, p (HAC) {ps:.3f}")
    f, p = bootstrap_schwelle(range(1990, 2026), Q, RATE)
    print(f"   Bootstrap: sup-F {f:.2f}, p = {p:.3f}")


def spalte2_X(J, rate, bruch):
    J = np.asarray(J)
    pi = np.array([rate[j] for j in J])
    dp = np.diff(pi)
    auf, ab = np.where(dp > 0, dp, 0), np.where(dp < 0, dp, 0)
    s = (J[1:] >= bruch).astype(float)
    return np.column_stack([auf, ab, auf * s, ab * s, s]), np.column_stack([auf, ab])


def bruchtest(reihe, rate, von=1975, bis=2005, n_boot=2000, seed=2):
    """Sup-F über mögliche Bruchjahre in Spalte 2, p-Wert per Residuen-Bootstrap
    unter dem Modell ohne Bruch."""
    J = np.arange(1950, 2026)
    d = np.diff(np.log([reihe[j] for j in J]))

    def supf(y):
        _, X0 = spalte2_X(J, rate, 1990)
        ssr0 = sm.OLS(y, sm.add_constant(X0)).fit().ssr
        best, jahr = 0.0, None
        for b in range(von, bis + 1):
            X1 = sm.add_constant(spalte2_X(J, rate, b)[0])
            ssr1 = sm.OLS(y, X1).fit().ssr
            f = ((ssr0 - ssr1) / 3) / (ssr1 / (len(y) - X1.shape[1]))
            if f > best:
                best, jahr = f, b
        return best, jahr

    f_obs, jahr = supf(d)
    _, X0 = spalte2_X(J, rate, 1990)
    m0 = sm.OLS(d, sm.add_constant(X0)).fit()
    rng = np.random.default_rng(seed)
    p = np.mean([supf(m0.fittedvalues + rng.choice(m0.resid, len(d)))[0] >= f_obs
                 for _ in range(n_boot)])
    return jahr, f_obs, p


def ohne_je_ein_jahr(reihe, rate):
    J = np.arange(1950, 2026)
    d = np.diff(np.log([reihe[j] for j in J]))
    X = sm.add_constant(spalte2_X(J, rate, 1990)[0])
    werte = []
    for i in range(len(d)):
        k = np.arange(len(d)) != i
        werte.append((sm.OLS(d[k], X[k]).fit().params[3], J[1:][i]))
    return min(werte), max(werte)


if __name__ == "__main__":
    P0 = {int(r["jahr"]): float(r["preisniveau_je_mio_woerter"].replace(",", "."))
          for r in lies("plenum_jahr.csv")}
    lo, hi = ohne_je_ein_jahr(P0, RATE)
    print(f"\nAnstieg ab 1990 ohne je ein Jahr: {lo[0]:.3f} (ohne {lo[1]}) bis {hi[0]:.3f} (ohne {hi[1]})")
    jahr, f, p = bruchtest(P0, RATE)
    print(f"Bruchtest 1975-2005: Bruchjahr {jahr}, sup-F {f:.2f}, p = {p:.3f}")
    pl = {int(r["jahr"]): float(r["placebo_je_mio"]) for r in
          csv.DictReader(open(os.path.join(DATEN, "validierung_jahr.csv"), encoding="utf-8"), delimiter=";")}
    J = range(1950, 2026)
    print(f"Placebo (Bundeswehr, Verteidigung) gegen Inflation: r = "
          f"{np.corrcoef([pl[j] for j in J], [RATE[j] for j in J])[0, 1]:.2f}")
    y = np.array([P0[j] for j in J]); pi = np.array([RATE[j] for j in J])
    k = np.array([j not in (1970, 1971, 1972, 1973, 1974, 1975, 2022, 2023) for j in J])
    print(f"Korrelation ohne 1970-75 und 2022-23: {np.corrcoef(y[k], pi[k])[0, 1]:.2f}; "
          f"in Veränderungen: {np.corrcoef(np.diff(np.log(y)), np.diff(pi))[0, 1]:.2f}")


if __name__ == "__main__":
    def spalte2(start, bruch, ohne=()):
        J = np.arange(start, 2026)
        X = sm.add_constant(spalte2_X(J, RATE, bruch)[0])
        d = np.diff(np.log([P0[j] for j in J]))
        k = ~np.isin(J[1:], ohne)
        return hac(d[k], X[k][:, 1:])
    print("\nSpalte 2 mit Bruch 1999")
    zeile("Anstieg, zusätzlich ab 1999", spalte2(1950, 1999), 3)
    zeile("dasselbe ohne 2022", spalte2(1950, 1999, (2022,)), 3)
    print("Spalte 2 ab 1953 (ohne Währungsreformjahre)")
    m = spalte2(1953, 1990)
    zeile("Anstieg vor 1990", m, 1)
    zeile("Anstieg, zusätzlich ab 1990", m, 3)
