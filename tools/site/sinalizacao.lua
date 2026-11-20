-- The geometry(p) functions of the signs, one section per component (between
-- "--- <file>" lines), as in componentes.lua.
--
-- Signs face -y. Their plates are plain pieces (so their materials travel with the
-- component); the scripts draw the symbols and text on the face as thin layers in
-- front of it, with new_mesh("front"): z is the distance in front of y = 0.

--- placa-regulamentacao
-- Layers of the face, towards the viewer (-y): the plain pieces' films up to y = -0.001,
-- then the symbols (L1) and the red bars over them (L2), 0.5 mm each.
local L1, L2, H = 0.001, 0.0015, 0.0005

function geometry(p)
  local D = max(p.Diametro, 0.2)
  local cz = p.AlturaLivre + D / 2
  local ri = D / 2 - D * 0.1 -- the white field inside the red ring
  local black, red, white = new_mesh("front"), new_mesh("front"), new_mesh("front")
  local function bar(ang, w)
    local c, s = cos(rad(ang)), sin(rad(ang))
    local nx, ny = -s * w / 2, c * w / 2
    red.figure(poly_figure({ { -ri * c + nx, -ri * s + ny }, { -ri * c - nx, -ri * s - ny }, { ri * c - nx, ri * s - ny }, { ri * c + nx, ri * s + ny } }), transform(0, cz, 1, 1), L2, H)
  end
  local function letter(s, height)
    text(black, s, { x = 0, y = cz, altura = height, largura = height * 0.62, z = L1, h = H })
  end
  local function arrow(name, size)
    local fig = decode(FIGURAS[name])
    local k = size / max(fig.xmax - fig.xmin, fig.ymax - fig.ymin)
    black.figure(fig, transform(0, cz, k, k, 0, (fig.xmin + fig.xmax) / 2, (fig.ymin + fig.ymax) / 2), L1, H)
  end
  local sym = p.Sinal
  local bw = D * 0.09
  if sym == "texto" then
    local unit = p.Unidade ~= ""
    local hv = D * (unit and 0.30 or 0.36)
    local y = unit and cz + D * 0.07 or cz
    text(black, p.Valor, fit(p.Valor, { x = 0, y = y, altura = hv, largura = hv * 0.6, espaco = hv * 0.05, z = L1, h = H }, ri * 1.5))
    if unit then
      local hu = D * 0.1
      text(black, p.Unidade, fit(p.Unidade, { x = 0, y = cz - D * 0.2, altura = hu, largura = hu * 0.7, espaco = hu * 0.05, z = L1, h = H }, ri * 1.2))
    end
  elseif sym == "estacionamento" then
    letter("E", D * 0.42)
  elseif sym == "proibido_estacionar" then
    letter("E", D * 0.42); bar(-45, bw)
  elseif sym == "proibido_parar" then
    letter("E", D * 0.42); bar(-45, bw); bar(45, bw)
  elseif sym == "proibido_esquerda" then
    arrow("seta_esquerda", D * 0.5); bar(-45, bw)
  elseif sym == "proibido_direita" then
    arrow("seta_direita", D * 0.5); bar(-45, bw)
  elseif sym == "proibido_retorno" then
    arrow("seta_retorno", D * 0.5); bar(-45, bw)
  elseif sym == "sentido_proibido" then
    red.figure(disc_figure(ri + 0.002, 72), transform(0, cz, 1, 1), L1, H)
    white.figure(poly_figure({ { -ri * 0.72, -D * 0.075 }, { ri * 0.72, -D * 0.075 }, { ri * 0.72, D * 0.075 }, { -ri * 0.72, D * 0.075 } }), transform(0, cz, 1, 1), L2, H)
  elseif sym == "sentido_frente" or sym == "sentido_direita" or sym == "sentido_esquerda" then
    local name = ({ sentido_frente = "seta_frente", sentido_direita = "seta_direita", sentido_esquerda = "seta_esquerda" })[sym]
    arrow(name, D * 0.56)
  end
  local out = {}
  add(out, black.piece({ name = "Símbolo" }), red.piece({ name = "Tarja", material = MAT.vermelha }), white.piece({ name = "Faixa branca", material = MAT.branca }))
  return out
