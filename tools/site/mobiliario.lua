-- The geometry(p) functions of the site furniture and the accessibility pieces, one
-- section per component (between "--- <file>" lines), as in componentes.lua. The
-- scripts add the parts whose number or presence follows the parameters; the parts
-- that are always there are plain pieces, which carry the materials.

--- banco-praca
-- The supports' section (side view: y across, z up), the same as the plain end supports.
local function support(x, t)
  return profile { points = { { -0.24, 0 }, { 0.24, 0 }, { 0.2, 0.42 }, { -0.2, 0.42 } }, offset = x - t / 2, depth = t, plane = "side", material = MAT.concreto, name = "Apoio intermediário" }
end

function geometry(p)
  local L = max(p.Comprimento, 0.6)
  local out = {}
  -- A middle support every 2 m or so.
  local inner = floor((L - 0.5) / 2.0)
  for i = 1, inner do
    local x = -(L / 2 - 0.25) + i * (L - 0.5) / (inner + 1)
    add(out, support(x, 0.12))
  end
  if p.Encosto then
    -- Three slats leaning back 15 degrees on concrete uprights at each support.
    local lean = rad(15)
    local s, c = sin(lean), cos(lean)
    local function slat(z0)
      local w, t = 0.09, 0.035
      local y0, zb = 0.2 + z0 * s, 0.47 + z0 * c
      local pts = { { y0, zb }, { y0 + t * c, zb - t * s }, { y0 + t * c + w * s, zb - t * s + w * c }, { y0 + w * s, zb + w * c } }
      return profile { points = pts, offset = -L / 2, depth = L, plane = "side", material = MAT.madeira, name = "Ripa do encosto" }
    end
    for i = 0, 2 do add(out, slat(i * 0.11)) end
    local xs = { -(L / 2 - 0.25), L / 2 - 0.25 }
    for i = 1, inner do xs[#xs + 1] = -(L / 2 - 0.25) + i * (L - 0.5) / (inner + 1) end
    for _, x in ipairs(xs) do
      local up = { { 0.2, 0.42 }, { 0.24, 0.42 }, { 0.24 + 0.36 * s, 0.42 + 0.36 * c }, { 0.2 + 0.36 * s, 0.42 + 0.36 * c } }
      add(out, profile { points = up, offset = x - 0.04, depth = 0.08, plane = "side", material = MAT.concreto, name = "Montante do encosto" })
    end
  end
  return out
end

--- coletores-reciclaveis
local FACE, H = 0.0005, 0.0005

function geometry(p)
  local w, gap = 0.4, 0.03
  local m = new_mesh("front")
  local labels = { p.Rotulo1, p.Rotulo2, p.Rotulo3, p.Rotulo4 }
  for i, s in ipairs(labels) do
    local x = -1.5 * (w + gap) + (i - 1) * (w + gap)
    -- The bins' fronts stand at y = -0.15; the label goes over the top third.
    local o = { x = x, y = 0.83, altura = 0.045, largura = 0.03, espaco = 0.004, z = 0.15 + FACE, h = H }
    text(m, s, fit(s, o, w * 0.82))
  end
  local piece = m.piece({ name = "Rótulos" })
  return piece and { piece } or {}
end

--- bicicletario
function geometry(p)
  local n = max(floor(p.Suportes + 0.5), 1)
  local step, h, half, r = p.Espacamento, p.Altura, p.Largura / 2, 0.025
  local bend = min(0.2, half * 0.9)
  local out = {}
  for i = 0, n - 1 do
    local x = -(n - 1) * step / 2 + i * step
    -- An inverted U of 50 mm tube in the y-z plane, its bends 200 mm in radius.
    add(out, sweep {
      path = { { -half, 0 }, { -half, h - bend, radius = -bend }, { -half + bend, h }, { half - bend, h, radius = -bend }, { half, h - bend }, { half, 0 } },
      profile = { { -r, 0, radius = r }, { r, 0, radius = r } },
      offset = x, plane = "side", material = MAT.aco, name = "Suporte em U",
    })
    if i > 0 then
      for _, y in ipairs({ -half, half }) do
        add(out, cylinder { x, y, 0, 0.06, 0.006, material = MAT.aco, name = "Flange" })
      end
    end
  end
  return out
end

--- pergolado
function geometry(p)
  local W, D, Hh = p.Largura, p.Profundidade, p.Altura
  local post, beam_h, beam_w = 0.15, 0.2, 0.06
  local out = {}
  -- Middle posts on the long sides, about every 3 m.
  local spans = max(1, math.ceil((W - post) / 3.0 - 1e-9))
  for i = 1, spans - 1 do
    local x = -W / 2 + post / 2 + i * (W - post) / spans
    for _, y in ipairs({ -D / 2 + post / 2, D / 2 - post / 2 }) do
      add(out, box { x - post / 2, y - post / 2, 0, post, post, Hh - beam_h, material = MAT.madeira, name = "Pilar intermediário" })
    end
  end
  -- Rafters across, over the beams, every Espacamento.
  local sw, sh = max(p.LarguraCaibro, 0.03), max(p.AlturaCaibro, 0.05)
  local n = max(2, floor((W - sw) / max(p.Espacamento, 0.1)) + 1)
  local over = 0.25
  for i = 0, n - 1 do
    local x = -W / 2 + sw / 2 + i * (W - sw) / (n - 1)
    add(out, box { x - sw / 2, -D / 2 - over, Hh, sw, D + 2 * over, sh, material = MAT.madeira, name = "Caibro" })
  end
  return out
end

--- piso-tatil
-- Relief of ABNT NBR 16537 on 250 mm tiles: warning (truncated cones 25 mm across at the
-- base, 4 mm high, 60 mm apart) or directional (bars 30 mm wide at the top, 4 mm high,
-- 75 mm apart along the walking direction, y).
local H = 0.004

local function frustum(m, cx, cy, r0, r1, h, n)
  local v, f = m.v, m.f
  local base = #v
  for i = 0, n - 1 do
    local a = 2 * math.pi * i / n
    v[#v + 1] = { cx + r0 * cos(a), cy + r0 * sin(a), 0 }
  end
  for i = 0, n - 1 do
    local a = 2 * math.pi * i / n
    v[#v + 1] = { cx + r1 * cos(a), cy + r1 * sin(a), h }
  end
  local top, bottom = {}, {}
  for i = 1, n do top[i] = base + n + i; bottom[i] = base + n - i + 1 end
  f[#f + 1] = top
  f[#f + 1] = bottom
  for i = 1, n do
    local j = i % n + 1
    f[#f + 1] = { base + i, base + j, base + n + j, base + n + i }
  end
end

function geometry(p)
  local W, L, T = p.Largura, p.Comprimento, 0.25
  local m = { v = {}, f = {} }
  local nx, ny = max(1, floor(W / T + 1e-6)), max(1, floor(L / T + 1e-6))
  local x0, y0 = -W / 2, -L / 2
  for i = 0, nx - 1 do
    for j = 0, ny - 1 do
      local tx, ty = x0 + i * T, y0 + j * T
      if p.Tipo == "direcional" then
        -- Four bars across the tile, running along y (the walking direction).
        for k = 0, 3 do
          local cx = tx + T / 8 + k * T / 4
          local v, f = m.v, m.f
          local b = #v
          local w0, w1, ya, yb = 0.04, 0.03, ty + 0.02, ty + T - 0.02
          local d = (w0 - w1) / 2
          local pts = {
            { cx - w0 / 2, ya, 0 }, { cx + w0 / 2, ya, 0 }, { cx + w0 / 2, yb, 0 }, { cx - w0 / 2, yb, 0 },
            { cx - w1 / 2, ya + d, H }, { cx + w1 / 2, ya + d, H }, { cx + w1 / 2, yb - d, H }, { cx - w1 / 2, yb - d, H },
          }
          for _, q in ipairs(pts) do v[#v + 1] = q end
          f[#f + 1] = { b + 5, b + 6, b + 7, b + 8 }
          f[#f + 1] = { b + 4, b + 3, b + 2, b + 1 }
          f[#f + 1] = { b + 1, b + 2, b + 6, b + 5 }
          f[#f + 1] = { b + 2, b + 3, b + 7, b + 6 }
          f[#f + 1] = { b + 3, b + 4, b + 8, b + 7 }
          f[#f + 1] = { b + 4, b + 1, b + 5, b + 8 }
        end
      else
        -- A 4 x 4 grid of truncated cones, 60 mm apart, centred on the tile.
        for a = 0, 3 do
          for c = 0, 3 do
            frustum(m, tx + T / 2 + (a - 1.5) * 0.06, ty + T / 2 + (c - 1.5) * 0.06, 0.0125, 0.0075, H, 12)
          end
        end
      end
    end
  end
  if #m.f == 0 then return {} end
  return { mesh { vertices = m.v, faces = m.f, name = "Relevo" } }
end
