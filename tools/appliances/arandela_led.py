"""Arandela LED de facho duplo (para cima e para baixo): corpo de alumínio fundido com a frente arredondada,
difusores leitosos rebaixados no topo e na base, base de fixação na parede, frisos dissipadores e parafusos de travamento.

Dispositivo de parede: a parede em y = 0, a frente em -y, a base em z = 0 (o ConstructCraft
aplica a altura de montagem, 2,10 m nas arandelas), centrada em x = 0.
"""

from kit import *
import _luminarias as lu


def build():
    c = Component("Arandela LED", "lighting", "arandela-led", "Lighting")
    L = c.param("Largura", 0.12)
    A = c.param("Altura", 0.12)
    P = c.param("Profundidade", 0.08)
    c.mep = {"Device": {"device": "WallLight", "power": 20}}
    lu.materiais(c)
    c.type("Arandela LED 20 VA", "Arandela de parede interna")
    c.type("Arandela externa LED 20 VA", "Arandela de parede, IP65", Largura=0.15, Altura=0.2, Profundidade=0.1)
    # make.py coloca a arandela a 2,10 m; câmeras de perto, apontadas para o meio do corpo
    s = 0.05
    c.preview_size = (s, s, s)
    c.preview_base = lu.PAREDE + 0.07 - s / 2

    hl = f"({L}/2)"
    tb = 0.003  # base de fixação: o corpo fica afastado da parede por ela
    r = f"(0.18*{P})"  # raio dos cantos da frente
    pw = 0.005  # parede do corpo em volta dos difusores
    AL = "Alumínio fundido"

    def contorno(g):
        """Contorno em planta do corpo, recuado g (a parede de trás fica em y = -tb - g)."""
        rg = f"({r} - {g})"
        return [(f"-{hl} + {r}", f"-{P} + {g}"), (f"{hl} - {r}", f"-{P} + {g}", rg), (f"{hl} - {g}", f"-{P} + {r}"),
                (f"{hl} - {g}", -tb - g), (f"-{hl} + {g}", -tb - g), (f"-{hl} + {g}", f"-{P} + {r}", rg)]

    # --- simplificado ---------------------------------------------------------------------
    c.box("Volume simplificado", f"-{hl}", f"-{P}", 0, L, P, A, AL, detail=COARSE, in_plan=True)

    # --- base de fixação e vedação ------------------------------------------------------------
    c.box("Base de fixação", f"-{hl} + 0.008", -tb, 0.008, f"{L} - 0.016", tb, f"{A} - 0.016", "Aço galvanizado")
    c.box("Junta de vedação", f"-{hl} + 0.006", -tb - 0.0004, 0.006, f"{L} - 0.012", 0.0004, f"{A} - 0.012", "Borracha", detail=FINE)

    # --- corpo: bloco central e colares em volta dos difusores (em cima e embaixo) -------------------
    rb = 0.006  # profundidade dos rebaixos acima dos difusores
    td = 0.003  # espessura dos difusores
    hc = rb + td  # altura dos colares
    c.profile("Corpo", "Plan", contorno(0), hc, f"{A} - {2 * hc}", AL, in_plan=True)
    rp = f"({r} - {pw})"
    colar = [(f"-{hl}", -tb), (f"-{hl}", f"-{P} + {r}", r), (f"-{hl} + {r}", f"-{P}"), (f"{hl} - {r}", f"-{P}", r), (hl, f"-{P} + {r}"),
             (hl, -tb), (f"{hl} - {pw}", -tb), (f"{hl} - {pw}", f"-{P} + {r}", f"-{rp}"), (f"{hl} - {r}", f"-{P} + {pw}"),
             (f"-{hl} + {r}", f"-{P} + {pw}", f"-{rp}"), (f"-{hl} + {pw}", f"-{P} + {r}"), (f"-{hl} + {pw}", -tb)]
    for nome, z in (("superior", f"{A} - {hc}"), ("inferior", 0)):
        c.profile(f"Colar {nome}", "Plan", colar, z, hc, AL)
        c.box(f"Colar {nome} - fundo", f"-{hl} + {pw}", -tb - pw, z, f"{L} - {2 * pw}", pw, hc, AL)

    # --- difusores leitosos rebaixados nos colares --------------------------------------------------
    c.profile("Difusor superior", "Plan", contorno(pw), f"{A} - {hc}", td, lu.DIFUSOR)
    c.profile("Difusor inferior", "Plan", contorno(pw), rb, td, lu.DIFUSOR)

    # --- frisos: um na frente, dissipadores nas laterais (sulcos) -------------------------------------
    c.box("Friso frontal", f"-{hl} + {r}", f"-{P} - 0.001", f"{A}/2 - 0.0012", f"{L} - 2*{r}", 0.0025, 0.0024, AL, detail=FINE, void=True)
    for i, sx in enumerate((-1, 1), 1):
        for k in range(5):
            f = 0.3 + 0.1 * k
            c.box(f"Aleta lateral {i}.{k + 1}", f"{sx}*{hl} - 0.0015", f"-{P} + {r} + 0.004", f"{f:.2f}*{A} - 0.001", 0.003,
                  f"{P} - {r} - {tb} - 0.012", 0.002, AL, detail=FINE, void=True)

    # --- parafusos de travamento do corpo na base, por baixo ---------------------------------------
    for i, sx in enumerate((-1, 1), 1):
        c.cyl(f"Parafuso de travamento {i}", f"{sx}*0.3*{L}", -tb - 0.0025, -0.0008, 0.0018, 0.0012, "Inox escovado", detail=FINE)
    return c
