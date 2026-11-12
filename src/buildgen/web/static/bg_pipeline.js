// End-to-end generator in the browser: port of buildgen/pipeline.py (Pipeline.generate). templates are the YAML
// templates as JSON ({name: template}); styleOverrides replace StyleParams fields of the georgian style.
import { STYLES, generateProgram, isGridTemplate } from './bg_program.js';
import { layoutProgram } from './bg_layout.js';
import { generateFromGrid } from './bg_grid.js';
import { buildGeometry } from './bg_geometry.js';

export function generateBuilding(templates, type, seed = 0, styleOverrides = {}, styleName = 'georgian') {
  const tmpl = templates[type];
  if (!tmpl) throw new Error(`No template for '${type}'. Available: ${Object.keys(templates).join(', ')}`);
  if (!STYLES[styleName]) throw new Error(`Unknown style '${styleName}'. Available: ${Object.keys(STYLES).join(', ')}`);
  const style = { ...STYLES[styleName], ...styleOverrides };
  let plans, program = null;
  if (isGridTemplate(tmpl)) plans = generateFromGrid(tmpl, seed).plans;
  else { program = generateProgram(tmpl, type, styleName, seed); plans = layoutProgram(program); }
  const geo = buildGeometry(plans, style);
  return { building_type: type, style_name: styleName, seed, style, program, plans, ...geo };
}

export function meshCounts(nodes) {
  let v = 0, f = 0;
  for (const n of nodes) { v += n.mesh.vertices.length; f += n.mesh.faces.length; }
  return { nodes: nodes.length, vertices: v, faces: f };
}
