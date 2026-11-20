"""Arquivo de aço: a four-drawer steel filing cabinet for hanging folders, with label holders, handles and a central lock."""

from kit import *
from _escritorio import declare


def build():
    c = Component("Arquivo de aço", "furniture", "arquivo-aco")
    W = c.param("Largura", 0.47)
    D = c.param("Profundidade", 0.71)
    H = c.param("Altura", 1.33)
    a = [c.param(f"AberturaGaveta{k}", 0, "Length", True) for k in range(1, 5)]
    c.open_pose.update({a[0]: 0.5, a[2]: 0.25})
    desc = ("Arquivo de aço com quatro gavetas para pastas suspensas em corrediças telescópicas, porta-etiquetas, puxadores e "
            "fechadura central que trava todas as gavetas")
    c.type("Arquivo de aço 4 gavetas", desc)
    c.type("Arquivo de aço 4 gavetas ofício", desc + "; para pastas tamanho ofício", Largura=0.5)
    declare(c, "Aço pintado cinza claro", "Papel kraft")

    steel = "Aço pintado cinza claro"
    t = 0.008  # the sheet, drawn thicker than it is
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{D}/2", f"{D}/2"
    zp = 0.06  # plinth

    c.box("Arquivo simplificado", xl, yf, 0, W, D, H, steel, detail=COARSE, in_plan=True)

    # Carcass: a recessed plinth, sides, top with a folded front edge, back.
    c.box("Rodapé", f"{xl} + 0.02", f"{yf} + 0.03", 0, f"{W} - 0.04", f"{D} - 0.04", zp, "Aço pintado cinza")
    c.box("Lateral esquerda", xl, yf, 0.004, t, D, f"{H} - 0.004", steel)
    c.box("Lateral direita", f"{xr} - {t}", yf, 0.004, t, D, f"{H} - 0.004", steel)
    c.box("Tampo", f"{xl} + {t}", yf, f"{H} - {t}", f"{W} - {2 * t}", D, t, steel, in_plan=True)
    c.box("Fundo", f"{xl} + {t}", f"{yb} - {t}", zp, f"{W} - {2 * t}", t, f"{H} - {zp} - {t}", steel)
    c.box("Base", f"{xl} + {t}", yf, zp, f"{W} - {2 * t}", D, t, steel)
    c.box("Trava das gavetas", f"{xl} + {t}", yf, f"{H} - {t} - 0.02", f"{W} - {2 * t}", 0.02, 0.02, steel)
    c.cyl_y("Fechadura - cilindro", 0, f"{H} - {t} - 0.01", f"{yf} - 0.006", 0.011, 0.006, "Cromado", detail=FINE)
    c.box("Fechadura - fenda", -0.001, f"{yf} - 0.0065", f"{H} - {t} - 0.017", 0.002, 0.001, 0.014, "Plástico preto", detail=FINE)

    # Four drawers of equal height between the base and the lock rail.
    z0 = f"{zp} + {t}"
    z1 = f"{H} - {t} - 0.02"
    hd = f"({z1} - {p(z0)})/4"
    g = 0.003
    for k in range(4):
        n, o = k + 1, a[k]
        zb, zt = f"{p(z0)} + {3 - k}*{hd} + {g}", f"{p(z0)} + {4 - k}*{hd} - {g}"  # drawer 1 at the top
        y = f"{yf} - {o}"
        tag = f"Gaveta {n}"
        c.box(f"{tag} - frente", f"{xl} + {t} + {g}", f"{y} - 0.02", zb, f"{W} - {2 * t} - {2 * g}", 0.02, f"{zt} - ({zb})", steel)
        # Body: sides, bottom and back that slide out with the front.
        c.box(f"{tag} - lateral esquerda", f"{xl} + {t} + 0.02", y, f"{zb} + 0.02", 0.006, f"{D} - 0.04", f"{hd} - 0.06", steel,
              detail=FINE)
        c.box(f"{tag} - lateral direita", f"{xr} - {t} - 0.026", y, f"{zb} + 0.02", 0.006, f"{D} - 0.04", f"{hd} - 0.06", steel,
              detail=FINE)
        c.box(f"{tag} - fundo", f"{xl} + {t} + 0.026", y, f"{zb} + 0.02", f"{W} - {2 * t} - 0.052", f"{D} - 0.04", 0.006, steel,
              detail=FINE)
        c.box(f"{tag} - traseira", f"{xl} + {t} + 0.026", f"{y} + {D} - 0.046", f"{zb} + 0.02", f"{W} - {2 * t} - 0.052", 0.006,
              f"{hd} - 0.06", steel, detail=FINE)
        # Handle: a pull bar on two posts under a label holder.
        zh = f"{zb} + 0.62*({zt} - ({zb}))"
        c.box(f"{tag} - puxador", "-0.07", f"{y} - 0.05", f"{zh} - 0.012", 0.14, 0.014, 0.024, "Cromado")
        for side, x in (("esquerdo", -0.066), ("direito", 0.056)):
            c.box(f"{tag} - pé do puxador {side}", x, f"{y} - 0.036", f"{zh} - 0.008", 0.01, 0.016, 0.016, "Cromado", detail=FINE)
        c.box(f"{tag} - porta-etiqueta", "-0.045", f"{y} - 0.024", f"{zh} + 0.03", 0.09, 0.004, 0.032, "Cromado", detail=FINE)
        c.box(f"{tag} - etiqueta", "-0.04", f"{y} - 0.0245", f"{zh} + 0.034", 0.08, 0.001, 0.024, "Branco", detail=FINE)
        # Hanging folders in the drawer.
        for m in range(6):
            yy = f"{y} + 0.05 + {m}*({D} - 0.16)/5"
            c.box(f"{tag} - pasta {m + 1}", f"{xl} + {t} + 0.035", yy, f"{zb} + 0.03", f"{W} - {2 * t} - 0.07", 0.004, f"{hd} - 0.1",
                  "Papel kraft", detail=FINE)
    return c
