# 3D CraftHouse

[![Validate](https://github.com/francisreboucas/constructcraft-components/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/francisreboucas/constructcraft-components/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC_BY_4.0-lightgrey.svg)](LICENSE)

3D CraftHouse is the free library of parametric components for [ConstructCraft](https://github.com/francisreboucas/constructcraft): furniture, casework, plumbing fixtures, electrical devices, lighting, planting and outdoor floor markings, ready to load into any project.

[Português (Brasil)](README.pt-BR.md) · [Viewer](https://3dcrafthouse.constructcraft.net/) · [Catalog](CATALOG.md) · [Contributing](CONTRIBUTING.md)

## Browse online

The [online viewer](https://3dcrafthouse.constructcraft.net/) shows every component in 3D with its dimensions, types and MEP data, and a link to download its `.ccomp` file.

![The library placed in a project: furniture, casework, plumbing fixtures, electrical devices and lighting](docs/vitrine-3d.png)

## Using a component

1. Download a `.ccomp` file from [`components/`](components) (browse them in the [catalog](CATALOG.md)), or download the whole library as a ZIP from the [latest release](https://github.com/francisreboucas/constructcraft-components/releases/latest).
2. In ConstructCraft, load it: the component and all its types join the project, with any materials the project lacks.
   From the command line or a macro:

   ```sh
   ccad -p house.ccad --save run component_load path=components/plumbing/pia-cozinha.ccomp
   ```

3. Place it with the component tool, or `component_place type="Pia cozinha 150 cm" position=[2,3]`.

Each file holds one component with several types (sizes). Types share the geometry and differ in parameter values (`Largura`, `Profundidade`, `Altura`…), which you can change after loading.

## What is in it

| Folder | Contents |
|---|---|
| [`furniture`](components/furniture) | Tables (dining and coffee), chairs, armchairs, beds, bunk beds, sofas, desks, nightstands, TV racks, split air conditioners, kitchen and laundry appliances (refrigerator, range, cooktop, oven, microwave, dishwasher, range hoods, small appliances, dryer), shower enclosures, towel rails |
| [`casework`](components/casework) | Wardrobes, chests of drawers, kitchen base and wall cabinets, shelving, mirror cabinets |
| [`plumbing`](components/plumbing) | Toilets, basins, sinks, showers, laundry tubs, washing machines, bathtubs, urinals, bidets, vanity units, bidet sprayers, gas water heaters, water purifiers, water tanks, inspection and grease boxes |
| [`electrical`](components/electrical) | General and dedicated outlets, shower points, switches, distribution boards, data/TV points |
| [`lighting`](components/lighting) | Ceiling, pendant, recessed, linear and wall lights, ceiling fans with light |
| [`planting`](components/planting) | Trees, conifers, palms, shrubs and potted plants for landscaping |
| [`doors`](components/doors) | Single and double swing, pivot, folding, glass and sliding doors, glazed sliding doors, garage doors |
| [`windows`](components/windows) | Sliding (also with shutters), casement, awning, hopper and fixed windows |
| [`vehicles`](components/vehicles) | A custom (cruiser) motorcycle, with the handlebar that steers and the side stand that folds |
| [`site`](components/site) | Outdoor floor elements: parking spaces (also angled, accessible and motorcycle), PARE legends with stop lines, floor legends, speed limits, lane arrows, pedestrian crossings, give-way triangles, bicycle and access symbols, hatched no-parking areas, speed humps, wheel stops and road studs. Every painted word (a space's number, PARE, ESCOLA, 40 km/h…) is a text parameter each placed element can change. Also park benches, litter and recycling bins, bike racks, bollards, picnic tables, street lights, swings, pergolas and tactile paving (NBR 16537) |
| [`signage`](components/signage) | Signs with editable text: regulatory (speed limit, no parking, no turns…), STOP, give way, warning, regulated parking with additional information, green guide and blue services signs, emergency exit and fire equipment signs (NBR 13434), tactile room signs with braille (NBR 9050) and house numbers |
| [`fire`](components/fire) | Fire protection: portable extinguishers (dry powder, CO2, water) on a wall bracket or a floor stand with the optional floor marking, hose cabinets with the angle valve, rolled hose and nozzle, a sidewalk fire department connection and a pillar hydrant, pendent sprinklers, smoke and heat detectors, manual call points, sounder beacons, an alarm control panel and emergency lights. The words on them (INCÊNDIO on the cabinet's glass and the connection's cover, the call point's and the panel's labels, FOGO on the beacon) are editable per element |

Plumbing fixtures carry their drainage fixture units (NBR 8160) and supply weights (NBR 5626), and electrical devices their device kind and load in VA (NBR 5410), so ConstructCraft sizes pipes and circuits with them. Names and descriptions are in Brazilian Portuguese, following the standards they cite.

## How the library is built

Components are written as readable JSON in [`sources/`](sources), in the shape of the engine's `component_create` command. [`tools/build.py`](tools/build.py) has ConstructCraft's own command line (`ccad`) create each component and save it as `.ccomp`, then loads every file back into a new project to validate it, and writes [`catalog.json`](catalog.json) and [`CATALOG.md`](CATALOG.md), with each component's author taken from [`authors.json`](authors.json). CI runs the same check on every pull request with the pinned ConstructCraft release.

```sh
python tools/build.py --ccad path/to/ccad          # build, validate, update the catalog
python tools/build.py --ccad path/to/ccad --check  # verify only (CI)
```

A `.ccomp` saved from the app (`component_save`) can also be added directly under `components/`, without a source; it is validated and cataloged the same way.

Each component has a 360x240 thumbnail in [`thumbnails/`](thumbnails), drawn by `ccad` from its first type, and `catalog.json` points to it in `thumbnail`. After building, run `python tools/thumbnails.py --ccad path/to/ccad` (it draws only the new and changed components) and commit the PNG, `thumbnails/manifest.json` and the catalog.

The planting sources are generated: [`tools/vegetation.py`](tools/vegetation.py) grows each species as a mesh (branches by space colonization, foliage clumps, palm fronds) and writes `sources/planting/`. Edit the generator and run it before `build.py`, not the JSON.

The outdoor floor sources are generated too: [`tools/site.py`](tools/site.py) writes `sources/site/` from the Lua scripts in [`tools/site/`](tools/site). Painted text is drawn from a glyph table of IBM Plex Sans Condensed Bold (SIL OFL 1.1), triangulated by `tools/site/fonte.py`, so the text stays editable in ConstructCraft. A `.ccomp` keeps only numbers per type: texts and choices belong to the component and are changed per placed element.

## Compatibility

`.ccomp` format version 1, built with ConstructCraft 0.12.0. The detailed components (pieces shown by detail level, Blend and Sweep shapes), which are all but the planting ones, need ConstructCraft 0.12.0; the planting components load in ConstructCraft 0.6.0 and later. The motorcycle's steered front end and side stand, and the outdoor floor markings, are pieces scripted in Lua; the web viewer shows them as ConstructCraft baked them ([`tools/scripted.py`](tools/scripted.py)).

## License

The components are licensed under [Creative Commons Attribution 4.0](LICENSE): use them in any project, commercial or not; if you redistribute the library or derived components, credit "ConstructCraft Components contributors". The viewer code in [`viewer/`](viewer) is licensed under [GPL-3.0-or-later](viewer/LICENSE).
