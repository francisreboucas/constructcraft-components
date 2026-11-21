"""Abrigo de gás: a ventilated concrete shelter for two LPG cylinders with their regulator and manifold (NBR 13523).

On the ground, the back at y = 0 (against a wall or the boundary), the louvred doors towards -Y.
"""

from kit import *


def build():
    c = Component("Abrigo de gás", "plumbing", "abrigo-gas", "Plumbing")
    W = c.param("Largura", 0.9)
    D = c.param("Profundidade", 0.45)
    H = c.param("Altura", 0.85)
    B = c.param("DiametroBotijao", 0.36)
    HB = c.param("AlturaBotijao", 0.46)
    A = c.angle("AnguloPorta", 0, open_at=100)
    desc = "Abrigo de concreto ventilado para dois botijões de GLP com regulador, coletor e válvula de bloqueio (NBR 13523)"
    c.type("Abrigo de gás 2 x P13", desc + "; botijões de 13 kg")
    c.type("Abrigo de gás 2 x P45", desc + "; cilindros de 45 kg", Largura=1.1, Profundidade=0.55, Altura=1.55, DiametroBotijao=0.37,
           AlturaBotijao=1.27)
    c.material("Botijão de GLP", (40, 96, 168), "Paint", "Glossy")
    c.preview_size = (1.0, 0.6, 0.95)

    t = 0.05
    c.box("Abrigo simplificado", f"-{W}/2", f"-{D}", 0, W, D, H, "Concreto", detail=COARSE, in_plan=True)
    c.box("Fundo", f"-{W}/2", f"-{t}", 0, W, t, H, "Concreto")
    c.box("Lateral esquerda", f"-{W}/2", f"-{D}", 0, t, f"{D} - {t}", H, "Concreto", in_plan=True)
    c.box("Lateral direita", f"{W}/2 - {t}", f"-{D}", 0, t, f"{D} - {t}", H, "Concreto", in_plan=True)
    c.box("Laje de cobertura", f"-{W}/2 - 0.03", f"-{D} - 0.04", H, f"{W} + 0.06", f"{D} + 0.04", 0.05, "Concreto")
    c.box("Piso", f"-{W}/2 + {t}", f"-{D}", 0, f"{W} - {2 * t}", f"{D} - {t}", 0.05, "Concreto")
    # Two louvred steel doors.
    dw = f"({W}/2 - {t})"
    for side, hx in (("left", f"-{W}/2 + {t}"), ("right", f"{W}/2 - {t}")):
        nm = "esquerda" if side == "left" else "direita"
        hinge = (hx, f"-{D}")
        c.door_box(f"Porta {nm}", hinge, A, 0.002, f"{dw} - 0.004", 0, 0.004, 0.06, f"{H} - 0.08", "Aço pintado cinza", side=side)
        for k in range(6):
            zl = f"0.12 + {k}*({H} - 0.3)/5"
            c.door_box(f"Porta {nm} - veneziana {k + 1}", hinge, A, 0.04, f"{dw} - 0.04", 0.004, 0.016, zl, 0.012, "Aço pintado cinza",
                       side=side, detail=FINE)
    # Cylinders: a turned body, collar and valve.
    for k, s in enumerate((-1, 1)):
        x = f"{s}*{W}/4"
        y = f"-{D}/2"
        r = f"{B}/2"
        pts = [(x, 0.05), (f"{x} + {r}*0.85", 0.05), (f"{x} + {r}", 0.09), (f"{x} + {r}", f"0.05 + {HB}*0.8"),
               (f"{x} + {r}*0.55", f"0.05 + {HB}*0.92"), (x, f"0.05 + {HB}*0.92")]
        c.rev(f"Botijão {k + 1}", "Front", pts, y, x, "Botijão de GLP", in_plan=True)
        c.rev(f"Alça do botijão {k + 1}", "Front", [(f"{x} + {r}*0.42", f"0.05 + {HB}*0.9"), (f"{x} + {r}*0.5", f"0.05 + {HB}*0.9"),
                                                   (f"{x} + {r}*0.5", f"0.05 + {HB}"), (f"{x} + {r}*0.42", f"0.05 + {HB}")], y, x,
              "Botijão de GLP", detail=FINE)
        c.cyl(f"Válvula do botijão {k + 1}", x, y, f"0.05 + {HB}*0.92", 0.016, 0.04, "Latão")
        c.cyl(f"Mangueira {k + 1}", x, y, f"0.05 + {HB}*0.92 + 0.04", 0.006, f"{H} - 0.15 - (0.05 + {HB}*0.92 + 0.04)", "Borracha")
    # Manifold and regulator high on the back, the outlet through the back wall.
    zc = f"{H} - 0.15"
    c.cyl_x("Coletor", f"-{D}/2", zc, f"-{W}/4", 0.012, f"{W}/2", "Cobre")
    c.cyl("Regulador", f"{W}/4 + 0.08", f"-{D}/2", f"{zc} - 0.04", 0.035, 0.07, "Aço pintado preto")
    c.cyl_y("Saída para a rede", f"{W}/4 + 0.08", zc, f"-{D}/2", 0.011, f"{D}/2", "Cobre")
    c.cyl_y("Válvula de bloqueio", f"{W}/4 + 0.08", zc, f"-{D}/4 - 0.03", 0.02, 0.06, "Latão", detail=FINE)
    return c
