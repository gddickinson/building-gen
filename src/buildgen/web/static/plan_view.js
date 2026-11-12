// 2D floor plan of one storey on a canvas: rooms coloured by function, walls, doors, windows and fixtures as the
// generator placed them. Street front (plan y = 0) at the bottom, as in buildgen's matplotlib plans.
const TYPE_COLOURS = {
  entrance_hall: '#4b5a7a', hallway: '#4b5a7a', landing: '#4b5a7a', stairwell: '#6b5a3a', parlour: '#3d6b55',
  drawing_room: '#3d6b55', dining_room: '#4d6b3a', kitchen: '#7a5a3a', scullery: '#6e5236', pantry: '#5e4a36',
  wc: '#3a5f7a', bathroom: '#3a5f7a', bedroom: '#5a4a7a', master_bedroom: '#62487e', dressing_room: '#55456e',
  nursery: '#6a4a72', study: '#3f6470', library: '#3f6470', servants_quarters: '#58506a', storage: '#4a4a4a',
  cellar: '#3e3e46', attic: '#4a4652', shop_floor: '#6a6a3a', workshop: '#6a5a3a', office: '#3f6470',
};
export const roomColour = t => TYPE_COLOURS[t] || '#4a5068';
const label = s => s.replace(/_/g, ' ');

export function drawPlan(canvas, plan, opts = {}) {
  const dpr = Math.min(2, window.devicePixelRatio || 1), W = canvas.clientWidth || 400, H = canvas.clientHeight || 300;
  canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#05060c'; ctx.fillRect(0, 0, W, H);
  if (!plan) return;
  const [x0, y0, x1, y1] = plan.footprint, pad = 26;
  const s = Math.min((W - 2 * pad) / (x1 - x0), (H - 2 * pad) / (y1 - y0));
  const ox = (W - (x1 - x0) * s) / 2, oy = (H + (y1 - y0) * s) / 2;
  const X = x => ox + (x - x0) * s, Y = y => oy - (y - y0) * s;

  for (const r of plan.rooms) {
    const [a, b, c, d] = r.b;
    ctx.fillStyle = roomColour(r.room_type); ctx.globalAlpha = 0.55;
    ctx.fillRect(X(a), Y(d), (c - a) * s, (d - b) * s);
    ctx.globalAlpha = 1;
  }
  if (opts.fixtures !== false) {
    ctx.strokeStyle = 'rgba(232,241,255,.55)'; ctx.lineWidth = 1;
    for (const r of plan.rooms) for (const f of r.fixtures) {
      const rot = f.rotation === 90 || f.rotation === 270, w = rot ? f.depth : f.width, h = rot ? f.width : f.depth;
      ctx.strokeRect(X(f.x - w / 2), Y(f.y + h / 2), w * s, h * s);
    }
  }
  for (const w of plan.walls) {
    ctx.strokeStyle = w.wall_type === 'exterior' ? '#e8f1ff' : '#94a3c6';
    ctx.lineWidth = Math.max(1.5, w.thickness * s);
    ctx.beginPath(); ctx.moveTo(X(w.start[0]), Y(w.start[1])); ctx.lineTo(X(w.end[0]), Y(w.end[1])); ctx.stroke();
  }
  for (const r of plan.rooms) for (const o of r.openings) {
    const [px, py] = o.position, col = o.type === 'window' ? '#4fc3ff' : o.type === 'front_door' ? '#ffd23f' : '#ff9f4f';
    ctx.fillStyle = col;
    ctx.beginPath(); ctx.arc(X(px), Y(py), Math.max(3, Math.min(6, o.width * s * 0.18)), 0, 2 * Math.PI); ctx.fill();
  }
  ctx.font = '11px ui-monospace, Menlo, monospace'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  for (const r of plan.rooms) {
    const [a, b, c, d] = r.b, cx = X((a + c) / 2), cy = Y((b + d) / 2), wpx = (c - a) * s;
    if (wpx < 30) continue;
    ctx.fillStyle = '#e8f1ff';
    let t = label(r.name);
    while (t.length > 3 && ctx.measureText(t).width > wpx - 6) t = t.slice(0, -2) + '…';
    ctx.fillText(t, cx, cy - 6);
    ctx.fillStyle = '#94a3c6';
    ctx.fillText(`${((c - a) * (d - b)).toFixed(1)} m²`, cx, cy + 8);
  }
  ctx.fillStyle = '#94a3c6'; ctx.textAlign = 'left';
  ctx.fillText(`street front ↓   ${(x1 - x0).toFixed(2)} × ${(y1 - y0).toFixed(2)} m`, 8, H - 9);
}
