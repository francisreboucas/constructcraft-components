-- The geometry(p) functions of the floor markings, one section per component
-- (between "--- <file>" lines). tools/site.py puts each section after the
-- shared code (lib.lua) and the parameter declarations it writes from its own
-- table of parameters.
--
-- Frame: meters, x to the right, y away from the driver (the direction of
-- travel), z up from the floor. Paint is THICK thick, from z = 0.

--- vaga-estacionamento
local THICK = 0.003

function geometry(p)
  local W, L, w = max(p.Largura, 0.3), max(p.Comprimento, 0.3), max(p.LarguraLinha, 0.01)
  local deg = min(max(p.Angulo, 20), 90)
  local s, c = sin(rad(deg)), cos(rad(deg))
  local cot = c / s
  local Wx, wx, Yb = W / s, w / s, L * s -- along the aisle: the spot's width and the lines'
  local mode = p.Demarcacao
  local opts = (p.Pintura ~= "" and p.Pintura) and { material = p.Pintura } or nil
  local out = {}
  -- The lines run along the sides at the angle; their ends are cut parallel to the aisle.
  local y0 = (mode == "retangulo") and -w / 2 or 0
  local y1 = (mode ~= "laterais") and Yb + w / 2 or Yb
  local function side(xc)
    return { { xc - wx / 2 + y0 * cot, y0 }, { xc + wx / 2 + y0 * cot, y0 }, { xc + wx / 2 + y1 * cot, y1 }, { xc - wx / 2 + y1 * cot, y1 } }
  end
  local function across(ya, yb) -- between the inner edges of the side lines
    local xl, xr = -Wx / 2 + wx / 2, Wx / 2 - wx / 2
    return { { xl + ya * cot, ya }, { xr + ya * cot, ya }, { xr + yb * cot, yb }, { xl + yb * cot, yb } }
  end
  add(out, prism(side(-Wx / 2), 0, THICK, opts), prism(side(Wx / 2), 0, THICK, opts))
  if mode ~= "laterais" then add(out, prism(across(Yb - w / 2, Yb + w / 2), 0, THICK, opts)) end
  if mode == "retangulo" then add(out, prism(across(-w / 2, w / 2), 0, THICK, opts)) end

  -- Number at the entry, legend in the middle, reading across the spot.
  local m = new_mesh()
  local room = W - 2 * w - 0.2
  local function at(t) return t * c, t * s end
  local hn, hl = max(p.AlturaNumero, 0.05), max(p.AlturaLegenda, 0.05)
  local start = (mode == "retangulo") and w / 2 + 0.25 or 0.3
  if p.Numero ~= "" then
    local x, y = at(start + hn / 2)
    local o = fit(p.Numero, { x = x, y = y, ang = deg - 90, altura = hn, largura = hn * 0.62, espaco = hn * 0.08, h = THICK }, room)
    text(m, p.Numero, o)
    start = start + hn + 0.3
  end
  if p.Legenda ~= "" then
    local t = max(L / 2, start + hl / 2)
    t = min(t, L - w - 0.2 - hl / 2)
    local x, y = at(t)
    local o = fit(p.Legenda, { x = x, y = y, ang = deg - 90, altura = hl, largura = hl * 0.5, espaco = hl * 0.1, h = THICK }, room)
    text(m, p.Legenda, o)
  end
  add(out, m.piece(opts and { name = "Texto", material = opts.material } or { name = "Texto" }))
  return out
end

--- vaga-pcd
local THICK = 0.003
local BLUE = 0.002 -- the blue square under the symbol (a piece of its own)

