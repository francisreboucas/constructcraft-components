"""Shared pieces of the bathroom accessories (papeleira, cabide, dispenser, prateleira): the wall rose.

Not a component module. The wall is y = 0 and the accessory stands out towards -Y; the instance parameter Elevacao is
its mounting height.
"""

from __future__ import annotations

from kit import FULL
from louca import add


def rose(c, name, x, z, r=0.025, depth=0.012, material="Cromado", detail=FULL, in_plan=True):
    """A round wall rose about the axis along Y at (x, z), with a rounded front edge."""
    c.rev(name, "Plan", [(x, -depth), (add(x, r - 0.005), -depth, 0.005), (add(x, r), add(-depth, 0.005)), (add(x, r), 0), (x, 0)], z, x,
          material, detail=detail, in_plan=in_plan)
