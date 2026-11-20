# 3D CraftHouse

[![Validate](https://github.com/francisreboucas/constructcraft-components/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/francisreboucas/constructcraft-components/actions/workflows/validate.yml)
[![Licença: CC BY 4.0](https://img.shields.io/badge/licen%C3%A7a-CC_BY_4.0-lightgrey.svg)](LICENSE)

O 3D CraftHouse é a biblioteca gratuita de componentes paramétricos para o [ConstructCraft](https://github.com/francisreboucas/constructcraft): mobiliário, marcenaria, louças e metais, dispositivos elétricos, iluminação e paisagismo, prontos para carregar em qualquer projeto.

[English](README.md) · [Visualizador](https://3dcrafthouse.constructcraft.net/) · [Catálogo](CATALOG.md) · [Como contribuir](CONTRIBUTING.md)

## Veja no navegador

O [visualizador online](https://3dcrafthouse.constructcraft.net/) mostra cada componente em 3D, com as medidas, os tipos e os dados de instalações, e um link para baixar o arquivo `.ccomp`.

![A biblioteca inserida num projeto: mobiliário, marcenaria, louças, dispositivos elétricos e luminárias](docs/vitrine-3d.png)

## Usando um componente

1. Baixe um arquivo `.ccomp` de [`components/`](components) (veja todos no [catálogo](CATALOG.md)), ou a biblioteca inteira em ZIP pelo [release mais recente](https://github.com/francisreboucas/constructcraft-components/releases/latest).
2. No ConstructCraft, carregue o arquivo: o componente e todos os seus tipos entram no projeto, junto com os materiais que faltarem.
   Pela linha de comando ou numa macro:

   ```sh
   ccad -p casa.ccad --save run component_load path=components/plumbing/pia-cozinha.ccomp
   ```

3. Insira com a ferramenta de componente, ou `component_place type="Pia cozinha 150 cm" position=[2,3]`.

Cada arquivo traz um componente com vários tipos (tamanhos). Os tipos compartilham a geometria e diferem nos valores dos parâmetros (`Largura`, `Profundidade`, `Altura`…), que você pode alterar depois de carregar.

## O que tem

| Pasta | Conteúdo |
|---|---|
| [`furniture`](components/furniture) | Mesas (de jantar e de centro), cadeiras, poltronas, camas, beliches, sofás, escrivaninhas, criados-mudos, mobiliário de escritório (estações de trabalho com divisória, mesas de reunião, cadeiras giratórias, gaveteiros volantes, arquivos e armários de aço, painéis divisórios), racks de TV, ar-condicionado split, eletrodomésticos de cozinha e lavanderia (geladeira, fogão, cooktop, forno, micro-ondas, lava-louças, coifa e depurador, eletroportáteis, secadora), box de vidro, toalheiros, acessórios de banheiro (papeleira, cabide, dispenser de sabonete, prateleira de vidro) |
| [`casework`](components/casework) | Guarda-roupas, cômodas, balcões e aéreos de cozinha, estantes, espelheiras |
| [`plumbing`](components/plumbing) | Bacias, lavatórios (também com cuba de apoio em bancada suspensa), pias, misturadores gourmet de cozinha, conjuntos de chuveiro com ducha de teto e ducha manual, chuveiros, tanques, máquinas de lavar, banheiras, mictórios, bidês, gabinetes com cuba, duchas higiênicas, aquecedores a gás, purificadores de água, caixas d'água, caixas de inspeção e de gordura |
| [`electrical`](components/electrical) | TUGs, TUEs, pontos de chuveiro, interruptores, quadros de distribuição, pontos de dados e TV |
| [`lighting`](components/lighting) | Plafons, pendentes, spots, luminárias lineares, arandelas e ventiladores de teto com luminária |
| [`planting`](components/planting) | Árvores, coníferas, palmeiras, arbustos e vasos com planta para paisagismo |
| [`doors`](components/doors) | Portas de abrir de uma e duas folhas, pivotante, camarão, de vidro temperado, de correr simples e dupla, porta-janela de correr e portão basculante |
| [`windows`](components/windows) | Janelas de correr (também com veneziana), de abrir, maxim-ar, basculante e fixa |
| [`vehicles`](components/vehicles) | Carro hatch compacto, sedã médio, SUV compacto com rack de teto e caminhonete cabine dupla com capota marítima, de desenho genérico e medidas reais, para estudos de vagas e garagens (carroceria contínua com caixas de roda, vidros, faróis, retrovisores, rodas de liga e interior); bicicleta urbana; motocicleta custom (cruiser), com guidão que esterça e descanso lateral que recolhe |
| [`site`](components/site) | Elementos de piso externo: vagas de estacionamento (também oblíquas, PcD e de moto), legenda PARE com linha de retenção, legendas no piso, velocidade máxima, setas direcionais, faixas de pedestres, Dê a preferência, símbolos de bicicleta e de acesso, áreas zebradas, lombadas, batentes de roda e tachas refletivas. Toda palavra pintada (número da vaga, PARE, ESCOLA, 40 km/h…) é um parâmetro de texto que cada elemento posicionado pode mudar. Também bancos de praça, lixeiras e coletores de recicláveis, bicicletários, frades e balizadores, mesas de piquenique, postes de iluminação, balanços, pergolados e piso tátil (NBR 16537) |
| [`signage`](components/signage) | Placas com texto editável: regulamentação (velocidade, proibido estacionar, proibido virar…), PARE, Dê a preferência, advertência, estacionamento regulamentado com informação complementar, orientação (verde) e serviços (azul), saída de emergência e equipamentos de incêndio (NBR 13434), identificação tátil com braille (NBR 9050) e numeração predial |
| [`fire`](components/fire) | Proteção contra incêndio: extintores portáteis (pó, CO2, água) no suporte de parede ou de piso, com a sinalização de piso opcional, abrigos de mangueira com registro angular, mangueira aduchada e esguicho, registro de recalque de passeio e hidrante de coluna, sprinklers pendentes, detectores de fumaça e de temperatura, acionadores manuais, sirenes audiovisuais, central de alarme e luminárias de emergência. Os textos (INCÊNDIO no vidro do abrigo e na tampa do recalque, os do acionador e da central, FOGO na sirene) são editáveis em cada elemento |

As louças trazem as unidades Hunter de contribuição (NBR 8160) e os pesos relativos (NBR 5626), e os dispositivos elétricos o tipo e a potência em VA (NBR 5410), para o ConstructCraft dimensionar tubulações e circuitos.

## Como a biblioteca é gerada

Os componentes são escritos em JSON legível em [`sources/`](sources), no formato do comando `component_create` do motor. O [`tools/build.py`](tools/build.py) usa a própria linha de comando do ConstructCraft (`ccad`) para criar cada componente e salvá-lo como `.ccomp`; depois carrega cada arquivo num projeto novo para validá-lo e escreve o [`catalog.json`](catalog.json) e o [`CATALOG.md`](CATALOG.md), com o autor de cada componente tirado do [`authors.json`](authors.json). A CI roda a mesma verificação em cada pull request, com a versão fixada do ConstructCraft.

```sh
python tools/build.py --ccad caminho/do/ccad          # gera, valida e atualiza o catálogo
python tools/build.py --ccad caminho/do/ccad --check  # só verifica (CI)
```

Um `.ccomp` salvo pelo próprio app (`component_save`) também pode ser adicionado direto em `components/`, sem fonte JSON; ele é validado e catalogado do mesmo jeito.

Cada componente tem uma miniatura de 360x240 em [`thumbnails/`](thumbnails), desenhada pelo `ccad` a partir do primeiro tipo, e o `catalog.json` aponta para ela em `thumbnail`. Depois do build, rode `python tools/thumbnails.py --ccad caminho/do/ccad` (ele só desenha os componentes novos e alterados) e inclua no commit o PNG, o `thumbnails/manifest.json` e o catálogo.

As fontes de paisagismo são geradas: [`tools/vegetation.py`](tools/vegetation.py) cria cada espécie como malha (galhos por colonização do espaço, massas de folhas, frondes de palmeira) e escreve `sources/planting/`. Altere o gerador e rode-o antes do `build.py`, não o JSON.

As fontes de área externa também são geradas: [`tools/site.py`](tools/site.py) escreve `sources/site/` a partir dos scripts Lua de [`tools/site/`](tools/site). O texto pintado vem de uma tabela de glifos da IBM Plex Sans Condensed Bold (SIL OFL 1.1), triangulada por `tools/site/fonte.py`, e por isso continua editável no ConstructCraft. O `.ccomp` guarda só números por tipo: textos e escolhas são do componente e mudam em cada elemento posicionado.

## Compatibilidade

Formato `.ccomp` versão 1, gerado com o ConstructCraft 0.12.0. Os componentes detalhados (peças por nível de detalhe, formas Blend e Sweep), que são todos menos os de paisagismo, exigem o ConstructCraft 0.12.0; os de paisagismo abrem no ConstructCraft 0.6.0 ou mais recente. A dianteira esterçável e o descanso lateral da motocicleta, e as marcações de piso externo, são peças em script Lua; o visualizador web as mostra como o ConstructCraft as gerou ([`tools/scripted.py`](tools/scripted.py)).

## Licença

Os componentes estão sob a licença [Creative Commons Atribuição 4.0](LICENSE): use em qualquer projeto, comercial ou não; se redistribuir a biblioteca ou componentes derivados, dê o crédito a "ConstructCraft Components contributors". O código do visualizador, em [`viewer/`](viewer), está sob a licença [GPL-3.0 ou posterior](viewer/LICENSE).
