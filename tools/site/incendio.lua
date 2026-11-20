-- The geometry(p) functions of the fire protection components, one section per component
-- (between "--- <file>" lines), as in componentes.lua: the parts whose presence follows the
-- parameters and the editable texts. The parts always there are plain pieces, which carry
-- the materials (MAT.<key>).

--- extintor
-- A truncated cone as a mesh, axis vertical at (cx, cy), from z0 (radius r0) to z1 (radius r1).
local function cone(cx, cy, z0, r0, z1, r1, n, opts)
  local v, f = {}, {}
  for i = 0, n - 1 do
    local a = 2 * math.pi * i / n
    v[#v + 1] = { cx + r0 * cos(a), cy + r0 * sin(a), z0 }
  end
  for i = 0, n - 1 do
    local a = 2 * math.pi * i / n
    v[#v + 1] = { cx + r1 * cos(a), cy + r1 * sin(a), z1 }
  end
  local top, bottom = {}, {}
  for i = 1, n do top[i] = n + i; bottom[i] = n - i + 1 end
  f[1], f[2] = top, bottom
  for i = 1, n do
    local j = i % n + 1
    f[#f + 1] = { i, j, n + j, n + i }
  end
  local p = mesh { vertices = v, faces = f }
  for k, val in pairs(opts) do p[k] = val end
  return p
end

local function tube(path, r, y, name)
  return sweep { path = path, profile = { { -r, 0, radius = r }, { r, 0, radius = r } }, offset = y, plane = "front", material = MAT.preto, name = name }
end

function geometry(p)
  local R, H, E = p.Diametro / 2, p.AlturaCorpo, p.Elevacao
  local cy = -0.035 - R
  local top = E + H
  local out = {}
  if p.Difusor then
    -- CO2: a thick hose from the valve down the right side to the horn.
    local x, zh = R + 0.065, E + 0.1
    add(out, tube({ { 0.02, top + 0.045 }, { x - 0.03, top + 0.045, radius = -0.03 }, { x, top + 0.015 }, { x, zh + 0.33 } }, 0.011, cy, "Mangueira"))
    add(out, cone(x, cy, zh + 0.3, 0.016, zh + 0.34, 0.016, 20, { material = MAT.preto, name = "Punho do difusor" }))
    add(out, cone(x, cy, zh, 0.052, zh + 0.3, 0.014, 28, { material = MAT.preto, name = "Difusor" }))
  else
    -- The gauge on the valve's front, the hose down the right side and its nozzle.
    local zg = top + 0.047
    add(out, profile { points = { { -0.018, zg, radius = 0.018 }, { 0.018, zg, radius = 0.018 } }, offset = cy - 0.032, depth = 0.012, plane = "front", material = MAT.latao, name = "Manômetro" })
    add(out, profile { points = { { -0.015, zg, radius = 0.015 }, { 0.015, zg, radius = 0.015 } }, offset = cy - 0.0326, depth = 0.0006, plane = "front", material = MAT.branco, name = "Mostrador do manômetro" })
    local x, zn = R + 0.02, E + 0.3 * H
    add(out, tube({ { 0.02, top + 0.04 }, { x - 0.025, top + 0.04, radius = -0.025 }, { x, top + 0.015 }, { x, zn } }, 0.008, cy, "Mangueira"))
    add(out, cone(x, cy, zn - 0.075, 0.009, zn + 0.005, 0.012, 16, { material = MAT.preto, name = "Esguicho" }))
  end
  if E >= 0.3 then
    -- The wall bracket: a plate and a hook under the handle's back end.
    add(out, box { -0.035, -0.004, top - 0.15, 0.07, 0.004, 0.2, material = MAT.galvanizado, name = "Suporte de parede" })
    add(out, box { -0.012, cy + 0.06, top + 0.035, 0.024, -0.004 - (cy + 0.06), 0.012, material = MAT.galvanizado, name = "Gancho" })
    add(out, box { -0.012, cy + 0.05, top + 0.035, 0.024, 0.01, 0.026, material = MAT.galvanizado, name = "Ponta do gancho" })
  else
    -- The floor stand: a base, a cup under the cylinder and a post behind it.
    add(out, box { -0.17, cy - 0.17, 0, 0.34, 0.34, 0.006, material = MAT.vermelho, name = "Base do suporte de piso" })
    if E > 0.012 then
      add(out, cylinder { 0, cy, 0.006, R + 0.008, E - 0.006, material = MAT.vermelho, name = "Apoio do cilindro" })
    end
    add(out, box { -0.015, cy + R + 0.002, 0.006, 0.03, 0.012, E + 0.6 * H, material = MAT.vermelho, name = "Haste do suporte" })
  end
  if p.SinalizacaoPiso then
    -- The floor under the extinguisher: a 1 m square, red with a yellow border.
    local b, z, t = 0.15, 0, 0.003
    add(out, rect(-0.5, -1, 0.5, -1 + b, z, t, { material = MAT.amarelo, name = "Borda amarela 1" }))
    add(out, rect(-0.5, -b, 0.5, 0, z, t, { material = MAT.amarelo, name = "Borda amarela 2" }))
    add(out, rect(-0.5, -1 + b, -0.5 + b, -b, z, t, { material = MAT.amarelo, name = "Borda amarela 3" }))
    add(out, rect(0.5 - b, -1 + b, 0.5, -b, z, t, { material = MAT.amarelo, name = "Borda amarela 4" }))
    add(out, rect(-0.5 + b, -1 + b, 0.5 - b, -b, z, t, { material = MAT.vermelho, name = "Área vermelha" }))
  end
  return out
end

--- abrigo-hidrante
-- The lettering on the door's glass (in front of it, the glass' front at y = -(P + 0.012)).
function geometry(p)
  local L, A, P, E = p.Largura, p.Altura, p.Profundidade, p.Elevacao
  local fw = 0.035
  local w = L - 2 * fw
  local lines = {}
  for _, s in ipairs({ p.Linha1, p.Linha2 }) do if s ~= "" then lines[#lines + 1] = s end end
  local h = min(0.07, w * 0.13)
  local m = new_mesh("front")
  for i, s in ipairs(lines) do
    local z = E + A - fw - 0.04 - h / 2 - (i - 1) * h * 1.5
    text(m, s, fit(s, { x = 0, y = z, altura = h, largura = h * 0.62, espaco = h * 0.06, z = P + 0.012, h = 0.0005 }, w * 0.85))
  end
  local piece = m.piece({ name = "Inscrição" })
  return piece and { piece } or {}
end

--- hidrante-recalque
-- The word cast on the cover, painted (the cover's top at z = 0).
function geometry(p)
  local L, C = p.Largura, p.Comprimento
  local h = min(0.07, C * 0.12)
  local m = new_mesh()
  text(m, p.Inscricao, fit(p.Inscricao, { x = 0, y = 0, altura = h, largura = h * 0.62, espaco = h * 0.08, z = 0, h = 0.002 }, L * 0.82))
  local piece = m.piece({ name = "Inscrição" })
  return piece and { piece } or {}
end

--- detector-incendio
-- The indicator LED (the script's own material) and the heat detector's thermistor,
-- under the body, in a guard of four ribs.
function geometry(p)
  local out = { cylinder { 0.03, 0, -0.0505, 0.0028, 0.0015, name = "LED" } }
  if not p.Termico then return out end
  add(out, cylinder { 0, 0, -0.06, 0.0035, 0.011, material = MAT.preto, name = "Termistor" })
  for i = 0, 3 do
    local a = i * math.pi / 2 + math.pi / 4
    add(out, box { 0.016 * cos(a) - 0.002, 0.016 * sin(a) - 0.002, -0.063, 0.004, 0.004, 0.014, material = MAT.branco, name = "Proteção " .. (i + 1) })
  end
  return out
end

--- acionador-manual
function geometry(p)
  local L, A, E = p.Largura, p.Altura, p.Elevacao
  local D = 0.052
  local out = {}
  local m = new_mesh("front")
  local h1 = A * 0.075
  text(m, p.Linha1, fit(p.Linha1, { x = 0, y = E + A * 0.84, altura = h1, largura = h1 * 0.62, espaco = h1 * 0.08, z = D, h = 0.0004 }, L * 0.86))
  add(out, m.piece({ name = "Texto do corpo" }))
  local m2 = new_mesh("front")
  local h2 = A * 0.085
  text(m2, p.Linha2, fit(p.Linha2, { x = 0, y = E + A * 0.42, altura = h2, largura = h2 * 0.62, espaco = h2 * 0.08, z = D + 0.0015, h = 0.0004 }, L * 0.62))
  add(out, m2.piece({ name = "Texto do visor", material = MAT.preto }))
  return out
end

--- sirene-audiovisual
-- The word on the strobe's lens (its front at y = -0.034).
function geometry(p)
  local E = p.Elevacao
  local h = 0.014
  local m = new_mesh("front")
  text(m, p.Texto, fit(p.Texto, { x = 0, y = E + 0.1435, altura = h, largura = h * 0.62, espaco = h * 0.08, z = 0.034, h = 0.0005 }, 0.07))
  local piece = m.piece({ name = "Texto da lente" })
  return piece and { piece } or {}
end

--- central-alarme
-- One or two lines over the display, on the box's front (y = -P).
function geometry(p)
  local L, A, P, E = p.Largura, p.Altura, p.Profundidade, p.Elevacao
  local lines = {}
  for _, s in ipairs({ p.Linha1, p.Linha2 }) do if s ~= "" then lines[#lines + 1] = s end end
  local h = A * 0.065
  local m = new_mesh("front")
  local zc = E + A * 0.835
  for i, s in ipairs(lines) do
    local z = zc + (#lines - 1) * h * 0.8 - (i - 1) * h * 1.6
    text(m, s, fit(s, { x = 0, y = z, altura = h, largura = h * 0.62, espaco = h * 0.08, z = P, h = 0.0005 }, L * 0.84))
  end
  local piece = m.piece({ name = "Texto da tampa" })
  return piece and { piece } or {}
end
