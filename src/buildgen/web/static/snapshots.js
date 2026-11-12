// Render buildings to PNG data URLs with one shared off-screen WebGL viewer (for the home page and gallery).
import { createViewer } from './gl_view.js';
import { generate } from './building_data.js';

export function snapshots(data, items, w = 480, h = 360) {
  const c = document.createElement('canvas');
  c.style.cssText = `position:fixed;left:-9999px;top:0;width:${w}px;height:${h}px`;
  document.body.appendChild(c);
  const v = createViewer(c);
  try {
    return items.map(({ type, seed, ov }) => {
      v.setScene(generate(data, type, seed, ov || {}).nodes);
      return v.snapshot();
    });
  } finally { v.destroy(); c.remove(); }
}
