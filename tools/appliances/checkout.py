"""Caixa de supermercado (checkout): a stainless counter with a feed conveyor, a scanner, the POS terminal and a
cashier's seat, and a bagging table. The customer's lane is at -Y; the belt runs towards +X.
"""

from kit import *


def build():
    c = Component("Caixa de supermercado", "furniture", "checkout")
    L = c.param("Comprimento", 2.4)
    c.type("Caixa de supermercado 2,4 m", "Checkout de supermercado com esteira de alimentação, leitor de código de barras, "
           "terminal de vendas, gaveta de dinheiro, banco do operador e mesa de empacotamento")
    c.type("Caixa de supermercado 3,0 m", "Checkout com esteira mais longa", Comprimento=3.0)
    c.material("Esteira", (30, 30, 32), "Plastic", "Matte")
    c.preview_size = (3.0, 1.2, 1.4)

    xl = f"-{L}/2"
    d = 0.8
    h = 0.85
    c.box("Caixa simplificado", xl, -d / 2, 0, L, d, h, "Inox escovado", detail=COARSE, in_plan=True)
    # Counter body and top, the belt along the customer side.
    c.box("Corpo", f"{xl} + 0.02", -d / 2 + 0.03, 0.08, f"{L} - 0.04", d - 0.06, h - 0.12, "Aço pintado cinza")
    c.box("Rodapé", f"{xl} + 0.05", -d / 2 + 0.06, 0, f"{L} - 0.1", d - 0.12, 0.08, "Aço pintado preto")
    c.box("Tampo", xl, -d / 2, h - 0.04, L, d, 0.04, "Inox escovado", in_plan=True)
    c.box("Esteira", xl, -d / 2 + 0.03, h, f"{L}*0.55", 0.42, 0.01, "Esteira")
    c.box("Guia da esteira", xl, -d / 2, h, f"{L}*0.55", 0.03, 0.05, "Inox escovado")
    c.box("Separador de compras", f"{xl} + 0.4", -d / 2 + 0.1, h + 0.01, 0.3, 0.04, 0.04, "Plástico azul", detail=FINE)
    # Scanner, scale and POS.
    xs = f"{xl} + {L}*0.6"
    c.box("Balança e leitor", xs, -d / 2 + 0.05, h - 0.005, 0.38, 0.38, 0.015, "Vidro fumê")
    c.box("Leitor vertical", xs, -d / 2 + 0.38, h, 0.38, 0.06, 0.18, "Plástico preto")
    c.box("Terminal - base", f"{xs} + 0.45", 0.05, h, 0.12, 0.12, 0.25, "Plástico preto")
    c.box("Terminal - tela", f"{xs} + 0.4", 0.02, h + 0.25, 0.3, 0.03, 0.22, "Tela de TV")
    c.box("Visor do cliente", f"{xs} + 0.45", -d / 2 + 0.1, h, 0.1, 0.03, 0.3, "Visor LED")
    c.box("Teclado", f"{xs} + 0.42", 0.2, h, 0.3, 0.12, 0.03, "Teclado", detail=FINE)
    c.box("Gaveta de dinheiro", f"{xs} + 0.4", d / 2 - 0.02, h - 0.2, 0.4, 0.04, 0.12, "Aço pintado preto")
    # Bagging table at the end, lower.
    c.box("Mesa de empacotamento", f"{L}/2 - 0.02", -d / 2, 0.75, 0.7, d, 0.03, "Inox escovado", in_plan=True)
    for k, (x, y) in enumerate(((0.05, -d / 2 + 0.05), (0.63, -d / 2 + 0.05), (0.05, d / 2 - 0.08), (0.63, d / 2 - 0.08))):
        c.box(f"Pé da mesa {k + 1}", f"{L}/2 + {x - 0.02}", y, 0, 0.03, 0.03, 0.75, "Inox escovado")
    # Cashier's seat behind the counter.
    c.cyl("Banco - base", f"{xs} + 0.55", d / 2 + 0.45, 0, 0.22, 0.03, "Aço pintado preto")
    c.cyl("Banco - coluna", f"{xs} + 0.55", d / 2 + 0.45, 0.03, 0.025, 0.6, "Cromado")
    c.cyl("Banco - assento", f"{xs} + 0.55", d / 2 + 0.45, 0.63, 0.2, 0.06, "Plástico preto")
    return c
