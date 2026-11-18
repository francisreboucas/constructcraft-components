"""Mesa redonda: bullnosed top on a turned pedestal with four saber feet."""

from kit import *


def turned(c, name, cx, cy, profile, material, detail=FULL, in_plan=False):
    """A turned piece about the vertical axis at (cx, cy): profile = [(radius, z), …] from bottom to top."""
    pts = [(cx, profile[0][1])] + [(f"{p(cx)} + {p(r)}", z) for r, z in profile] + [(cx, profile[-1][1])]
    c.rev(name, "Front", pts, cy, cx, material, detail=detail, in_plan=in_plan)


def mirrored(pts):
    """The outline mirrored in u (u -> -u), kept counter-clockwise with each arc on its own segment."""
    n = len(pts)
    out = []
    for j in range(n):
        u, v = pts[n - 1 - j][0], pts[n - 1 - j][1]
        prev = pts[(n - 2 - j) % n]
        radius = prev[2] if len(prev) > 2 else None
        out.append((f"-({e(u)})", v, radius))
    return out


def build():
    c = Component("Mesa redonda", "furniture", "mesa-redonda")
    Dm = c.param("Diametro", 1.0)
    H = c.param("Altura", 0.75)
    c.type("Mesa redonda Ø90", "Mesa redonda, 4 lugares", Diametro=0.9)
    c.type("Mesa redonda Ø120", "Mesa redonda, 6 lugares", Diametro=1.2)
    c.material("Feltro", (70, 66, 60), "Generic", "Matte")

    wood, dark = "Madeira", "Madeira escura"
    R = f"{Dm}/2"

    # Coarse stand-ins: the old cylinders.
    c.cyl("Tampo simplificado", 0, 0, f"{H} - 0.03", R, 0.03, wood, detail=COARSE, in_plan=True)
    c.cyl("Coluna simplificada", 0, 0, 0.03, 0.05, f"{H} - 0.06", wood, detail=COARSE)
    c.cyl("Base simplificada", 0, 0, 0, f"{Dm}/4", 0.03, wood, detail=COARSE)

    # Top with a rounded edge and a chamfered underside.
    c.cyl("Tampo", 0, 0, f"{H} - 0.03", f"{R} - 0.02", 0.03, wood)
    c.rev("Borda do tampo", "Front", [(f"{R} - 0.02", f"{H} - 0.03"), (f"{R} - 0.016", f"{H} - 0.03"), (f"{R} - 0.003", f"{H} - 0.017"),
                                      (R, f"{H} - 0.01"), (f"{R} - 0.0015", f"{H} - 0.003"), (f"{R} - 0.006", H), (f"{R} - 0.02", H)],
          0, 0, wood, in_plan=True)
    c.cyl("Filete do tampo", 0, 0, f"{H} - 0.0305", f"{R} - 0.03", 0.001, dark, detail=FINE)
    # Spider under the top: a plate and four tapered arms.
    zu = f"{H} - 0.03"
    arm = f"0.36*{Dm}"
    c.cyl("Chapa de fixação", 0, 0, f"{zu} - 0.012", f"0.11*{Dm}", 0.012, dark)
    pts = [(f"-({arm})", f"{zu} - 0.018"), ("-0.07", f"{zu} - 0.05"), ("0.07", f"{zu} - 0.05"), (arm, f"{zu} - 0.018"), (arm, zu),
           (f"-({arm})", zu)]
    c.profile("Braço do tampo longitudinal", "Front", pts, -0.022, 0.044, wood)
    c.profile("Braço do tampo transversal", "Side", pts, -0.022, 0.044, wood)
    n = 0
    for ax in ("x", "y"):
        for s in (-1, 1):
            for f in (0.5, 0.92):
                n += 1
                x, y = (f"{s}*{f}*{arm}", 0) if ax == "x" else (0, f"{s}*{f}*{arm}")
                c.cyl(f"Parafuso do braço {n}", x, y, f"{zu} - 0.0215 - {0.032 * (1 - f) / 0.93:.4f}", 0.004, 0.003, "Aço galvanizado",
                      detail=FINE)

    # Turned column.
    z0 = 0.21
    z1 = f"{zu} - 0.05"
    h = f"({z1} - {z0})"
    c.rev("Coluna", "Front", [(0, z0)] + [(r, z) for r, z in [
        (0.05, z0), (0.05, z0 + 0.02), (0.041, z0 + 0.035), (0.046, f"{z0} + 0.08*{h}"), (0.074, f"{z0} + 0.22*{h}"),
        (0.076, f"{z0} + 0.27*{h}"), (0.068, f"{z0} + 0.34*{h}"), (0.04, f"{z0} + 0.62*{h}"), (0.034, f"{z0} + 0.8*{h}"),
        (0.047, f"{z0} + 0.85*{h}"), (0.047, f"{z0} + 0.88*{h}"), (0.036, f"{z0} + 0.91*{h}"), (0.058, f"{z1} - 0.012"),
        (0.058, z1)]] + [(0, z1)], 0, 0, wood)
    c.rev("Anel da coluna", "Front", [(0.04, z0 + 0.03), (0.047, z0 + 0.03), (0.047, z0 + 0.04), (0.04, z0 + 0.04)], 0, 0, dark,
          detail=FINE)
    # Hub the feet join.
    c.cyl("Cubo da base", 0, 0, 0.1, 0.055, 0.11, wood)
    turned(c, "Pingente da base", 0, 0, [(0.012, 0.062), (0.024, 0.07), (0.026, 0.082), (0.04, 0.1)], wood, detail=FINE)

    # Saber feet: concave arcs above and below.
    Rf = f"0.31*{Dm}"
    under = f"1.6*sqrt(({Rf} - 0.085)*({Rf} - 0.085) + 0.0081)"
    over = f"1.1*sqrt(({Rf} - 0.03)*({Rf} - 0.03) + 0.0256)"
    foot = [("0.03", 0.105, f"-({under})"), (f"{Rf} - 0.055", 0.015), (Rf, 0.015), (Rf, 0.045, f"-({over})"), ("0.03", 0.205)]
    c.profile("Pé direito", "Front", foot, -0.021, 0.042, wood)
    c.profile("Pé esquerdo", "Front", mirrored(foot), -0.021, 0.042, wood)
    c.profile("Pé traseiro", "Side", foot, -0.021, 0.042, wood)
    c.profile("Pé frontal", "Side", mirrored(foot), -0.021, 0.042, wood)
    for name, (sx, sy) in {"direito": (1, 0), "esquerdo": (-1, 0), "traseiro": (0, 1), "frontal": (0, -1)}.items():
        x, y = f"{sx}*({Rf} - 0.028)", f"{sy}*({Rf} - 0.028)"
        c.cyl(f"Sapata do pé {name}", x, y, 0.003, 0.016, 0.012, "Latão", detail=FINE)
        c.cyl(f"Feltro do pé {name}", x, y, 0, 0.013, 0.003, "Feltro", detail=FINE)
    return c
