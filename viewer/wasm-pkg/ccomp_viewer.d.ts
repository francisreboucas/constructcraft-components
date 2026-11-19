/* tslint:disable */
/* eslint-disable */

/** A parameter of the component with the value it has in the type shown. */
export interface ComponentParam {
    name: string;
    /** "Length" (meters), "Angle" (degrees), "Number", "Boolean", "Text", "Choice" or "Material". */
    kind: string;
    /** A number for numeric kinds (booleans are 1 or 0); a string for text, choice (its key) and material kinds. */
    value: number | string;
    /** Elements may override the value. */
    instance: boolean;
}

/** A type of the component: its name, description and parameter values. */
export interface ComponentType {
    name: string;
    description: string;
    values: Record<string, number>;
}

/** Where a pipe or conduit connects, in the component's frame (the values of the type shown). */
export interface ComponentConnector {
    name: string;
    /** The system kind, e.g. "ColdWater", "Sanitary", "Power". */
    system: string;
    /** Meters. */
    position: [number, number, number];
    /** Unit vector of the way runs leave. */
    direction: [number, number, number];
    /** Outside diameter in meters, or null when unset. */
    diameter: number | null;
}

/** An axis-aligned box, meters. */
export interface ComponentBounds {
    min: [number, number, number];
    max: [number, number, number];
}

/** A piece that failed to resolve. */
export interface ComponentError {
    /** Index of the piece in the definition. */
    item: number;
    name: string;
    message: string;
}

/** One solid piece, tessellated. */
export interface Part {
    name: string;
    /** The material's name ("" for none). */
    material: string;
    /** sRGB 0-255: the material's shading color, grey when the material is missing or empty. */
    color: [number, number, number];
    /** 0 (opaque) to 1 (invisible), from the material. */
    transparency: number;
    /** Non-indexed triangles, x, y, z per vertex, counter-clockwise seen from outside. */
    positions: Float32Array;
    /** One unit normal per vertex: smooth across the facets of curved surfaces, flat elsewhere. */
    normals: Float32Array;
    /**
     * The piece's outline as line segments, x, y, z per end: the face boundaries the engine's views
     * draw. The pieces a face was split into read as one face and the facets of a curved surface
     * have no lines between them.
     */
    edges: Float32Array;
}

/** A component file, resolved with the values of one of its types. */
export interface Component {
    /** Index in `types` of the type shown: the one the parameter values, connectors, bounds and parts are of. */
    type_index: number;
    /** The component's name. */
    name: string;
    /** Its kind: "Furniture", "Casework", "Plumbing", "Lighting", "Electrical", "Generic", "Door", "Window", "Niche", "TitleBlock" or "Detail". */
    kind: string;
    /** What wrote the file, e.g. "ConstructCraft 0.12.0". */
    generator: string;
    params: ComponentParam[];
    types: ComponentType[];
    /** Plumbing fixture or electrical device data as the file holds it, e.g. { Fixture: { drain_units, supply_weight, hot_water } }. */
    mep: Record<string, any> | null;
    connectors: ComponentConnector[];
    /** The box of all parts, or null when there are none. */
    bounds: ComponentBounds | null;
    /** The 3D pieces shown at the fine detail level, voids cut out. 2D components (title blocks, detail components) have none. */
    parts: Part[];
    errors: ComponentError[];
}



/**
 * Parse the text of a `.ccomp` file and tessellate its 3D pieces with the
 * values of the type at `type_index` of its types (the first when left out
 * or out of range). Throws an `Error` with the engine's message when the
 * file does not parse.
 */
export function load_component(text: string, type_index?: number | null): Component;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
    readonly memory: WebAssembly.Memory;
    readonly load_component: (a: number, b: number, c: number) => [number, number, number];
    readonly __wbindgen_malloc: (a: number, b: number) => number;
    readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
    readonly __wbindgen_free: (a: number, b: number, c: number) => void;
    readonly __wbindgen_exn_store: (a: number) => void;
    readonly __externref_table_alloc: () => number;
    readonly __wbindgen_externrefs: WebAssembly.Table;
    readonly __externref_table_dealloc: (a: number) => void;
    readonly __wbindgen_start: () => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;

/**
 * Instantiates the given `module`, which can either be bytes or
 * a precompiled `WebAssembly.Module`.
 *
 * @param {{ module: SyncInitInput }} module - Passing `SyncInitInput` directly is deprecated.
 *
 * @returns {InitOutput}
 */
export function initSync(module: { module: SyncInitInput } | SyncInitInput): InitOutput;

/**
 * If `module_or_path` is {RequestInfo} or {URL}, makes a request and
 * for everything else, calls `WebAssembly.instantiate` directly.
 *
 * @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
 *
 * @returns {Promise<InitOutput>}
 */
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;
