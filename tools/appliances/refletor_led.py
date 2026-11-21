"""Refletor LED: a wall floodlight with a finned die-cast body and glass front, on a yoke aimed down.

Wall device (wall light): the wall is y = 0, the front -Y, the base z = 0 at the yoke (ConstructCraft puts wall lights
at 2,10 m; raise it for a façade or a court).
"""

from kit import *
import _luminarias as lu


def build():
    c = Component("Refletor LED", "lighting", "refletor-led", "Lighting")
    W = c.param("Largura", 0.24)
    H = c.param("Altura", 0.19)
    A = c.param("Inclinacao", 25, "Angle")
    c.mep = {"Device": {"device": "WallLight", "power": 50}}
    lu.materiais(c)
    desc = "Refletor LED de alumínio injetado com vidro temperado e alça articulada, IP66, para fachadas, muros e quintais"
    c.type("Refletor LED 50 W", desc)
    c.type("Refletor LED 100 W", desc, Largura=0.3, Altura=0.24)
    c.type("Refletor LED 200 W", desc, Largura=0.38, Altura=0.3)
    s = 0.15
    c.preview_size = (s * 2, s * 2, s * 2)
    c.preview_base = lu.PAREDE - 0.1

    d = 0.045  # body depth
    zp = 0.0  # pivot height
    yp = -0.09  # pivot out from the wall
    ca, sa = f"cos({A})", f"sin({A})"

    def pt(u, v):  # (y, z) of the point u out (towards the front of the body) and v up the body's face, about the pivot
        return (f"{yp} - ({u})*{ca} - ({v})*{sa}", f"{zp} - ({u})*{sa} + ({v})*{ca}")

    def slab(name, u0, u1, v0, v1, x, w, mat, **kw):
        c.profile(name, "Side", [pt(u0, v0), pt(u0, v1), pt(u1, v1), pt(u1, v0)], x, w, mat, **kw)

    xl = f"-{W}/2"
    c.box("Refletor simplificado", xl, f"{yp} - {d} - 0.02", f"-{H}/2", W, f"{d} + 0.1", H, "Aço pintado preto", detail=COARSE, in_plan=True)
    # Yoke: a wall plate and a U arm round the body.
    c.box("Placa da alça", -0.03, -0.006, -0.04, 0.06, 0.006, 0.08, "Aço pintado preto")
    c.box("Alça - braço", -0.012, yp, -0.012, 0.024, -yp - 0.006, 0.024, "Aço pintado preto")
    for side, x in (("esquerda", f"{xl} - 0.012"), ("direita", f"{W}/2 + 0.004")):
        c.cyl_x(f"Pivô {side}", yp, zp, x, 0.012, 0.008, "Aço pintado preto")
        c.box(f"Alça - lateral {side}", x, f"{yp} - 0.006", -0.01, 0.008, -yp * 0.1, 0.02, "Aço pintado preto", detail=FINE)
    # Body: the finned back, the frame, the glass and the LED board.
    slab("Corpo", -0.02, f"{d} - 0.02", f"-{H}/2", f"{H}/2", xl, W, "Aço pintado preto", in_plan=True)
    for k in range(7):
        v = f"-{H}/2 + ({k} + 0.5)*{H}/7"
        slab(f"Aleta {k + 1}", -0.035, -0.02, f"{v} - 0.003", f"{v} + 0.003", f"{xl} + 0.01", f"{W} - 0.02", "Aço pintado preto", detail=FINE)
    slab("Vidro", f"{d} - 0.02", f"{d} - 0.016", f"-{H}/2 + 0.012", f"{H}/2 - 0.012", f"{xl} + 0.012", f"{W} - 0.024", lu.DIFUSOR)
    slab("Placa de LEDs", f"{d} - 0.026", f"{d} - 0.022", f"-{H}/2 + 0.03", f"{H}/2 - 0.03", f"{xl} + 0.03", f"{W} - 0.06", lu.LED,
         detail=FINE)
    c.cyl("Prensa-cabo", f"{W}/4", yp, f"-{H}/2 - 0.015", 0.008, 0.015, "Plástico preto", detail=FINE)
    return c
