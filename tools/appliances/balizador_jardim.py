"""Balizador de jardim: a round aluminium bollard light with a louvred head that throws the light down onto the path.

On the ground, centred on the origin. It carries no device data (the engine would lift a wall light to 2,10 m);
its power is in the description.
"""

from kit import *
import _luminarias as lu


def build():
    c = Component("Balizador de jardim", "lighting", "balizador-jardim", "Lighting")
    H = c.param("Altura", 0.8)
    D = c.param("Diametro", 0.12)
    lu.materiais(c)
    desc = "Balizador de jardim de alumínio pintado com cabeça de aletas que direciona a luz para o chão, LED 10 W, IP65"
    c.type("Balizador de jardim 80 cm", desc)
    c.type("Balizador de jardim 60 cm", desc, Altura=0.6)
    c.type("Balizador de jardim 1,0 m", desc, Altura=1.0, Diametro=0.15)
    c.preview_size = (0.2, 0.2, 0.9)

    r = f"{D}/2"
    head = f"{D}*1.4"  # height of the lamp head
    zh = f"{H} - {head}"
    c.cyl("Balizador simplificado", 0, 0, 0, r, H, "Aço pintado preto", detail=COARSE, in_plan=True)
    c.cyl("Base de fixação", 0, 0, 0, f"{r} + 0.03", 0.008, "Aço pintado preto")
    c.cyl("Corpo", 0, 0, 0.008, r, f"{zh} - 0.008", "Aço pintado preto", in_plan=True)
    # The head: a diffuser behind four rings of louvres, under a domed cap.
    c.cyl("Difusor", 0, 0, zh, f"{r} - 0.008", head, lu.DIFUSOR)
    for k in range(4):
        z = f"{zh} + ({k} + 0.35)*{head}/4"
        c.rev(f"Aleta {k + 1}", "Front", [(f"{r} - 0.012", z), (f"{r} + 0.004", f"{z} - 0.012"), (f"{r} + 0.004", f"{z} - 0.008"),
                                          (f"{r} - 0.012", f"{z} + 0.004")], 0, 0, "Aço pintado preto")
    for k in range(3):
        c.box(f"Haste da cabeça {k + 1}", f"{r}*0.92*cos({120 * k + 30}) - 0.003", f"{r}*0.92*sin({120 * k + 30}) - 0.003", zh, 0.006, 0.006,
              head, "Aço pintado preto", detail=FINE)
    c.rev("Tampa", "Front", [(0, H), (f"{r} + 0.006", H), (f"{r} + 0.006", f"{H} + 0.006"), (f"{r}*0.6", f"{H} + 0.016", 0.06), (0, f"{H} + 0.02")],
          0, 0, "Aço pintado preto")
    c.cyl("LED", 0, 0, f"{H} - 0.012", f"{r}*0.5", 0.004, lu.LED, detail=FINE)
    for k in range(3):
        c.cyl(f"Parafuso da base {k + 1}", f"({r} + 0.018)*cos({120 * k})", f"({r} + 0.018)*sin({120 * k})", 0.008, 0.005, 0.004,
              "Inox escovado", detail=FINE)
    return c
