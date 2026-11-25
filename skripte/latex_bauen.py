#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut latex/preisrede.tex aus der Markdown-Fassung der Note (eine Textquelle für Word und LaTeX).

Präambel und Satzspiegel stehen hier; Absätze, Abbildungen, Tabelle und Literatur
werden aus dem Markdown übernommen. Aufruf: python latex_bauen.py MANUSKRIPT.md DATUM
Danach: cd latex && latexmk -lualatex preisrede.tex && latexmk -c
"""
import re, sys, os

HIER = os.path.dirname(os.path.abspath(__file__))
PRAEAMBEL = open(os.path.join(HIER, "latex_praeambel.tex"), encoding="utf-8").read()


def inl(t):
    t = t.replace("\\", "\\textbackslash{}")
    for a, b in (("&", "\\&"), ("%", "\\%"), ("_", "\\_"), ("#", "\\#"), ("$", "\\$")):
        t = t.replace(a, b)
    t = re.sub(r"(https?://\S+?)([.,;)]?)(?=\s|$)", lambda m: "\\url{" + m.group(1) + "}" + m.group(2), t)
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
    t = re.sub(r"\*(.+?)\*", r"\\emph{\1}", t)
    t = t.replace(" – ", " -- ").replace("–", "--").replace("[", "{[}").replace("]", "{]}")
    t = re.sub(r"(\d) \\%", r"\1~\\%", t)
    t = re.sub(r"Abbildung (\d)", r"Abbildung~\\ref{fig:\1}", t)
    t = re.sub(r"Tabelle 1(?!:)", r"Tabelle~\\ref{tab:1}", t)
    return t


def main(md, datum):
    s = open(md, encoding="utf-8").read().split("---", 2)[2]
    titel = re.search(r'title: "(.+?)"', open(md, encoding="utf-8").read()).group(1)
    unter = re.search(r'subtitle: "(.+?)"', open(md, encoding="utf-8").read()).group(1)
    bl = [b.strip() for b in re.split(r"\n\s*\n", s) if b.strip()]
    out, i, nfig, abstract, jel = [], 0, 0, "", ""
    while i < len(bl):
        b = bl[i]
        if b.startswith("**Der Beitrag gibt"):
            pass
        elif b == "### Abstract":
            abstract = inl(bl[i + 1]); jel = bl[i + 2].split(":", 1)[1].strip(); i += 2
        elif b.startswith("### "):
            h = b[4:]
            out.append(("\\section*{" if h in ("Hinweis zum Einsatz von KI", "Literatur") else "\\section{") + inl(h) + "}")
            if h == "Literatur":
                items = [inl(x) for x in bl[i + 1:]]
                out.append("\\begin{literatur}\n" + "\n\n".join("\\item " + x for x in items) + "\n\\end{literatur}")
                break
        elif b.startswith("!["):
            nfig += 1
            m = re.match(r"!\[Abbildung \d+: (.+?)\]\(\.\./abbildungen/(.+?)\.png\)", b, re.S)
            text, datei = m.group(1), m.group(2)
            kopf, _, rest = text.partition(". ")
            rest, _, quellen = rest.partition("Quellen: ")
            out.append("\\begin{figure}[tb]\n\\caption{" + inl(kopf) + "}\\label{fig:" + str(nfig) + "}\n"
                       "\\includegraphics[width=\\linewidth]{abbildungen/" + datei + ".pdf}\n"
                       "\\begin{figurenotes}" + inl(rest.strip()) + "\\par\\textit{Quellen:} " + inl(quellen.strip()) + "\\end{figurenotes}\n\\end{figure}")
        elif b.startswith("*Alt-Text"):
            pass
        elif b.startswith("**Tabelle"):
            cap = re.match(r"\*\*Tabelle \d+: (.+)\*\*", b).group(1)
            zeilen = [z.strip().strip("|").split("|") for z in bl[i + 1].splitlines() if not z.startswith("|---")]
            notes = bl[i + 2].replace("Anmerkungen: ", ""); quellen = bl[i + 3].replace("Quellen: ", "")
            i += 3
            kopf = zeilen[0]; ncol = len(kopf) - 1
            t = ["\\begin{table}[tb]", "\\caption{" + inl(cap) + "}\\label{tab:1}", "\\small",
                 "\\begin{tabular*}{\\linewidth}{@{\\extracolsep{\\fill}}>{\\raggedright\\arraybackslash}p{4.3cm}" + "c" * ncol + "@{}}", "\\toprule",
                 " & ".join(inl(k.strip()) if j == 0 else "{\\footnotesize\\shortstack{" + inl(k.strip()).replace(") ", ")\\\\ ", 1) + "}}" for j, k in enumerate(kopf)) + " \\\\",
                 "\\midrule"]
            for z in zeilen[1:]:
                werte = [x.strip() for x in z]
                if werte[0] in ("Beobachtungen",):
                    t.append("\\midrule")
                oben = [inl(werte[0])] + [inl(re.sub(r"\s*\(.*\)", "", w)).replace("-", "$-$") if re.match(r"-?\d", w) else inl(w) for w in werte[1:]]
                t.append(" & ".join(oben) + " \\\\")
                ps = [re.search(r"\((.*)\)", w).group(1) if re.search(r"\(\d", w) else "" for w in werte[1:]]
                if any(ps):
                    t.append(" & " + " & ".join("{\\footnotesize(" + p + ")}" if p else "" for p in ps) + " \\\\")
            t += ["\\bottomrule", "\\end{tabular*}", "\\begin{tablenotes}" + inl(notes) + "\\par\\textit{Quellen:} " + inl(quellen) + "\\end{tablenotes}", "\\end{table}"]
            out.append("\n".join(t))
        else:
            out.append(inl(b))
        i += 1
    tex = PRAEAMBEL.replace("@TITEL@", titel).replace("@UNTER@", unter).replace("@DATUM@", datum) \
        .replace("@ABSTRACT@", abstract).replace("@JEL@", jel) + "\n\n".join(out) + "\n\n\\end{document}\n"
    tex = tex.replace("$R^2$", "R²").replace("R²", "$R^2$")
    open(os.path.join(HIER, "..", "latex", "preisrede.tex"), "w", encoding="utf-8").write(tex)
    print("geschrieben")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
