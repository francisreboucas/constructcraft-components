"""Shared pieces of the office furniture: materials and the steel T-leg of desks and tables.

Not a component module: make.py skips the files whose name starts with `_`.
"""

from __future__ import annotations

from kit import FINE, FULL, p

# Materials of the office furniture (the same name means the same material in every component).
OFFICE = {
    "Melamina carvalho": ((184, 150, 110), "Wood", "Satin", 0),
    "Melamina grafite": ((72, 74, 78), "Wood", "Satin", 0),
    "Aço pintado cinza claro": ((196, 198, 196), "Paint", "Satin", 0),
    "Tecido de divisória": ((74, 86, 102), "Generic", "Matte", 0),
    "Tecido estofado preto": ((38, 38, 42), "Generic", "Matte", 0),
    "Papel kraft": ((176, 140, 92), "Generic", "Matte", 0),
}


def declare(c, *names):
    for n in names:
        c.material(n, *OFFICE[n])


def t_leg(c, tag, xc, y0, y1, zt, steel, foot=0.07, col=(0.04, 0.08)):
    """A steel T-leg at x = xc: a tapered foot along Y on two levelers, a column and a bracket under the top (zt)."""
    lv = 0.01
    fh = 0.045
    c.profile(f"{tag} - pé", "Side", [(y0, lv), (y1, lv), (y1, f"{lv} + 0.018"), (f"{p(y1)} - 0.07", lv + fh), (f"{p(y0)} + 0.07", lv + fh),
                                       (y0, f"{lv} + 0.018")], f"{p(xc)} - {foot / 2}", foot, steel)
    for n, y in enumerate((f"{p(y0)} + 0.03", f"{p(y1)} - 0.03"), 1):
        c.cyl(f"{tag} - sapata {n}", xc, y, 0, 0.016, lv, "Plástico preto", detail=FINE)
    yc = f"({p(y0)} + {p(y1)})/2"
    cx, cy = col
    c.box(f"{tag} - coluna", f"{p(xc)} - {cx / 2}", f"{yc} - {cy / 2}", lv + fh, cx, cy, f"{p(zt)} - 0.03 - {lv + fh}", steel)
    c.box(f"{tag} - capa da coluna", f"{p(xc)} - {cx / 2 + 0.002}", f"{yc} - {cy / 2 + 0.002}", lv + fh, cx + 0.004, cy + 0.004, 0.012,
          "Plástico preto", detail=FINE)
    c.box(f"{tag} - suporte do tampo", f"{p(xc)} - 0.025", f"{p(y0)} + 0.04", f"{p(zt)} - 0.03", 0.05, f"{p(y1)} - {p(y0)} - 0.08", 0.03,
          steel)


def grommet(c, gx, gy, z, detail=FINE):
    """A round cable grommet on a top whose upper face is at z."""
    c.rev("Passa-cabos - aro", "Front", [(f"{p(gx)} + 0.024", z), (f"{p(gx)} + 0.034", z), (f"{p(gx)} + 0.034", f"{p(z)} + 0.002"),
                                          (f"{p(gx)} + 0.031", f"{p(z)} + 0.0035"), (f"{p(gx)} + 0.024", f"{p(z)} + 0.0035")], gy, gx,
          "Plástico preto", detail=detail)
    c.cyl("Passa-cabos - tampa", gx, gy, z, 0.024, 0.002, "Plástico cinza", detail=detail)


def top_side(c, name, xl, w, yf, yb, zu, h, mat, in_plan=True, detail=FULL):
    """A top with a rounded front edge, drawn on the side plane from xl, w wide (zu = underside, h = top face)."""
    r = 0.008
    c.profile(name, "Side", [(f"{p(yf)} + {r}", zu), (yb, zu), (yb, h), (f"{p(yf)} + {r}", h, r), (yf, f"{p(h)} - {r}"),
                             (yf, f"{p(zu)} + {r}", r)], xl, w, mat, in_plan=in_plan, detail=detail)