function geometry(p)
  local W, L, w, C = max(p.Largura, 0.5), max(p.Comprimento, 1), max(p.LarguraLinha, 0.01), max(p.LarguraCirculacao, 0)
  local S = max(p.LadoSimbolo, 0.2)
  local side = p.Lado
  if C <= w then side = "nenhum" end
  local out = {}
  -- Side lines at these x (centres), from left to right; strips are hatched between some of them.
  local xs, strips = {}, {}
  if side == "esquerda" or side == "ambos" then xs[#xs + 1] = -W / 2 - C; strips[#strips + 1] = { -W / 2 - C, -W / 2 } end
  xs[#xs + 1] = -W / 2
  xs[#xs + 1] = W / 2
  if side == "direita" or side == "ambos" then xs[#xs + 1] = W / 2 + C; strips[#strips + 1] = { W / 2, W / 2 + C } end
  if C <= w then strips = {} end
  for _, x in ipairs(xs) do add(out, rect(x - w / 2, 0, x + w / 2, L + w / 2, 0, THICK)) end
  for i = 1, #xs - 1 do add(out, rect(xs[i] + w / 2, L - w / 2, xs[i + 1] - w / 2, L + w / 2, 0, THICK)) end
  -- The access aisle: bands at 45 degrees inside its lines.
  for _, st in ipairs(strips) do
    local region = { { st[1] + w / 2, 0 }, { st[2] - w / 2, 0 }, { st[2] - w / 2, L - w / 2 }, { st[1] + w / 2, L - w / 2 } }
    local cx = (st[1] + st[2]) / 2
    for _, band in ipairs(hatch(region, 45, max(p.LarguraZebrado, 0.02), max(p.LarguraZebrado + p.EspacamentoZebrado, 0.05), cx, L / 2)) do
      add(out, prism(band, 0, THICK))
    end
  end
  -- The International Symbol of Access, white on the blue square.
  local fig = decode(FIGURAS.cadeirante)
  local size = S * 0.8 / max(fig.xmax - fig.xmin, fig.ymax - fig.ymin)
  local m = new_mesh()
  m.figure(fig, transform(0, L / 2, size, size, 0, (fig.xmin + fig.xmax) / 2, (fig.ymin + fig.ymax) / 2), BLUE, THICK)
  add(out, m.piece({ name = "Símbolo internacional de acesso" }))
  -- Number at the entry, legend beyond the symbol.
  local t = new_mesh()
  local room = W - 2 * w - 0.2
  local hn = max(p.AlturaNumero, 0.05)
  if p.Numero ~= "" then
    local y = min(0.3 + hn / 2, L / 2 - S / 2 - 0.1 - hn / 2)
    text(t, p.Numero, fit(p.Numero, { x = 0, y = y, altura = hn, largura = hn * 0.62, espaco = hn * 0.08, h = THICK }, room))
  end
  local hl = max(p.AlturaLegenda, 0.05)
  if p.Legenda ~= "" then
    local y = L / 2 + S / 2 + 0.25 + hl / 2
    y = min(y, L - w - 0.15 - hl / 2)
    text(t, p.Legenda, fit(p.Legenda, { x = 0, y = y, altura = hl, largura = hl * 0.5, espaco = hl * 0.1, h = THICK }, room))
  end
  add(out, t.piece({ name = "Texto" }))
  return out
end

--- legenda-pare
local THICK = 0.003

function geometry(p)
  local out = {}
  local lw = max(p.LarguraLinha, 0.05)
  local road = max(p.LarguraVia, 0.5)
  local opts = (p.Pintura ~= "" and p.Pintura) and { material = p.Pintura } or nil
  local front = 0 -- where the legend's far edge may reach
  if p.LinhaRetencao then
    add(out, rect(-road / 2, -lw, road / 2, 0, 0, THICK, opts and { name = "Linha de retenção", material = opts.material } or { name = "Linha de retenção" }))
    front = -lw
  end
  local h = max(p.AlturaLetra, 0.1)
  local m = new_mesh()
  local o = fit(p.Texto, { x = 0, y = front - max(p.Distancia, 0) - h / 2, altura = h, largura = max(p.LarguraLetra, 0.05), espaco = p.Espacamento, h = THICK }, road - 0.3)
  text(m, p.Texto, o)
  add(out, m.piece(opts and { name = "Legenda", material = opts.material } or { name = "Legenda" }))
  return out
end

--- legenda-piso
local THICK = 0.003

function geometry(p)
  local lines = {}
  for _, s in ipairs({ p.Linha1, p.Linha2, p.Linha3 }) do
    if s ~= "" then lines[#lines + 1] = s end
  end
  if #lines == 0 then return {} end
  local h, gap = max(p.AlturaLetra, 0.05), max(p.EntreLinhas, 0)
  local opts = (p.Pintura ~= "" and p.Pintura) and { name = "Legenda", material = p.Pintura } or { name = "Legenda" }
  local m = new_mesh()
  -- The first line is the nearest to the driver, who reads from near to far.
  local total = #lines * h + (#lines - 1) * gap
  for i, s in ipairs(lines) do
    local y = -total / 2 + h / 2 + (i - 1) * (h + gap)
    local o = fit(s, { x = 0, y = y, altura = h, largura = max(p.LarguraLetra, 0.02), espaco = p.Espacamento, h = THICK }, p.LarguraMaxima)
    text(m, s, o)
  end
  return { m.piece(opts) }
end

--- velocidade-piso
local THICK = 0.003

function geometry(p)
  local hn, hu = max(p.AlturaNumero, 0.05), max(p.AlturaUnidade, 0.05)
  local gap = max(p.Afastamento, 0)
  local opts = (p.Pintura ~= "" and p.Pintura) and { name = "Velocidade", material = p.Pintura } or { name = "Velocidade" }
  local m = new_mesh()
  local has_unit = p.Unidade ~= ""
  local total = hn + (has_unit and (gap + hu) or 0)
  -- The number first (nearest to the driver), the unit beyond it.
  local y = -total / 2 + hn / 2
  text(m, p.Velocidade, fit(p.Velocidade, { x = 0, y = y, altura = hn, largura = max(p.LarguraNumero, 0.02), espaco = hn * 0.06, h = THICK }, p.LarguraMaxima))
  if has_unit then
    local yu = -total / 2 + hn + gap + hu / 2
    text(m, p.Unidade, fit(p.Unidade, { x = 0, y = yu, altura = hu, largura = max(p.LarguraUnidade, 0.02), espaco = hu * 0.06, h = THICK }, p.LarguraMaxima))
  end
  local piece = m.piece(opts)
  return piece and { piece } or {}
end

--- seta-direcional
local THICK = 0.003

function geometry(p)
  local fig = decode(FIGURAS["seta_" .. p.Tipo] or FIGURAS.seta_frente)
  local sy = max(p.Comprimento, 0.3) / 1000
  local sx = sy / max(p.Alongamento, 0.2)
  local opts = (p.Pintura ~= "" and p.Pintura) and { name = "Seta", material = p.Pintura } or { name = "Seta" }
  local m = new_mesh()
  -- The arrow's middle (y = 500 of the figure) on the origin, the stem on x = 0.
  m.figure(fig, transform(0, 0, sx, sy, 0, 0, 500), 0, THICK)
  return { m.piece(opts) }
end

--- faixa-pedestres
local THICK = 0.003

function geometry(p)
  local road, band = max(p.LarguraVia, 0.5), max(p.LarguraFaixa, 0.3)
  local bw, gap = max(p.LarguraBarra, 0.05), max(p.Espacamento, 0.05)
  local opts = (p.Pintura ~= "" and p.Pintura) and { material = p.Pintura } or nil
  local out = {}
  if p.Tipo == "paralela" then
    -- Two lines across the road bounding the crossing.
    add(out, rect(-road / 2, -band / 2, road / 2, -band / 2 + bw, 0, THICK, opts), rect(-road / 2, band / 2 - bw, road / 2, band / 2, 0, THICK, opts))
  else
    -- Bars along the traffic, centred across the road.
    local n = floor((road + gap) / (bw + gap) + 1e-9)
    local span = n * bw + (n - 1) * gap
    for i = 0, n - 1 do
      local x = -span / 2 + i * (bw + gap)
      add(out, rect(x, -band / 2, x + bw, band / 2, 0, THICK, opts))
    end
  end
  if p.LinhasRetencao then
    local lw, d = max(p.LarguraRetencao, 0.05), max(p.DistanciaRetencao, 0)
    add(out, rect(-road / 2, -band / 2 - d - lw, road / 2, -band / 2 - d, 0, THICK, opts))
    if p.RetencaoDosDoisLados then
      add(out, rect(-road / 2, band / 2 + d, road / 2, band / 2 + d + lw, 0, THICK, opts))
    end
  end
  return out
end

--- simbolo-piso
local THICK = 0.003

function geometry(p)
  local fig = decode(FIGURAS[p.Simbolo] or FIGURAS.cadeirante)
  local sx = max(p.Largura, 0.1) / (fig.xmax - fig.xmin)
  local sy = sx * max(p.Alongamento, 0.2)
  local opts = (p.Pintura ~= "" and p.Pintura) and { name = "Símbolo", material = p.Pintura } or { name = "Símbolo" }
  local m = new_mesh()
  m.figure(fig, transform(0, 0, sx, sy, 0, (fig.xmin + fig.xmax) / 2, (fig.ymin + fig.ymax) / 2), 0, THICK)
  return { m.piece(opts) }
end

--- de-a-preferencia
local THICK = 0.003

function geometry(p)
  local b, l, t = max(p.Base, 0.2), max(p.Comprimento, 0.3), max(p.LarguraTraco, 0.02)
  local opts = (p.Pintura ~= "" and p.Pintura) and { material = p.Pintura } or nil
  local out = {}
  local front = 0
  if p.Linha then
    -- The give-way line: dashes across the road, centred.
    local road, lw = max(p.LarguraVia, 0.5), max(p.LarguraLinha, 0.05)
    local dash, space = max(p.Traco, 0.05), max(p.Intervalo, 0.05)
    local n = floor((road + space) / (dash + space) + 1e-9)
    local span = n * dash + (n - 1) * space
    for i = 0, n - 1 do
      local x = -span / 2 + i * (dash + space)
      add(out, rect(x, -lw, x + dash, 0, 0, THICK, opts))
    end
    front = -lw
  end
  -- The triangle points at the driver: its base is the far side.
  local yb = front - max(p.Distancia, 0)
  local A, B, C = { 0, yb - l }, { b / 2, yb }, { -b / 2, yb } -- counter-clockwise
  if not p.Vazado then
    add(out, prism({ A, B, C }, 0, THICK, opts))
    return out
  end
  -- An outline of three trapezoids that meet on the corners' bisectors.
  local function len(P, Q) return sqrt((P[1] - Q[1]) ^ 2 + (P[2] - Q[2]) ^ 2) end
  local a, bb, cc = len(B, C), len(C, A), len(A, B)
  local per = a + bb + cc
  local I = { (a * A[1] + bb * B[1] + cc * C[1]) / per, (a * A[2] + bb * B[2] + cc * C[2]) / per }
  local s = per / 2
  local r = sqrt(max(s * (s - a) * (s - bb) * (s - cc), 0)) / s
  if t >= r * 0.95 then
    add(out, prism({ A, B, C }, 0, THICK, opts))
    return out
  end
  local k = (r - t) / r
  local function inner(P) return { I[1] + (P[1] - I[1]) * k, I[2] + (P[2] - I[2]) * k } end
  local Ai, Bi, Ci = inner(A), inner(B), inner(C)
  add(out, prism({ A, B, Bi, Ai }, 0, THICK, opts), prism({ B, C, Ci, Bi }, 0, THICK, opts), prism({ C, A, Ai, Ci }, 0, THICK, opts))
  return out
end

--- area-zebrada
local THICK = 0.003

function geometry(p)
  local W, L, w = max(p.Largura, 0.3), max(p.Comprimento, 0.3), max(p.LarguraLinha, 0.01)
  local region = { { -W / 2 + w, -L / 2 + w }, { W / 2 - w, -L / 2 + w }, { W / 2 - w, L / 2 - w }, { -W / 2 + w, L / 2 - w } }
  if W <= 2 * w or L <= 2 * w then return {} end
  local out = {}
  local fw = max(p.LarguraFaixa, 0.02)
  for _, band in ipairs(hatch(region, p.AnguloFaixas, fw, fw + max(p.Espacamento, 0.02), 0, 0)) do
    add(out, prism(band, 0, THICK))
  end
  return out
end

--- lombada
local THICK = 0.003

function geometry(p)
  local W, L, H = max(p.LarguraVia, 0.5), max(p.Comprimento, 0.3), max(p.Altura, 0.005)
  local R = (L * L / 4 + H * H) / (2 * H)
  local function zf(y) local q = R * R - y * y; return (q > 0 and sqrt(q) or 0) - (R - H) end
  local region = { { -W / 2, -L / 2 }, { W / 2, -L / 2 }, { W / 2, L / 2 }, { -W / 2, L / 2 } }
  local fw = max(p.LarguraFaixa, 0.05)
  local bands = hatch(region, p.AnguloFaixas, fw, fw + max(p.Espacamento, 0.05), 0, 0)
  -- Each band is draped on the hump: cut into slices across the traffic, every vertex on a
  -- cut, so each slice is a flat face; the paint stands THICK above the surface.
  local m = { v = {}, f = {} }
  local function vtx(x, y, dz) local n = #m.v + 1; m.v[n] = { x, y, zf(y) + dz }; return n end
  local STEP = 0.08
  local sunk = -0.0005 -- the paint's underside, just inside the hump
  for _, band in ipairs(bands) do
    local ys = {}
    local y0, y1 = 1e9, -1e9
    for _, q in ipairs(band) do y0, y1 = min(y0, q[2]), max(y1, q[2]) end
    local cuts = { y0 }
    local y = (floor(y0 / STEP) + 1) * STEP
    while y < y1 - 1e-6 do cuts[#cuts + 1] = y; y = y + STEP end
    cuts[#cuts + 1] = y1
    for _, q in ipairs(band) do cuts[#cuts + 1] = q[2] end
    table.sort(cuts)
    local uniq = {}
    for _, c in ipairs(cuts) do if #uniq == 0 or c - uniq[#uniq] > 1e-6 then uniq[#uniq + 1] = c end end
    for i = 1, #uniq - 1 do
      local a, b = uniq[i], uniq[i + 1]
      local slab = clip_half(clip_half(band, 0, a, 1, a), 1, b, 0, b) -- a <= y <= b
      if #slab >= 3 then
        local top, bot = {}, {}
        for k, q in ipairs(slab) do
          top[k] = vtx(q[1], q[2], THICK)
          bot[#slab - k + 1] = vtx(q[1], q[2], sunk)
        end
        m.f[#m.f + 1] = top
        m.f[#m.f + 1] = bot
      end
    end
    -- The band's sides, split at the same cuts.
    local n = #band
    for i = 1, n do
      local P, Q = band[i], band[i % n + 1]
      local pts = { P }
      local lo, hi = min(P[2], Q[2]), max(P[2], Q[2])
      local inside = {}
      for _, c in ipairs(uniq) do if c > lo + 1e-6 and c < hi - 1e-6 then inside[#inside + 1] = c end end
      if Q[2] < P[2] then table.sort(inside, function(u, v) return u > v end) end
      for _, c in ipairs(inside) do
        local t = (c - P[2]) / (Q[2] - P[2])
        pts[#pts + 1] = { P[1] + (Q[1] - P[1]) * t, c }
      end
      pts[#pts + 1] = Q
      for k = 1, #pts - 1 do
        local u, v = pts[k], pts[k + 1]
        local a0, b0 = vtx(u[1], u[2], sunk), vtx(v[1], v[2], sunk)
        local b1, a1 = vtx(v[1], v[2], THICK), vtx(u[1], u[2], THICK)
        m.f[#m.f + 1] = { a0, b0, b1, a1 }
      end
    end
  end
  if #m.f == 0 then return {} end
  return { mesh { vertices = m.v, faces = m.f, name = "Pintura" } }
end
