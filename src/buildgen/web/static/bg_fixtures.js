// Port of buildgen/layout/fixtures.py: furniture and fittings placed against room walls. The 3D model does not
// draw them, but they draw random numbers, so the port keeps the generator in step with Python (and the plan shows them).
const SIZES = {
  sink: [0.6, 0.5], cooker: [0.6, 0.6], fridge: [0.6, 0.6], worktop: [2.0, 0.6], toilet: [0.4, 0.7], bath: [0.7, 1.7],
  shower: [0.9, 0.9], basin: [0.5, 0.4], fireplace: [1.2, 0.4], sofa: [2.0, 0.9], dining_table: [1.4, 0.9],
  desk: [1.2, 0.6], bed_single: [0.9, 2.0], bed_double: [1.4, 2.0], wardrobe: [1.2, 0.6], washing_machine: [0.6, 0.6],
  boiler: [0.5, 0.5],
};
const ROOM_FIXTURES = {
  kitchen: ['sink', 'cooker', 'fridge', 'worktop'], scullery: ['sink', 'washing_machine'], wc: ['toilet', 'basin'],
  bathroom: ['toilet', 'bath', 'basin'], parlour: ['fireplace', 'sofa'], drawing_room: ['fireplace', 'sofa'],
  dining_room: ['dining_table', 'fireplace'], study: ['desk', 'fireplace'], library: ['desk', 'fireplace'],
  master_bedroom: ['bed_double', 'wardrobe'], bedroom: ['bed_single', 'wardrobe'], dressing_room: ['wardrobe'],
  nursery: ['bed_single'], servants_quarters: ['bed_single'],
};
const WALL_PREF = {
  toilet: 'north', bath: 'east', basin: 'north', sink: 'north', cooker: 'east', fridge: 'west', worktop: 'south',
  fireplace: 'north', wardrobe: 'west', bed_single: 'east', bed_double: 'north',
};

function placeAgainstWall(wall, minx, miny, maxx, maxy, fw, fd, rng) {
  const margin = 0.15, cx = (minx + maxx) / 2, cy = (miny + maxy) / 2, jitter = 0.3;
  let x, y, rot;
  if (wall === 'north') { x = cx + rng.uniform(-jitter, jitter); y = maxy - fd / 2 - margin; rot = 0; }
  else if (wall === 'south') { x = cx + rng.uniform(-jitter, jitter); y = miny + fd / 2 + margin; rot = 180; }
  else if (wall === 'east') { x = maxx - fd / 2 - margin; y = cy + rng.uniform(-jitter, jitter); rot = 90; }
  else if (wall === 'west') { x = minx + fd / 2 + margin; y = cy + rng.uniform(-jitter, jitter); rot = 270; }
  else { x = cx + rng.uniform(-0.5, 0.5); y = cy + rng.uniform(-0.5, 0.5); rot = 0; }
  x = Math.max(minx + fw / 2 + margin, Math.min(x, maxx - fw / 2 - margin));
  y = Math.max(miny + fd / 2 + margin, Math.min(y, maxy - fd / 2 - margin));
  return [x, y, rot];
}

const overlapsAny = (r, others, m = 0.1) => others.some(o => r[0] - m < o[2] && r[2] + m > o[0] && r[1] - m < o[3] && r[3] + m > o[1]);

export function placeFixturesInRoom(bounds, roomType, rng) {
  const types = ROOM_FIXTURES[roomType] || [];
  const [minx, miny, maxx, maxy] = bounds, rw = maxx - minx, rh = maxy - miny;
  const placed = [], occupied = [];
  for (const ft of types) {
    const [fw, fd] = SIZES[ft] || [0.5, 0.5];
    if (fw > rw - 0.2 || fd > rh - 0.2) continue;
    let wall = WALL_PREF[ft] || '';
    let [x, y, rot] = placeAgainstWall(wall, minx, miny, maxx, maxy, fw, fd, rng);
    let rect = [x - fw / 2, y - fd / 2, x + fw / 2, y + fd / 2];
    if (overlapsAny(rect, occupied)) {
      let found = false;
      for (const alt of ['north', 'south', 'east', 'west']) {
        if (alt === wall) continue;
        [x, y, rot] = placeAgainstWall(alt, minx, miny, maxx, maxy, fw, fd, rng);
        rect = [x - fw / 2, y - fd / 2, x + fw / 2, y + fd / 2];
        if (!overlapsAny(rect, occupied)) { wall = alt; found = true; break; }
      }
      if (!found) continue;
    }
    occupied.push(rect);
    placed.push({ type: ft, x, y, width: fw, depth: fd, rotation: rot, against_wall: wall });
  }
  return placed;
}
