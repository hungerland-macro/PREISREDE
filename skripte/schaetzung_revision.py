#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schätzungen der überarbeiteten Fassung.

Hauptmodell (Fehlerkorrektur in Niveaus): log A_t = c + c_B·B_t + φ·log A_{t-1} + β·π_t + β_B·B_t·π_t
B_t = 1 ab dem Bruchjahr. Das entspricht einem ECM mit regimeeigenem Langfristmittel
(c + c_B)/(1-φ) und Langfristwirkung (β + β_B)/(1-φ). HAC-Standardfehler, drei Lags.

Prüfungen: Bruch 1990 und 1999; Index aller privaten Haushalte (1963-2025); ohne je eine
Inflationsepisode; ohne 1951/52 und 2022/23 zugleich; Redetext statt Protokoll; Placebo-Felder.
Aufruf: python schaetzung_revision.py
"""
import csv, os
import numpy as np
import statsmodels.api as sm

DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")


def lies(name):
    with open(os.path.join(DATEN, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


P = {int(r["jahr"]): float(r["preisniveau_je_mio_woerter"].replace(",", ".")) for r in lies("plenum_jahr.csv")}
INFL = lies("inflation.csv")
RATE = {int(r["jahr"]): float(r["vpi_rate"]) for r in INFL}
RATE_ALLE = dict(RATE)
RATE_ALLE.update({int(r["jahr"]): float(r["alle_priv_hh_frueheres_bundesgebiet"]) for r in INFL if r["alle_priv_hh_frueheres_bundesgebiet"]})
EPISODEN = {"1951-52": (1951, 1952), "1970-75": (1970, 1975), "1979-82": (1979, 1982),
            "1991-93": (1991, 1993), "2021-23": (2021, 2023)}


def reihe_aus(datei, feld="preisniveau"):
    r = lies(datei)
    return {int(x["jahr"]): 1e6 * int(x[feld]) / int(x["woerter"]) for x in r if int(x["woerter"])}


def ecm(A, rate=RATE, bruch=1999, start=1951, ende=2025, ohne=()):
    J = np.array([j for j in range(start, ende + 1) if j not in ohne and (j - 1) in A and j in A])
    y = np.log([A[j] for j in J]); yl = np.log([A[j - 1] for j in J])
    pi = np.array([rate[j] for j in J]); B = (J >= bruch).astype(float)
    X = sm.add_constant(np.column_stack([B, yl, pi, B * pi]))
    m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    c, cB, phi, b, bB = m.params
    lr = lambda reg, p: np.exp((c + cB * reg + (b + bB * reg) * p) / (1 - phi))
    return m, dict(n=len(J), phi=phi, beta=b, beta_B=bB, p_bB=m.pvalues[4], cB=cB, p_cB=m.pvalues[1],
                   lr_vor_2=lr(0, 2), lr_nach_2=lr(1, 2), lr_vor_6=lr(0, 6), lr_nach_6=lr(1, 6),
                   lr_slope_vor=b / (1 - phi), lr_slope_nach=(b + bB) / (1 - phi))


def zeige(name, d):
    print(f"{name:38s} n={d['n']:2d} φ={d['phi']:.2f} β={d['beta']:.3f} β_B={d['beta_B']:.3f} (p={d['p_bB']:.3f}) "
          f"c_B={d['cB']:.2f} (p={d['p_cB']:.3f}) | bei 2 %: {d['lr_vor_2']:.0f}→{d['lr_nach_2']:.0f}, "
          f"bei 6 %: {d['lr_vor_6']:.0f}→{d['lr_nach_6']:.0f}")


def ohne_episode(J):
    return tuple(j for a, b in [EPISODEN[k] for k in J] for j in range(a, b + 1))


if __name__ == "__main__":
    print("Hauptmodell und Bruchjahr")
    for b in (1990, 1999):
        zeige(f"Protokolle, Bruch {b}", ecm(P, bruch=b)[1])
    m, _ = ecm(P)
    print(m.summary().tables[1])
    zeige("Index aller Haushalte, 1964-2025", ecm(P, rate=RATE_ALLE, start=1964)[1])
    zeige("ab 1953", ecm(P, start=1953)[1])
    print("\nOhne je eine Episode (Bruch 1999)")
    for k in EPISODEN:
        zeige(f"ohne {k}", ecm(P, ohne=ohne_episode([k]))[1])
    zeige("ohne 1951-52 und 2021-23", ecm(P, ohne=ohne_episode(["1951-52", "2021-23"]))[1])
    zeige("ohne 1951-52, 2021-23, Bruch 1990", ecm(P, bruch=1990, ohne=ohne_episode(["1951-52", "2021-23"]))[1])


def bruchtest_ecm(A, rate=RATE, von=1975, bis=2005, n_boot=2000, seed=3):
    """Sup-F über Bruchjahre im Niveaumodell (Niveau und Steigung brechen), Bootstrap unter H0 ohne Bruch."""
    J = np.arange(1951, 2026)
    y = np.log([A[j] for j in J]); yl = np.log([A[j - 1] for j in J]); pi = np.array([rate[j] for j in J])
    X0 = sm.add_constant(np.column_stack([yl, pi]))

    def supf(yy):
        ssr0 = sm.OLS(yy, X0).fit().ssr
        best = (0, None)
        for b in range(von, bis + 1):
            B = (J >= b).astype(float)
            X1 = np.column_stack([X0, B, B * pi])
            ssr1 = sm.OLS(yy, X1).fit().ssr
            f = ((ssr0 - ssr1) / 2) / (ssr1 / (len(yy) - X1.shape[1]))
            best = max(best, (f, b))
        return best

    f_obs, jahr = supf(y)
    m0 = sm.OLS(y, X0).fit()
    rng = np.random.default_rng(seed)
    p = np.mean([supf(m0.fittedvalues + rng.choice(m0.resid, len(y)))[0] >= f_obs for _ in range(n_boot)])
    return jahr, f_obs, p


if __name__ == "__main__":
    j, f, p = bruchtest_ecm(P)
    print(f"\nBruchtest Niveaumodell 1975-2005: Bruchjahr {j}, sup-F {f:.2f}, p = {p:.3f}")
