"""Arandela tartaruga: the oval outdoor bulkhead light with a cast grille over an opal diffuser (walls, porches, garages).

Wall device (wall light): the wall is y = 0, the front -Y, the base z = 0 (ConstructCraft puts it at 2,10 m).
"""

from kit import *
import louca
import _luminarias as lu


def build():
    c = Component("Arandela tartaruga", "lighting", "arandela-tartaruga", "Lighting")
    W = c.param("Largura", 0.24)
    H = c.param("Altura", 0.16)
    c.mep = {"Device": {"device": "WallLight", "power": 12}}
    lu.materiais(c)
    desc = "Arandela tartaruga de alumínio fundido com grade e difusor opalino, LED 12 W, IP65, para áreas externas"
    c.type("Arandela tartaruga oval", desc)
    c.type("Arandela tartaruga grande", desc, Largura=0.3, Altura=0.2)
    s = 0.06
    c.preview_size = (s, s, s)
    c.preview_base = lu.PAREDE + 0.08 - s / 2

    zc = f"{H}/2"
    c.box("Arandela simplificada", f"-{W}/2", -0.08, 0, W, 0.08, H, "Aço pintado preto", detail=COARSE, in_plan=True)
    # Base: an oval frame against the wall; the diffuser a dome inside it; the grille: three bars and an oval ring.
    oval = louca.oval(0, zc, f"{W}/2", f"{H}/2", n=32)
    c.profile("Base", "Front", oval, -0.03, 0.03, "Aço pintado preto", in_plan=True)
    inner = louca.oval(0, zc, f"{W}/2 - 0.014", f"{H}/2 - 0.014", n=32)
    c.profile("Difusor", "Front", inner, -0.07, 0.04, lu.DIFUSOR)
    c.box("Grade - barra horizontal", f"-{W}/2 + 0.02", -0.076, f"{zc} - 0.005", f"{W} - 0.04", 0.008, 0.01, "Aço pintado preto")
    for k, x in enumerate((-0.28, 0.0, 0.28)):
        half = f"{(1 - (2 * x) ** 2) ** 0.5:.4f}*({H}/2 - 0.018)"  # inside the oval at that x
        c.box(f"Grade - barra vertical {k + 1}", f"{x}*{W} - 0.005", -0.076, f"{zc} - {half}", 0.01, 0.008, f"2*{half}", "Aço pintado preto")
    for k in range(4):
        c.cyl_y(f"Parafuso {k + 1}", f"{(-1, 1, -1, 1)[k]}*{W}*0.38", f"{zc} + {(-1, -1, 1, 1)[k]}*{H}*0.3", -0.032, 0.004, 0.003,
                "Inox escovado", detail=FINE)
    return c