end

--- placa-pare
local L1, H = 0.001, 0.0005

function geometry(p)
  local F = max(p.Largura, 0.2)
  local cz = p.AlturaLivre + F / 2
  local m = new_mesh("front")
  local h = F * 0.27
  text(m, p.Texto, fit(p.Texto, { x = 0, y = cz, altura = h, largura = h * 0.56, espaco = h * 0.06, z = L1, h = H }, F * 0.74))
  local piece = m.piece({ name = "Legenda" })
  return piece and { piece } or {}
end

--- placa-advertencia
local L1, H = 0.0015, 0.0005

function geometry(p)
  local G = max(p.Lado, 0.2) * sqrt(2) -- the diagonal
  local cz = p.AlturaLivre + G / 2
  local m = new_mesh("front")
  local T = transform(0, cz, 1, 1)
  local sym = p.Sinal
  local function box(x0, y0, x1, y1) m.figure(poly_figure({ { x0, y0 }, { x1, y0 }, { x1, y1 }, { x0, y1 } }), T, L1, H) end
  local function arrow(name, size)
    local fig = decode(FIGURAS[name])
    local k = size / max(fig.xmax - fig.xmin, fig.ymax - fig.ymin)
    m.figure(fig, transform(0, cz, k, k, 0, (fig.xmin + fig.xmax) / 2, (fig.ymin + fig.ymax) / 2), L1, H)
  end
  if sym == "texto" then
    local lines = {}
    for _, s in ipairs({ p.Linha1, p.Linha2 }) do if s ~= "" then lines[#lines + 1] = s end end
    if #lines == 1 then
      local h = G * 0.15
      text(m, lines[1], fit(lines[1], { x = 0, y = cz, altura = h, largura = h * 0.55, espaco = h * 0.05, z = L1, h = H }, G * 0.6))
    elseif #lines == 2 then
      local h = G * 0.12
      for i, s in ipairs(lines) do
        local y = cz + (i == 1 and 1 or -1) * h * 0.85
        text(m, s, fit(s, { x = 0, y = y, altura = h, largura = h * 0.55, espaco = h * 0.05, z = L1, h = H }, G * 0.42))
      end
    end
  elseif sym == "lombada" then
    local w, t, hb = G * 0.48, G * 0.045, G * 0.15
    local y0 = -G * 0.1
    box(-w / 2, y0 - t, w / 2, y0)
    local pts = {}
    local n = 24
    for i = 0, n do
      local a = math.pi * i / n
      pts[#pts + 1] = { hb * 1.15 * cos(a), y0 + hb * sin(a) }
    end
    m.figure(poly_figure(pts), T, L1, H)
  elseif sym == "curva_direita" then
    arrow("seta_direita", G * 0.42)
  elseif sym == "curva_esquerda" then
    arrow("seta_esquerda", G * 0.42)
  elseif sym == "cruzamento" then
    local a, b = G * 0.045, G * 0.25
    box(-a, -b, a, b); box(-b, -a, -a, a); box(a, -a, b, a)
  elseif sym == "duplo_sentido" then
    local fig = decode(FIGURAS.seta_frente)
    local k = G * 0.36 / 1000
    m.figure(fig, transform(-G * 0.07, cz, k, k, 0, 0, 500), L1, H)
    m.figure(fig, transform(G * 0.07, cz, k, k, 180, 0, 500), L1, H)
  end
  local piece = m.piece({ name = "Símbolo" })
  return piece and { piece } or {}
end

--- placa-estacionamento
local L1, H = 0.001, 0.0005

function geometry(p)
  local D = max(p.Diametro, 0.2)
  local hi, wi = max(p.AlturaInfo, 0.1), max(p.LarguraInfo, 0.2)
  local cz = p.AlturaLivre + hi + 0.05 + D / 2
  local m = new_mesh("front")
  text(m, "E", { x = 0, y = cz, altura = D * 0.42, largura = D * 0.26, z = L1, h = H })
  -- The additional information below: lines of text, and the symbol of access if chosen.
  local o = wi * 0.05 + 0.012 -- inside the black edge
  local x0, x1, y0, y1 = -wi / 2 + o, wi / 2 - o, p.AlturaLivre + o, p.AlturaLivre + hi - o
  if p.Simbolo == "cadeirante" then
    local fig = decode(FIGURAS.cadeirante)
    local s = (y1 - y0) * 0.86
    local k = s / max(fig.xmax - fig.xmin, fig.ymax - fig.ymin)
    m.figure(fig, transform(x0 + s / 2 + 0.01, (y0 + y1) / 2, k, k, 0, (fig.xmin + fig.xmax) / 2, (fig.ymin + fig.ymax) / 2), L1, H)
    x0 = x0 + s + 0.03
  end
  local lines = {}
  for _, s in ipairs({ p.Linha1, p.Linha2, p.Linha3 }) do if s ~= "" then lines[#lines + 1] = s end end
  local n = #lines
  if n > 0 then
    local h = min((y1 - y0) / (n + (n - 1) * 0.55), (y1 - y0) * 0.36)
    local total = n * h + (n - 1) * 0.55 * h
    for i, s in ipairs(lines) do
      local y = (y0 + y1) / 2 + total / 2 - h / 2 - (i - 1) * 1.55 * h
      text(m, s, fit(s, { x = (x0 + x1) / 2, y = y, altura = h, largura = h * 0.6, espaco = h * 0.06, z = L1, h = H }, x1 - x0))
    end
  end
  local piece = m.piece({ name = "Legenda" })
  return piece and { piece } or {}
end

--- placa-orientacao
local L1, H = 0.001, 0.0005
local ANGLES = { esquerda = 90, direita = -90, frente = 0, frente_esquerda = 45, frente_direita = -45 }

function geometry(p)
  local W, Hp = max(p.Largura, 0.3), max(p.Altura, 0.15)
  local o = min(W, Hp) * 0.04 + 0.01 -- inside the white edge
  local x0, x1, y0, y1 = -W / 2 + o, W / 2 - o, p.AlturaLivre + o, p.AlturaLivre + Hp - o
  local m = new_mesh("front")
  local out = {}
  local pad = (y1 - y0) * 0.1
  local ang = ANGLES[p.Seta]
  if ang then
    local s = min((y1 - y0) * 0.82, (x1 - x0) * 0.26)
    local k = s / 1000
    local right = ang < 0
    local cx = right and x1 - pad - s / 2 or x0 + pad + s / 2
    m.figure(decode(FIGURAS.seta_frente), transform(cx, (y0 + y1) / 2, k, k, ang, 0, 500), L1, H)
    if right then x1 = x1 - s - 2 * pad else x0 = x0 + s + 2 * pad end
  end
  local lines = {}
  for _, s in ipairs({ p.Linha1, p.Linha2, p.Linha3 }) do if s ~= "" then lines[#lines + 1] = s end end
  local n = #lines
  if n > 0 then
    local h = min((y1 - y0 - 2 * pad) / (n + (n - 1) * 0.5), (y1 - y0) * 0.34)
    local total = n * h + (n - 1) * 0.5 * h
    for i, s in ipairs(lines) do
      local y = (y0 + y1) / 2 + total / 2 - h / 2 - (i - 1) * 1.5 * h
      text(m, s, fit(s, { x = (x0 + x1) / 2, y = y, altura = h, largura = h * 0.62, espaco = h * 0.05, z = L1, h = H }, x1 - x0 - 2 * pad))
    end
  end
  add(out, m.piece({ name = "Legenda" }))
  -- The posts, behind the rails of the plate: one, or two for wide plates.
  local r = 0.0381
  local top = p.AlturaLivre + Hp - 0.04
  local xs = (W > 1.3) and { -W * 0.3, W * 0.3 } or { 0 }
  for _, x in ipairs(xs) do
    add(out, cylinder { x, 0.024 + r, 0, r, top, material = MAT.aco, name = "Poste" })
  end
  return out
end

--- placa-emergencia
local L1, H = 0.002, 0.0005
local ANGLES = { esquerda = 90, direita = -90, frente = 0, baixo = 180, frente_esquerda = 45, frente_direita = -45 }

function geometry(p)
  local W, Hp = max(p.Largura, 0.1), max(p.Altura, 0.05)
  local z0 = p.Elevacao
  local o = min(W, Hp) * 0.08
  local x0, x1, y0, y1 = -W / 2 + o, W / 2 - o, z0 + o, z0 + Hp - o
  local m = new_mesh("front")
  local ang = ANGLES[p.Seta]
  if ang then
    local s = min(y1 - y0, (x1 - x0) * 0.32)
    local k = s / 1000
    local right = ang < 0
    local cx = right and x1 - s / 2 or x0 + s / 2
    m.figure(decode(FIGURAS.seta_frente), transform(cx, (y0 + y1) / 2, k, k, ang, 0, 500), L1, H)
    if right then x1 = x1 - s - o else x0 = x0 + s + o end
  end
  local lines = {}
  for _, s in ipairs({ p.Linha1, p.Linha2 }) do if s ~= "" then lines[#lines + 1] = s end end
  local n = #lines
  if n > 0 then
    local h = min((y1 - y0) / (n + (n - 1) * 0.45), (y1 - y0) * 0.5)
    local total = n * h + (n - 1) * 0.45 * h
    for i, s in ipairs(lines) do
      local y = (y0 + y1) / 2 + total / 2 - h / 2 - (i - 1) * 1.45 * h
      text(m, s, fit(s, { x = (x0 + x1) / 2, y = y, altura = h, largura = h * 0.62, espaco = h * 0.06, z = L1, h = H }, x1 - x0))
    end
  end
  local piece = m.piece({ name = "Símbolo e texto" })
  return piece and { piece } or {}
end

--- placa-identificacao
local FACE, RELIEF, DOT = 0.003, 0.001, 0.0007
-- Braille cells (dots 1 to 6) of the Portuguese alphabet (Grafia Braille para a Língua Portuguesa).
local BRAILLE = {
  a = "1", b = "12", c = "14", d = "145", e = "15", f = "124", g = "1245", h = "125", i = "24", j = "245",
  k = "13", l = "123", m = "134", n = "1345", o = "135", p = "1234", q = "12345", r = "1235", s = "234", t = "2345",
  u = "136", v = "1236", w = "2456", x = "1346", y = "13456", z = "1356",
  [0xE1] = "12356", [0xE0] = "1246", [0xE2] = "16", [0xE3] = "345", [0xE9] = "123456", [0xEA] = "126",
  [0xED] = "34", [0xF3] = "346", [0xF4] = "1456", [0xF5] = "246", [0xFA] = "23456", [0xFC] = "1256", [0xE7] = "12346",
  ["."] = "3", [","] = "2", ["-"] = "36", [":"] = "25", [";"] = "23", ["!"] = "235", ["?"] = "26",
}
local DIGITS = { ["1"] = "1", ["2"] = "12", ["3"] = "14", ["4"] = "145", ["5"] = "15", ["6"] = "124", ["7"] = "1245", ["8"] = "125", ["9"] = "24", ["0"] = "245" }
local NUMBER_SIGN = "3456"

-- The cells of a text, lower-cased; numbers get the number sign.
local function braille_cells(s)
  local cells, in_number = {}, false
  for _, cp in ipairs(codepoints(s)) do
    if cp >= 0x41 and cp <= 0x5A then cp = cp + 32 end
    if cp >= 0xC0 and cp <= 0xDE and cp ~= 0xD7 then cp = cp + 32 end
    local ch = cp < 128 and string.char(cp) or nil
    if ch and DIGITS[ch] then
      if not in_number then cells[#cells + 1] = NUMBER_SIGN; in_number = true end
      cells[#cells + 1] = DIGITS[ch]
    else
      if cp ~= 46 and cp ~= 44 then in_number = false end
      if cp == 32 then cells[#cells + 1] = ""
      else
        local cell = (ch and BRAILLE[ch]) or BRAILLE[cp]
        if cell then cells[#cells + 1] = cell end
      end
    end
  end
  return cells
end

function geometry(p)
  local W, Hp = max(p.Largura, 0.05), max(p.Altura, 0.03)
  local z0 = p.Elevacao
  local m = new_mesh("front")
  local h = max(p.AlturaTexto, 0.01)
  local lines = {}
  for _, s in ipairs({ p.Linha1, p.Linha2 }) do if s ~= "" then lines[#lines + 1] = s end end
  local braille = p.Braille and #lines > 0
  local n = #lines
  local block = n * h + (n - 1) * 0.5 * h + (braille and (0.008 + n * 0.010) or 0)
  local top = z0 + Hp / 2 + block / 2
  for i, s in ipairs(lines) do
    local y = top - h / 2 - (i - 1) * 1.5 * h
    text(m, s, fit(s, { x = 0, y = y, altura = h, largura = h * 0.62, espaco = h * 0.08, z = FACE, h = RELIEF }, W * 0.86))
  end
  if braille then
    -- Cells 6.2 mm apart, dots 2.5 mm apart and 1.5 mm across (ABNT NBR 9050), each line centred.
    local dot = disc_figure(0.00075, 10)
    local pos = { ["1"] = { 0, 0 }, ["2"] = { 0, -1 }, ["3"] = { 0, -2 }, ["4"] = { 1, 0 }, ["5"] = { 1, -1 }, ["6"] = { 1, -2 } }
    local ytop = top - n * h - (n - 1) * 0.5 * h - 0.008
    for i, s in ipairs(lines) do
      local cells = braille_cells(s)
      local width = (#cells - 1) * 0.0062 + 0.0025
      local x = -width / 2
      local y = ytop - (i - 1) * 0.010
      for _, cell in ipairs(cells) do
        for d in cell:gmatch("%d") do
          local q = pos[d]
          m.figure(dot, transform(x + q[1] * 0.0025, y + q[2] * 0.0025, 1, 1), FACE, DOT)
        end
        x = x + 0.0062
      end
    end
  end
  local piece = m.piece({ name = "Texto em relevo e braille" })
  return piece and { piece } or {}
end

--- numero-predial
local FACE, RELIEF = 0.004, 0.002

function geometry(p)
  local W, Hp = max(p.Largura, 0.05), max(p.Altura, 0.03)
  local z0 = p.Elevacao
  local m = new_mesh("front")
  local small = p.Logradouro ~= ""
  local hn = Hp * (small and 0.5 or 0.62)
  local yn = z0 + Hp / 2 + (small and Hp * 0.1 or 0)
  text(m, p.Numero, fit(p.Numero, { x = 0, y = yn, altura = hn, largura = hn * 0.62, espaco = hn * 0.06, z = FACE, h = RELIEF }, W * 0.84))
  if small then
    local hs = Hp * 0.11
    text(m, p.Logradouro, fit(p.Logradouro, { x = 0, y = z0 + Hp * 0.17, altura = hs, largura = hs * 0.6, espaco = hs * 0.06, z = FACE, h = RELIEF }, W * 0.84))
  end
  local piece = m.piece({ name = "Números" })
  return piece and { piece } or {}
end
