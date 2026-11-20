-- Shared by the floor markings of sources/site/: painted figures and text as
-- thin solids lying on the floor. Generated into each component by tools/site.py.

local floor, abs, sqrt, cos, sin, rad, min, max = math.floor, math.abs, math.sqrt, math.cos, math.sin, math.rad, math.min, math.max
local byte, sub = string.byte, string.sub

-- Figures (glyphs, pictograms, arrows) are strings of base 64 pairs: see tools/site/fonte.py.
local B64 = {}
do
  local alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
  for i = 1, 64 do B64[byte(alphabet, i)] = i - 1 end
end

local function decode(s)
  local n, pos = #s, 1
  local function nxt()
    local a, b = byte(s, pos, pos + 1)
    pos = pos + 2
    return B64[a] * 64 + B64[b] - 1024
  end
  local fig = { advance = nxt(), rings = {}, tris = {} }
  local count = nxt()
  local sizes = {}
  for i = 1, count do sizes[i] = nxt() end
  local xmin, xmax, ymin, ymax = 1e9, -1e9, 1e9, -1e9
  for i = 1, count do
    local ring = {}
    for k = 1, sizes[i] do
      local x, y = nxt(), nxt()
      ring[#ring + 1] = x; ring[#ring + 1] = y
      if x < xmin then xmin = x end; if x > xmax then xmax = x end
      if y < ymin then ymin = y end; if y > ymax then ymax = y end
    end
    fig.rings[i] = ring
  end
  local nt = nxt()
  for i = 1, nt * 3 do fig.tris[i] = nxt() end
  fig.xmin, fig.xmax, fig.ymin, fig.ymax = xmin, xmax, ymin, ymax
  if count == 0 then fig.xmin, fig.xmax, fig.ymin, fig.ymax = 0, 0, 0, 0 end
  return fig
end

-- A mesh that figures are added to; `piece` returns it as one mesh piece.
local function new_mesh()
  local m = { v = {}, f = {}, empty = true }
  -- Adds `fig` as a prism from z to z + h, its points (x, y) going to T(x, y).
  function m.figure(fig, T, z, h, flip)
    if #fig.rings == 0 then return end
    m.empty = false
    local v, f = m.v, m.f
    local base = #v -- vertex numbers from base + 1
    local pts = 0
    local bottom, top = {}, {}
    for _, ring in ipairs(fig.rings) do
      for k = 1, #ring, 2 do
        local x, y = T(ring[k], ring[k + 1])
        pts = pts + 1
        v[#v + 1] = { x, y, z }
      end
    end
    for i = 1, pts do
      local p = v[base + i]
      v[#v + 1] = { p[1], p[2], z + h }
    end
    local tris = fig.tris
    for i = 1, #tris, 3 do
      local a, b, c = base + tris[i] + 1, base + tris[i + 1] + 1, base + tris[i + 2] + 1
      if flip then b, c = c, b end
      f[#f + 1] = { a + pts, b + pts, c + pts } -- top, counter-clockwise from above
      f[#f + 1] = { a, c, b } -- bottom
    end
    local first = base
    for _, ring in ipairs(fig.rings) do
      local n = floor(#ring / 2)
      for k = 0, n - 1 do
        local a, b = first + k + 1, first + (k + 1) % n + 1
        if flip then a, b = b, a end
        f[#f + 1] = { a, b, b + pts, a + pts }
      end
      first = first + n
    end
  end
  function m.piece(opts)
    if m.empty then return nil end
    local p = mesh { vertices = m.v, faces = m.f }
    if opts then for k, val in pairs(opts) do p[k] = val end end
    return p
  end
  return m
end

-- An affine map of figure units: scale (sx, sy), turn by `ang` degrees, move to (x0, y0).
local function transform(x0, y0, sx, sy, ang, ox, oy)
  local c, s = cos(rad(ang or 0)), sin(rad(ang or 0))
  ox, oy = ox or 0, oy or 0
  return function(x, y)
    local u, w = (x - ox) * sx, (y - oy) * sy
    return x0 + u * c - w * s, y0 + u * s + w * c
  end
end

-- --- text -----------------------------------------------------------------------

local glyph_cache = {}
local function glyph(code)
  local g = glyph_cache[code]
  if g == nil then
    local data = FONTE.glyphs[code]
    g = data and decode(data) or false
    glyph_cache[code] = g
  end
  return g or nil
end

-- The code points of a UTF-8 string (invalid bytes are skipped).
local function codepoints(s)
  local out, i, n = {}, 1, #s
  while i <= n do
    local c = byte(s, i)
    local cp, len
    if c < 0x80 then cp, len = c, 1
    elseif c >= 0xC2 and c < 0xE0 then cp, len = c - 0xC0, 2
    elseif c >= 0xE0 and c < 0xF0 then cp, len = c - 0xE0, 3
    elseif c >= 0xF0 and c < 0xF5 then cp, len = c - 0xF0, 4
    else cp, len = nil, 1 end
    if cp and i + len - 1 <= n then
      for k = 1, len - 1 do
        local cc = byte(s, i + k)
        if cc < 0x80 or cc > 0xBF then cp = nil; break end
        cp = cp * 64 + (cc - 0x80)
      end
    else cp = nil end
    if cp then out[#out + 1] = cp end
    i = i + len
  end
  return out
end

-- Look-alikes for characters the font table lacks.
local FALLBACK = { [0x2014] = 0x2013, [0x2010] = 45, [0x2011] = 45, [0x2212] = 45, [0x2018] = 39, [0x2019] = 39,
  [0x201C] = 34, [0x201D] = 34, [0xA0] = 32, [0x2022] = 42, [0xB7] = 46 }

-- Lays a line of text out on the floor and adds it to mesh `m`.
-- o: x, y (the anchor), ang (degrees, the reading direction from +x), altura (the capital
-- height, along the letters), largura (the width of an H; the other letters follow),
-- espaco (extra space between letters), z, h (the paint's thickness), alinha ("centro",
-- "esquerda" or "direita", where the anchor falls along the line) and base ("centro":
-- the anchor halfway up the capitals, or "linha": on the baseline).
-- Returns the width of the ink, or 0 for an empty text.
local function layout(s, o)
  local sy = (o.altura or 1) / FONTE.cap
  local sx = (o.largura or (o.altura or 1) * FONTE.h_width / FONTE.cap) / FONTE.h_width
  local gap = (o.espaco or 0) / sx
  local items, pen = {}, 0
  local ink0, ink1 = nil, nil
  for _, cp in ipairs(codepoints(s or "")) do
    if cp == 32 or cp == 9 or cp == 0xA0 then
      pen = pen + FONTE.space + gap
    else
      local g = glyph(cp) or glyph(FALLBACK[cp] or 63)
      if g then
        items[#items + 1] = { g, pen }
        if #g.rings > 0 then
          local a, b = pen + g.xmin, pen + g.xmax
          if ink0 == nil or a < ink0 then ink0 = a end
          if ink1 == nil or b > ink1 then ink1 = b end
        end
        pen = pen + g.advance + gap
      end
    end
  end
  return items, ink0, ink1, sx, sy
end

-- The width of the ink of a line of text laid out with `o` (see `text`).
local function text_width(s, o)
  local _, ink0, ink1, sx = layout(s, o)
  if ink0 == nil then return 0 end
  return (ink1 - ink0) * sx
end

-- `o` with its letters narrowed (and their spacing) so the text is at most `limit` wide.
local function fit(s, o, limit)
  local w = text_width(s, o)
  if limit and limit > 0 and w > limit then
    local k = limit / w
    local q = {}
    for key, val in pairs(o) do q[key] = val end
    q.largura = (o.largura or (o.altura or 1) * FONTE.h_width / FONTE.cap) * k
    q.espaco = (o.espaco or 0) * k
    return q
  end
  return o
end

local function text(m, s, o)
  local items, ink0, ink1, sx, sy = layout(s, o)
  if ink0 == nil then return 0 end
  local width = ink1 - ink0
  local start = ink0 + width / 2
  if o.alinha == "esquerda" then start = ink0 elseif o.alinha == "direita" then start = ink1 end
  local base = (o.base == "linha") and 0 or FONTE.cap / 2
  for _, it in ipairs(items) do
    local g, at = it[1], it[2]
    m.figure(g, transform(o.x or 0, o.y or 0, sx, sy, o.ang or 0, start - at, base), o.z or 0, o.h or 0.003)
  end
  return width * sx
end

-- --- simple shapes -------------------------------------------------------------------

-- A painted strip from (ax, ay) to (bx, by), w wide, as an extrusion.
local function strip(ax, ay, bx, by, w, z, h, opts)
  local dx, dy = bx - ax, by - ay
  local l = sqrt(dx * dx + dy * dy)
  if l < 1e-9 or w <= 0 then return nil end
  local nx, ny = -dy / l * w / 2, dx / l * w / 2
  local p = extrusion { points = { { ax + nx, ay + ny }, { ax - nx, ay - ny }, { bx - nx, by - ny }, { bx + nx, by + ny } }, z = z, height = h }
  if opts then for k, val in pairs(opts) do p[k] = val end end
  return p
end

-- A painted rectangle between x0..x1 and y0..y1.
local function rect(x0, y0, x1, y1, z, h, opts)
  if x1 - x0 <= 1e-9 or y1 - y0 <= 1e-9 then return nil end
  local p = box { x0, y0, z, x1 - x0, y1 - y0, h }
  if opts then for k, val in pairs(opts) do p[k] = val end end
  return p
end

-- The part of the convex polygon `poly` ({{x, y}, ...}, counter-clockwise) on the left of a -> b.
local function clip_half(poly, ax, ay, bx, by)
  local out = {}
  local n = #poly
  if n == 0 then return out end
  local function side(p) return (bx - ax) * (p[2] - ay) - (by - ay) * (p[1] - ax) end
  for i = 1, n do
    local p, q = poly[i], poly[i % n + 1]
    local sp, sq = side(p), side(q)
    if sp >= 0 then out[#out + 1] = p end
    if (sp >= 0) ~= (sq >= 0) then
      local t = sp / (sp - sq)
      out[#out + 1] = { p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t }
    end
  end
  return out
end

-- `poly` clipped to the convex polygon `region` (both counter-clockwise).
local function clip(poly, region)
  local out = poly
  for i = 1, #region do
    local a, b = region[i], region[i % #region + 1]
    out = clip_half(out, a[1], a[2], b[1], b[2])
    if #out < 3 then return {} end
  end
  return out
end

local function area(poly)
  local s = 0
  for i = 1, #poly do
    local p, q = poly[i], poly[i % #poly + 1]
    s = s + p[1] * q[2] - q[1] * p[2]
  end
  return s / 2
end

-- Parallel bands across the convex `region`, turned `ang` degrees from +x, `w` wide every
-- `step` (centre to centre), one band centred on (cx, cy). Returns the band polygons.
local function hatch(region, ang, w, step, cx, cy)
  local c, s = cos(rad(ang)), sin(rad(ang))
  local nx, ny = -s, c -- across the bands
  local lo, hi, far = 1e9, -1e9, 0
  for _, p in ipairs(region) do
    local d = (p[1] - cx) * nx + (p[2] - cy) * ny
    lo, hi = min(lo, d), max(hi, d)
    far = max(far, abs(p[1] - cx) + abs(p[2] - cy))
  end
  local out = {}
  local k0, k1 = floor(lo / step) - 1, floor(hi / step) + 1
  for k = k0, k1 do
    local d0, d1 = k * step - w / 2, k * step + w / 2
    local L = far + 1
    local band = {
      { cx + nx * d0 - c * L, cy + ny * d0 - s * L },
      { cx + nx * d0 + c * L, cy + ny * d0 + s * L },
      { cx + nx * d1 + c * L, cy + ny * d1 + s * L },
      { cx + nx * d1 - c * L, cy + ny * d1 - s * L },
    }
    if area(band) < 0 then band = { band[4], band[3], band[2], band[1] } end
    local piece = clip(band, region)
    if #piece >= 3 and abs(area(piece)) > 1e-5 then out[#out + 1] = piece end
  end
  return out
end

local function prism(poly, z, h, opts)
  if #poly < 3 then return nil end
  local p = extrusion { points = poly, z = z, height = h }
  if opts then for k, val in pairs(opts) do p[k] = val end end
  return p
end

-- Appends the pieces of `more` (skipping nils) to `list`.
local function add(list, ...)
  for i = 1, select("#", ...) do
    local p = select(i, ...)
    if p then list[#list + 1] = p end
  end
  return list
end
