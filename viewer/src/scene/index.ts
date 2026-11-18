// Public API of the 3D scene.
export { buildComponentObject, ComponentObject, type BuildOptions } from './component-object';
export { DimensionSet, formatMetres } from './dimensions';
export { GroundGrid } from './grid';
export {
  renderThumbnail,
  disposeThumbnailRenderer,
  thumbnailRendererInfo,
  ThumbnailError,
  type ThumbnailOptions,
} from './thumbnail';
export { Viewport, type ComponentDisplayOptions, type SetViewOptions } from './viewport';
export { VIEW_NAMES, type ViewName } from './views';
