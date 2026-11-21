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
| [`furniture`](components/furniture) | Tables (dining and coffee), chairs, armchairs, beds, bunk beds, sofas, desks, nightstands, office furniture (workstations with privacy screens, meeting tables, swivel chairs, mobile pedestals, steel filing cabinets and cupboards, partition panels), TV racks, split and ceiling cassette air conditioners, bathroom extract fans, kitchen and laundry appliances (refrigerator, range, cooktop, oven, microwave, dishwasher, range hoods, small appliances, dryer), shower enclosures, towel rails, bathroom accessories (toilet roll holder, hooks, soap dispenser, glass shelf); commercial and institutional furniture: a reception counter with an accessible section, a supermarket checkout, shop gondolas, steel shelving, restaurant tables with chairs, bar stools, waiting room benches, steel lockers, school desks with chairs (NBR 14006 sizes), whiteboards and a hospital bed |
| [`casework`](components/casework) | Wardrobes, chests of drawers, kitchen base and wall cabinets, shelving, mirror cabinets |
| [`plumbing`](components/plumbing) | Toilets, basins (also a vessel basin on a floating countertop), sinks, kitchen mixers with a pull-out spray, shower sets with a rain head and a hand shower, showers, laundry tubs, washing machines, bathtubs, urinals, bidets, vanity units, bidet sprayers, gas water heaters, water purifiers, water tanks, inspection and grease boxes, solar water-heating collectors and hot-water tanks, a water meter assembly in its box, an LPG cylinder shelter and an accessible drinking fountain |
| [`electrical`](components/electrical) | General and dedicated outlets, shower points, switches, distribution boards, data/TV points, an EV wall charger (7.4 kW dedicated outlet), solar PV modules on a tilted mount and a string inverter, the utility service entrance (steel pole, meter box, grounding), a CCTV camera, a video door phone and a ceiling occupancy sensor |
| [`lighting`](components/lighting) | Ceiling, pendant, recessed, linear and wall lights, ceiling fans with light; outdoor lighting: garden bollards, spike spotlights aimed at 30°, 60° or 85°, LED floodlights, a bulkhead wall light, in-ground uplights, garden lamp posts (lantern or globe) and recessed step lights |
| [`planting`](components/planting) | Trees, conifers, palms, shrubs, ornamental grasses (purple fountain grass, Dietes, agapanthus), ground covers, lawns, planting beds (with a curb, raised, round) and potted plants and planters, drawn as light silhouettes at coarse detail and as detailed plants (branches, single leaves, flowers, palm leaflets) at medium and fine detail |
| [`doors`](components/doors) | Single and double swing, pivot, folding, glass and sliding doors, glazed sliding doors, garage doors |
| [`windows`](components/windows) | Sliding (also with shutters), casement, awning, hopper and fixed windows |
| [`vehicles`](components/vehicles) | A compact hatchback, a mid-size sedan, a compact SUV with roof rails and a double-cab pickup with a tonneau cover, of generic design and real sizes, for parking and garage studies (lofted bodies with wheel arches, glass, lamps, mirrors, alloy wheels and an interior); an urban bicycle; a custom (cruiser) motorcycle, with the handlebar that steers and the side stand that folds |
| [`site`](components/site) | Outdoor floor elements: parking spaces (also angled, accessible and motorcycle), PARE legends with stop lines, floor legends, speed limits, lane arrows, pedestrian crossings, give-way triangles, bicycle and access symbols, hatched no-parking areas, speed humps, wheel stops and road studs. Every painted word (a space's number, PARE, ESCOLA, 40 km/h…) is a text parameter each placed element can change. Also park benches, litter and recycling bins, bike racks, bollards, picnic tables, street lights, swings, pergolas and tactile paving (NBR 16537) |
| [`signage`](components/signage) | Signs with editable text: regulatory (speed limit, no parking, no turns…), STOP, give way, warning, regulated parking with additional information, green guide and blue services signs, emergency exit and fire equipment signs (NBR 13434), tactile room signs with braille (NBR 9050) and house numbers |
| [`fire`](components/fire) | Fire protection: portable extinguishers (dry powder, CO2, water) on a wall bracket or a floor stand with the optional floor marking, hose cabinets with the angle valve, rolled hose and nozzle, a sidewalk fire department connection and a pillar hydrant, pendent sprinklers, smoke and heat detectors, manual call points, sounder beacons, an alarm control panel and emergency lights. The words on them (INCÊNDIO on the cabinet's glass and the connection's cover, the call point's and the panel's labels, FOGO on the beacon) are editable per element |
| [`people`](components/people) | Fourteen low-poly people standing (men in suits, blazers and shirts, women in skirts, suits and trousers), from the Citizen NPC Pack by 00amza (CC BY 4.0, see below); and generic human figures for scale: two people standing, a person walking, a person sitting (for seats at 45 cm), a child and a wheelchair user in a folding wheelchair with the NBR 9050 reference module (0.80 x 1.20 m) drawn in plan; smooth featureless mannequins (one continuous surface, the joints blended) in varied skin tones and clothes |

Plumbing fixtures carry their drainage fixture units (NBR 8160) and supply weights (NBR 5626), and electrical devices their device kind and load in VA (NBR 5410), so ConstructCraft sizes pipes and circuits with them. Names and descriptions are in Brazilian Portuguese, following the standards they cite.

## How the library is built

Components are written as readable JSON in [`sources/`](sources), in the shape of the engine's `component_create` command. [`tools/build.py`](tools/build.py) has ConstructCraft's own command line (`ccad`) create each component and save it as `.ccomp`, then loads every file back into a new project to validate it, and writes [`catalog.json`](catalog.json) and [`CATALOG.md`](CATALOG.md), with each component's author taken from [`authors.json`](authors.json). CI runs the same check on every pull request with the pinned ConstructCraft release.

```sh
python tools/build.py --ccad path/to/ccad          # build, validate, update the catalog
python tools/build.py --ccad path/to/ccad --check  # verify only (CI)
```

A `.ccomp` saved from the app (`component_save`) can also be added directly under `components/`, without a source; it is validated and cataloged the same way.

Each component has a 360x240 thumbnail in [`thumbnails/`](thumbnails), drawn by `ccad` from its first type, and `catalog.json` points to it in `thumbnail`. After building, run `python tools/thumbnails.py --ccad path/to/ccad` (it draws only the new and changed components) and commit the PNG, `thumbnails/manifest.json` and the catalog.

The planting sources are generated: [`tools/vegetation.py`](tools/vegetation.py) grows each species as a mesh and writes `sources/planting/`. The coarse level is a light silhouette from [`tools/vegetation_coarse.py`](tools/vegetation_coarse.py) (a trunk forking into limbs, a crown of leaf clusters in two tones, serrated palm fronds); [`tools/vegetation_detail.py`](tools/vegetation_detail.py) draws the detailed plant (branches by space colonization, leaf sprays, flowers, palm leaflets, needle tufts, grass blades). Edit the generator and run it before `build.py`, not the JSON.

The outdoor floor sources are generated too: [`tools/site.py`](tools/site.py) writes `sources/site/` from the Lua scripts in [`tools/site/`](tools/site). Painted text is drawn from a glyph table of IBM Plex Sans Condensed Bold (SIL OFL 1.1), triangulated by `tools/site/fonte.py`, so the text stays editable in ConstructCraft. A `.ccomp` keeps only numbers per type: texts and choices belong to the component and are changed per placed element.

## Compatibility

`.ccomp` format version 1, built with ConstructCraft 0.12.0. Every component needs ConstructCraft 0.12.0 or later: they show different pieces at each detail level and use Blend and Sweep shapes. The motorcycle's steered front end and side stand, and the outdoor floor markings, are pieces scripted in Lua; the web viewer shows them as ConstructCraft baked them ([`tools/scripted.py`](tools/scripted.py)).

## Third-party models

The fourteen `people/cidadao-*` components come from ["Citizen NPC Pack 1 Character Lowpoly Mobile"](https://sketchfab.com/3d-models/citizen-npc-pack-1-character-lowpoly-mobile-711ee48bcf80426bbf98ad01e1b9da1c) by [00amza](https://sketchfab.com/00amza), licensed under [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). Changes: turned to ConstructCraft's frame, the arms lowered from the A pose, and the photo textures reduced to flat colours ([`tools/pessoas_glb.py`](tools/pessoas_glb.py)).

## License

The components are licensed under [Creative Commons Attribution 4.0](LICENSE): use them in any project, commercial or not; if you redistribute the library or derived components, credit "ConstructCraft Components contributors". The viewer code in [`viewer/`](viewer) is licensed under [GPL-3.0-or-later](viewer/LICENSE).
