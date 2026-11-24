/**
 * SignBridge AI — Client-Side Kinematic Inference & Gesture Engine
 * 
 * Provides ultra-low-latency (0ms, 60 FPS) local ASL sign classification,
 * kinematic rule disambiguation, dynamic word tracking (HELLO, HI, YES, NO, etc.),
 * temporal smoothing with double-letter support, and sentence formation.
 * 
 * Completely immune to cloud cold starts, network dropouts, or WebSocket delays.
 */

// Canonical 3D Joint Templates for all 26 letters + Controls + Direct Word Signs
const FINGER_BASES = {
  WRIST: [0.0, 0.0, 0.0],
  THUMB_CMC: [-0.15, -0.16, 0.0],
  THUMB_MCP: [-0.26, -0.30, 0.02],
  THUMB_IP: [-0.34, -0.42, 0.04],
  INDEX_MCP: [-0.14, -0.50, 0.0],
  MIDDLE_MCP: [0.0, -0.54, 0.0],
  RING_MCP: [0.12, -0.50, 0.0],
  PINKY_MCP: [0.22, -0.44, 0.0]
};

const EXT_INDEX = [[-0.14, -0.68, 0.0], [-0.14, -0.82, 0.0], [-0.14, -0.96, 0.0]];
const EXT_MIDDLE = [[0.0, -0.72, 0.0], [0.0, -0.86, 0.0], [0.0, -1.0, 0.0]];
const EXT_RING = [[0.12, -0.68, 0.0], [0.12, -0.82, 0.0], [0.12, -0.95, 0.0]];
const EXT_PINKY = [[0.22, -0.60, 0.0], [0.22, -0.72, 0.0], [0.22, -0.85, 0.0]];

const FOLD_INDEX = [[-0.14, -0.55, 0.06], [-0.14, -0.45, 0.12], [-0.14, -0.35, 0.10]];
const FOLD_MIDDLE = [[0.0, -0.58, 0.06], [0.0, -0.48, 0.12], [0.0, -0.38, 0.10]];
const FOLD_RING = [[0.12, -0.55, 0.06], [0.12, -0.45, 0.12], [0.12, -0.35, 0.10]];
const FOLD_PINKY = [[0.22, -0.48, 0.06], [0.22, -0.40, 0.12], [0.22, -0.32, 0.10]];

const CURVE_INDEX = [[-0.14, -0.62, 0.10], [-0.14, -0.60, 0.20], [-0.14, -0.52, 0.22]];
const CURVE_MIDDLE = [[0.0, -0.66, 0.10], [0.0, -0.64, 0.20], [0.0, -0.56, 0.22]];
const CURVE_RING = [[0.12, -0.62, 0.10], [0.12, -0.60, 0.20], [0.12, -0.52, 0.22]];
const CURVE_PINKY = [[0.22, -0.54, 0.10], [0.22, -0.52, 0.20], [0.22, -0.45, 0.22]];

function buildTemplate(thumb, idx, mid, rng, pnk) {
  const pts = new Float32Array(63);
  const arr = [
    FINGER_BASES.WRIST,
    FINGER_BASES.THUMB_CMC,
    FINGER_BASES.THUMB_MCP,
    FINGER_BASES.THUMB_IP,
    thumb,
    FINGER_BASES.INDEX_MCP,
    idx[0], idx[1], idx[2],
    FINGER_BASES.MIDDLE_MCP,
    mid[0], mid[1], mid[2],
    FINGER_BASES.RING_MCP,
    rng[0], rng[1], rng[2],
    FINGER_BASES.PINKY_MCP,
    pnk[0], pnk[1], pnk[2]
  ];

  let maxD = 0;
  for (let i = 0; i < 21; i++) {
    const x = arr[i][0], y = arr[i][1], z = arr[i][2];
    const d = Math.sqrt(x * x + y * y + z * z);
    if (d > maxD) maxD = d;
  }

  for (let i = 0; i < 21; i++) {
    pts[i * 3] = maxD > 0 ? arr[i][0] / maxD : 0;
    pts[i * 3 + 1] = maxD > 0 ? arr[i][1] / maxD : 0;
    pts[i * 3 + 2] = maxD > 0 ? arr[i][2] / maxD : 0;
  }
  return pts;
}

export const TEMPLATES = {
  A: buildTemplate([-0.25, -0.58, 0.06], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  B: buildTemplate([0.0, -0.32, 0.08], EXT_INDEX, EXT_MIDDLE, EXT_RING, EXT_PINKY),
  C: buildTemplate([-0.28, -0.42, 0.18], CURVE_INDEX, CURVE_MIDDLE, CURVE_RING, CURVE_PINKY),
  D: buildTemplate([-0.06, -0.42, 0.08], EXT_INDEX, [[-0.04, -0.54, 0.08], [-0.05, -0.48, 0.10], [-0.06, -0.42, 0.08]], FOLD_RING, FOLD_PINKY),
  E: buildTemplate([-0.04, -0.28, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  F: buildTemplate([-0.14, -0.50, 0.10], [[-0.14, -0.60, 0.06], [-0.14, -0.55, 0.10], [-0.14, -0.50, 0.10]], EXT_MIDDLE, EXT_RING, EXT_PINKY),
  G: buildTemplate([-0.35, -0.48, 0.0], [[-0.28, -0.50, 0.0], [-0.42, -0.50, 0.0], [-0.56, -0.50, 0.0]], FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  H: buildTemplate([-0.15, -0.36, 0.05], [[-0.28, -0.50, 0.0], [-0.42, -0.50, 0.0], [-0.56, -0.50, 0.0]], [[-0.26, -0.54, 0.0], [-0.40, -0.54, 0.0], [-0.54, -0.54, 0.0]], FOLD_RING, FOLD_PINKY),
  I: buildTemplate([0.0, -0.38, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, EXT_PINKY),
  J: buildTemplate([0.0, -0.38, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, EXT_PINKY),
  K: buildTemplate([-0.08, -0.52, 0.06], EXT_INDEX, [[-0.04, -0.70, 0.08], [-0.04, -0.84, 0.12], [-0.04, -0.96, 0.14]], FOLD_RING, FOLD_PINKY),
  L: buildTemplate([-0.55, -0.32, 0.0], EXT_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  M: buildTemplate([0.06, -0.34, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  N: buildTemplate([-0.02, -0.34, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  O: buildTemplate([-0.08, -0.46, 0.15], [[-0.12, -0.58, 0.10], [-0.10, -0.52, 0.14], [-0.08, -0.46, 0.15]], [[-0.02, -0.60, 0.10], [-0.04, -0.54, 0.14], [-0.08, -0.46, 0.15]], [[0.08, -0.58, 0.10], [0.04, -0.52, 0.14], [-0.06, -0.46, 0.15]], [[0.16, -0.52, 0.10], [0.10, -0.48, 0.14], [-0.05, -0.46, 0.15]]),
  P: buildTemplate([-0.08, -0.38, 0.06], [[-0.14, -0.38, 0.0], [-0.14, -0.24, 0.0], [-0.14, -0.10, 0.0]], [[0.0, -0.40, 0.06], [0.0, -0.26, 0.08], [0.0, -0.12, 0.10]], FOLD_RING, FOLD_PINKY),
  Q: buildTemplate([-0.25, -0.20, 0.0], [[-0.14, -0.38, 0.0], [-0.14, -0.24, 0.0], [-0.14, -0.10, 0.0]], FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  R: buildTemplate([0.0, -0.38, 0.08], [[-0.10, -0.68, 0.0], [-0.06, -0.82, 0.02], [-0.02, -0.96, 0.04]], [[-0.06, -0.72, 0.0], [-0.10, -0.86, -0.02], [-0.14, -1.0, -0.04]], FOLD_RING, FOLD_PINKY),
  S: buildTemplate([0.02, -0.45, 0.12], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  T: buildTemplate([-0.08, -0.46, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  U: buildTemplate([0.0, -0.38, 0.08], [[-0.08, -0.68, 0.0], [-0.06, -0.82, 0.0], [-0.04, -0.96, 0.0]], [[0.02, -0.72, 0.0], [0.03, -0.86, 0.0], [0.04, -1.0, 0.0]], FOLD_RING, FOLD_PINKY),
  V: buildTemplate([0.0, -0.35, 0.08], [[-0.20, -0.68, 0.0], [-0.26, -0.82, 0.0], [-0.32, -0.96, 0.0]], [[0.06, -0.72, 0.0], [0.10, -0.86, 0.0], [0.14, -1.0, 0.0]], FOLD_RING, FOLD_PINKY),
  W: buildTemplate([0.10, -0.35, 0.08], [[-0.20, -0.68, 0.0], [-0.26, -0.82, 0.0], [-0.32, -0.96, 0.0]], EXT_MIDDLE, [[0.18, -0.68, 0.0], [0.22, -0.82, 0.0], [0.26, -0.95, 0.0]], FOLD_PINKY),
  X: buildTemplate([-0.20, -0.38, 0.08], [[-0.14, -0.64, 0.06], [-0.14, -0.56, 0.14], [-0.14, -0.46, 0.10]], FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  Y: buildTemplate([-0.55, -0.35, 0.0], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, [[0.30, -0.60, 0.0], [0.42, -0.72, 0.0], [0.54, -0.85, 0.0]]),
  Z: buildTemplate([0.0, -0.38, 0.08], [[-0.14, -0.68, 0.0], [-0.14, -0.82, 0.0], [-0.14, -0.96, 0.0]], FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  SPACE: buildTemplate([-0.42, -0.42, 0.0], [[-0.20, -0.68, 0.0], [-0.26, -0.82, 0.0], [-0.30, -0.96, 0.0]], EXT_MIDDLE, [[0.18, -0.68, 0.0], [0.22, -0.82, 0.0], [0.26, -0.95, 0.0]], [[0.30, -0.60, 0.0], [0.38, -0.72, 0.0], [0.45, -0.85, 0.0]]),
  DEL: buildTemplate([-0.55, -0.20, 0.0], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY),
  I_LOVE_YOU: buildTemplate([-0.55, -0.35, 0.0], EXT_INDEX, FOLD_MIDDLE, FOLD_RING, [[0.28, -0.60, 0.0], [0.38, -0.72, 0.0], [0.48, -0.85, 0.0]])
};

export const CLASSES = Object.keys(TEMPLATES);

/**
 * Normalizes 21 3D landmarks relative to wrist origin and scales to unit size.
 */
export function normalizeLandmarks(landmarks, handedness = 'Right') {
  if (!landmarks || landmarks.length !== 21) return new Float32Array(63);

  const pts = new Float32Array(63);
  const isLeft = handedness && handedness.toLowerCase() === 'left';
  const wx = landmarks[0].x;
  const wy = landmarks[0].y;
  const wz = landmarks[0].z || 0.0;

  let maxD = 0;
  for (let i = 0; i < 21; i++) {
    let x = landmarks[i].x - wx;
    if (isLeft) x = -x;
    const y = landmarks[i].y - wy;
    const z = (landmarks[i].z || 0.0) - wz;
    const d = Math.sqrt(x * x + y * y + z * z);
    if (d > maxD) maxD = d;
    pts[i * 3] = x;
    pts[i * 3 + 1] = y;
    pts[i * 3 + 2] = z;
  }

  if (maxD > 1e-6) {
    for (let i = 0; i < 63; i++) pts[i] /= maxD;
  }
  return pts;
}

/**
 * Computes anatomical kinematic extension and posture flags.
 */
export function extractGeometricFeatures(landmarks) {
  if (!landmarks || landmarks.length !== 21) return {};

  const dist = (i, j) => {
    const dx = landmarks[i].x - landmarks[j].x;
    const dy = landmarks[i].y - landmarks[j].y;
    const dz = (landmarks[i].z || 0) - (landmarks[j].z || 0);
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  };

  const d8_0 = dist(8, 0);
  const d6_0 = dist(6, 0);
  const d12_0 = dist(12, 0);
  const d10_0 = dist(10, 0);
  const d16_0 = dist(16, 0);
  const d14_0 = dist(14, 0);
  const d20_0 = dist(20, 0);
  const d18_0 = dist(18, 0);

  // In screen coords, smaller y is towards top of screen (extended upwards)
  const is_index_extended = landmarks[8].y < landmarks[6].y && d8_0 > d6_0 * 1.10;
  const is_middle_extended = landmarks[12].y < landmarks[10].y && d12_0 > d10_0 * 1.10;
  const is_ring_extended = landmarks[16].y < landmarks[14].y && d16_0 > d14_0 * 1.10;
  const is_pinky_extended = landmarks[20].y < landmarks[18].y && d20_0 > d18_0 * 1.10;

  const d4_17 = dist(4, 17);
  const d2_17 = dist(2, 17);
  const d4_2 = dist(4, 2);
  const is_thumb_extended = d4_17 > d2_17 * 1.15 || d4_2 > 0.35;

  const ext_count = (is_index_extended ? 1 : 0) + (is_middle_extended ? 1 : 0) +
                    (is_ring_extended ? 1 : 0) + (is_pinky_extended ? 1 : 0);
  const total_extended = ext_count + (is_thumb_extended ? 1 : 0);

  const thumb_index_dist = dist(4, 8);
  const index_middle_dist = dist(8, 12);
  const thumb_pinky_dist = dist(4, 20);

  const is_fist = ext_count === 0;
  const is_index_hooked = landmarks[6].y < landmarks[5].y && landmarks[8].y > landmarks[6].y + 0.02 &&
                          !is_middle_extended && !is_ring_extended && !is_pinky_extended;

  const is_crossed = is_index_extended && is_middle_extended && !is_ring_extended && !is_pinky_extended &&
                     ((landmarks[8].x > landmarks[12].x) || (index_middle_dist < 0.06 && dist(5, 9) > 0.08));

  const is_two_fingers = is_index_extended && is_middle_extended && !is_ring_extended && !is_pinky_extended;
  const is_spread_v = is_two_fingers && index_middle_dist > 0.12 && !is_crossed;
  const is_closed_u = is_two_fingers && index_middle_dist <= 0.09 && !is_crossed;

  const is_three_w = is_index_extended && is_middle_extended && is_ring_extended && !is_pinky_extended;
  const is_l_shape = is_index_extended && !is_middle_extended && !is_ring_extended && !is_pinky_extended &&
                     is_thumb_extended && thumb_index_dist > 0.38 && landmarks[4].x < landmarks[2].x - 0.08;

  const is_y_shape = is_thumb_extended && is_pinky_extended && !is_index_extended && !is_middle_extended &&
                     !is_ring_extended && thumb_pinky_dist > 0.50;

  const is_ily_shape = is_thumb_extended && is_index_extended && is_pinky_extended &&
                       !is_middle_extended && !is_ring_extended && thumb_pinky_dist > 0.45;

  const is_ok_shape = thumb_index_dist < 0.13 && is_middle_extended && is_ring_extended && is_pinky_extended;

  const thumb_up_beside_index = is_fist && (landmarks[4].y < landmarks[2].y) && (landmarks[4].x <= landmarks[5].x + 0.02);
  const thumb_across_front = is_fist && (landmarks[4].x > landmarks[5].x) && (landmarks[4].y > landmarks[5].y - 0.02);
  const thumb_under_fingertips = is_fist && landmarks[4].y >= Math.min(landmarks[8].y, landmarks[12].y) - 0.04;
  const thumb_between_index_middle = is_fist && (landmarks[5].x <= landmarks[4].x && landmarks[4].x <= landmarks[9].x + 0.04);
  const thumb_under_three = is_fist && landmarks[4].x > landmarks[9].x;
  const thumb_under_two = is_fist && landmarks[5].x <= landmarks[4].x && landmarks[4].x <= landmarks[9].x;

  return {
    is_index_extended,
    is_middle_extended,
    is_ring_extended,
    is_pinky_extended,
    is_thumb_extended,
    ext_count,
    total_extended,
    thumb_index_dist,
    index_middle_dist,
    thumb_pinky_dist,
    is_fist,
    is_index_hooked,
    is_crossed,
    is_spread_v,
    is_closed_u,
    is_three_w,
    is_l_shape,
    is_y_shape,
    is_ily_shape,
    is_ok_shape,
    thumb_up_beside_index,
    thumb_across_front,
    thumb_under_fingertips,
    thumb_between_index_middle,
    thumb_under_three,
    thumb_under_two
  };
}

/**
 * Fast client-side kinematic classifier matching against canonical ASL poses with rule boosts.
 */
export function classifySign(normVector, geom) {
  if (!normVector || normVector.length !== 63) {
    return { label: 'UNKNOWN', confidence: 0, top3: [], is_unknown: true };
  }

  let normA = 0;
  for (let i = 0; i < 63; i++) normA += normVector[i] * normVector[i];
  normA = Math.sqrt(normA);

  const scores = {};

  for (const char of CLASSES) {
    const tmpl = TEMPLATES[char];
    let dot = 0;
    let normB = 0;
    let eucSq = 0;

    for (let i = 0; i < 63; i++) {
      const a = normVector[i];
      const b = tmpl[i];
      dot += a * b;
      normB += b * b;
      const diff = a - b;
      eucSq += diff * diff;
    }
    normB = Math.sqrt(normB);
    const cosSim = dot / (normA * normB + 1e-8);
    const eucDist = Math.sqrt(eucSq);

    scores[char] = 0.60 * cosSim + 0.40 * (1.0 / (1.0 + eucDist));
  }

  // Kinematic Rule Boosts
  if (geom.is_ily_shape) {
    scores['I_LOVE_YOU'] = (scores['I_LOVE_YOU'] || 0) + 0.70;
    scores['Y'] = (scores['Y'] || 0) + 0.30;
  }
  if (geom.is_ok_shape) {
    scores['F'] = (scores['F'] || 0) + 0.65;
  }
  if (geom.is_spread_v) {
    scores['V'] = (scores['V'] || 0) + 0.65;
  }
  if (geom.is_closed_u) {
    scores['U'] = (scores['U'] || 0) + 0.65;
  }
  if (geom.is_crossed) {
    scores['R'] = (scores['R'] || 0) + 0.70;
  }
  if (geom.is_index_hooked) {
    scores['X'] = (scores['X'] || 0) + 0.70;
  }
  if (geom.is_l_shape) {
    scores['L'] = (scores['L'] || 0) + 0.75;
  }
  if (geom.is_y_shape && !geom.is_index_extended) {
    scores['Y'] = (scores['Y'] || 0) + 0.75;
  }
  if (geom.is_three_w) {
    scores['W'] = (scores['W'] || 0) + 0.70;
  }
  if (geom.is_fist) {
    if (geom.thumb_up_beside_index) scores['A'] = (scores['A'] || 0) + 0.60;
    else if (geom.thumb_across_front) scores['S'] = (scores['S'] || 0) + 0.60;
    else if (geom.thumb_under_fingertips) scores['E'] = (scores['E'] || 0) + 0.55;
    else if (geom.thumb_between_index_middle) scores['T'] = (scores['T'] || 0) + 0.55;
    else if (geom.thumb_under_three) scores['M'] = (scores['M'] || 0) + 0.50;
    else if (geom.thumb_under_two) scores['N'] = (scores['N'] || 0) + 0.50;
    else scores['A'] = (scores['A'] || 0) + 0.30;
  }
  if (geom.is_index_extended && !geom.is_middle_extended && !geom.is_ring_extended && !geom.is_pinky_extended) {
    if (!geom.is_thumb_extended || geom.thumb_index_dist < 0.25) {
      scores['D'] = (scores['D'] || 0) + 0.55;
    }
  }
  if (geom.is_pinky_extended && !geom.is_index_extended && !geom.is_middle_extended && !geom.is_ring_extended) {
    if (!geom.is_thumb_extended) scores['I'] = (scores['I'] || 0) + 0.65;
  }
  if (geom.ext_count === 4 && !geom.is_thumb_extended) {
    scores['B'] = (scores['B'] || 0) + 0.65;
  }
  if (geom.total_extended === 5 && geom.index_middle_dist > 0.12) {
    scores['SPACE'] = (scores['SPACE'] || 0) + 0.65;
  }

  // Softmax calibration
  const temp = 0.040;
  let maxScore = -Infinity;
  for (const c of CLASSES) {
    if (scores[c] > maxScore) maxScore = scores[c];
  }

  const expVals = [];
  let sumExp = 0;
  for (const c of CLASSES) {
    const ev = Math.exp((scores[c] - maxScore) / temp);
    expVals.push({ label: c, exp: ev });
    sumExp += ev;
  }

  expVals.sort((a, b) => b.exp - a.exp);
  const top3 = expVals.slice(0, 3).map(item => ({
    label: item.label,
    confidence: Math.round((item.exp / sumExp) * 100) / 100
  }));

  const bestLabel = top3[0].label;
  const bestConf = top3[0].confidence;
  const isUnknown = bestConf < 0.50;

  return {
    label: isUnknown ? 'UNKNOWN' : bestLabel,
    confidence: bestConf,
    top3,
    is_unknown: isUnknown
  };
}

/**
 * Tracks 20-frame motion trajectories in screen-space for dynamic words.
 */
export class ClientDynamicTracker {
  constructor(bufferSize = 20) {
    this.bufferSize = bufferSize;
    this.palmHistory = [];
    this.cooldown = 0;
  }

  addFrame(rawLandmarks, geom) {
    if (this.cooldown > 0) this.cooldown--;
    if (!rawLandmarks || rawLandmarks.length !== 21) return null;

    const cx = (rawLandmarks[0].x + rawLandmarks[5].x + rawLandmarks[17].x) / 3.0;
    const cy = (rawLandmarks[0].y + rawLandmarks[5].y + rawLandmarks[17].y) / 3.0;
    const cz = ((rawLandmarks[0].z || 0) + (rawLandmarks[5].z || 0) + (rawLandmarks[17].z || 0)) / 3.0;

    // Joint 4 is thumb tip, joint 8 is index tip
    const thumbIdxDist = Math.hypot(rawLandmarks[4].x - rawLandmarks[8].x, rawLandmarks[4].y - rawLandmarks[8].y);

    this.palmHistory.push({ 
      cx, cy, cz, 
      thumbIdxDist,
      ext_count: geom.ext_count || 0, 
      is_fist: !!geom.is_fist, 
      is_ok: !!geom.is_ok_shape,
      geom 
    });
    if (this.palmHistory.length > this.bufferSize) {
      this.palmHistory.shift();
    }

    if (this.palmHistory.length < 10 || this.cooldown > 0) return null;

    const n = this.palmHistory.length;
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    let sumX = 0, sumY = 0;
    const dx = [];
    const dy = [];

    for (let i = 0; i < n; i++) {
      const p = this.palmHistory[i];
      if (p.cx < minX) minX = p.cx;
      if (p.cx > maxX) maxX = p.cx;
      if (p.cy < minY) minY = p.cy;
      if (p.cy > maxY) maxY = p.cy;
      sumX += p.cx;
      sumY += p.cy;
      if (i > 0) {
        dx.push(p.cx - this.palmHistory[i - 1].cx);
        dy.push(p.cy - this.palmHistory[i - 1].cy);
      }
    }

    const xSpan = maxX - minX;
    const ySpan = maxY - minY;
    const meanX = sumX / n;
    const meanY = sumY / n;

    let varX = 0, varY = 0;
    for (let i = 0; i < n; i++) {
      varX += (this.palmHistory[i].cx - meanX) ** 2;
      varY += (this.palmHistory[i].cy - meanY) ** 2;
    }
    const stdX = Math.sqrt(varX / n);
    const stdY = Math.sqrt(varY / n);

    // Direction zero crossings
    let zx = 0;
    for (let i = 1; i < dx.length; i++) {
      if ((dx[i] >= 0 && dx[i - 1] < 0) || (dx[i] < 0 && dx[i - 1] >= 0)) zx++;
    }
    let zy = 0;
    for (let i = 1; i < dy.length; i++) {
      if ((dy[i] >= 0 && dy[i - 1] < 0) || (dy[i] < 0 && dy[i - 1] >= 0)) zy++;
    }

    const first = this.palmHistory[0];
    const latest = this.palmHistory[n - 1];

    // 1. Waving gesture -> "HELLO" / "HI"
    if (zx >= 2 && xSpan > 0.035 && latest.ext_count >= 2) {
      this.cooldown = 20;
      return { word: xSpan > 0.05 ? 'HELLO' : 'HI', confidence: 0.95 };
    }

    // 2. Nodding fist gesture -> "YES"
    if (zy >= 2 && ySpan > 0.025 && (latest.is_fist || latest.ext_count <= 1)) {
      this.cooldown = 20;
      return { word: 'YES', confidence: 0.93 };
    }

    // 3. Snapping fingers closed onto thumb -> "NO"
    const snapStart = (this.palmHistory[0].thumbIdxDist + this.palmHistory[1].thumbIdxDist) / 2;
    const snapEnd = (latest.thumbIdxDist + this.palmHistory[n - 2].thumbIdxDist) / 2;
    if (snapStart > 0.14 && snapEnd < 0.08 && (snapStart - snapEnd > 0.06)) {
      this.cooldown = 20;
      return { word: 'NO', confidence: 0.91 };
    }

    // 4. Circular chest rub motion -> "PLEASE"
    if (latest.ext_count >= 3 && zx >= 1 && zy >= 1 && stdX > 0.012 && stdY > 0.012) {
      const ratio = stdX / (stdY + 1e-6);
      if (ratio > 0.4 && ratio < 2.5) {
        this.cooldown = 25;
        return { word: 'PLEASE', confidence: 0.90 };
      }
    }

    // 5. Flat hand outward/downward from chin -> "THANK YOU"
    if (latest.ext_count >= 3 && ySpan > 0.030 && latest.cy > first.cy + 0.025) {
      this.cooldown = 25;
      return { word: 'THANK YOU', confidence: 0.88 };
    }

    // 6. Upward thumbs up -> "HELP"
    if ((latest.is_fist || (latest.geom && latest.geom.thumb_up_beside_index)) && ySpan > 0.030 && (first.cy - latest.cy > 0.025)) {
      this.cooldown = 20;
      return { word: 'HELP', confidence: 0.92 };
    }

    return null;
  }

  reset() {
    this.palmHistory = [];
    this.cooldown = 0;
  }
}

/**
 * Temporal smoothing with hysteresis and double-letter support.
 */
export class ClientTemporalSmoother {
  constructor(windowSize = 5, minConsecutive = 4) {
    this.windowSize = windowSize;
    this.minConsecutive = minConsecutive;
    this.history = [];
    this.candidateLabel = null;
    this.candidateCount = 0;
    this.lastStableLabel = null;
  }

  process(label, confidence) {
    const isUnknown = confidence < 0.50 || label === 'UNKNOWN' || label === 'NONE';
    const eff = isUnknown ? 'UNKNOWN' : label;

    this.history.push(eff);
    if (this.history.length > this.windowSize) this.history.shift();

    if (eff === this.candidateLabel) {
      this.candidateCount++;
    } else {
      this.candidateLabel = eff;
      this.candidateCount = 1;
    }

    let isNewToken = false;
    if (this.candidateCount >= this.minConsecutive) {
      if (this.candidateLabel !== 'UNKNOWN') {
        if (this.candidateLabel !== this.lastStableLabel) {
          this.lastStableLabel = this.candidateLabel;
          isNewToken = true;
        }
      } else {
        // Reset when hand relaxes so repeating letters (LL in HELLO, ALL) can trigger
        this.lastStableLabel = null;
      }
    }

    // Majority vote in window
    const counts = {};
    for (const h of this.history) counts[h] = (counts[h] || 0) + 1;
    let maj = eff;
    let maxC = 0;
    for (const k in counts) {
      if (counts[k] > maxC) {
        maxC = counts[k];
        maj = k;
      }
    }

    return {
      stabilizedLabel: maj,
      activeStableLabel: this.lastStableLabel,
      isNewToken
    };
  }

  reset() {
    this.history = [];
    this.candidateLabel = null;
    this.candidateCount = 0;
    this.lastStableLabel = null;
  }
}

/**
 * Vocabulary and live autocomplete suggestions engine.
 */
const COMMON_DICTIONARY = [
  'HELLO', 'HI', 'HEY', 'ALL', 'YES', 'NO', 'PLEASE', 'THANK', 'THANKS', 'WELCOME',
  'SORRY', 'HELP', 'STOP', 'COME', 'GO', 'OK', 'OKAY', 'GOOD', 'GOODBYE', 'BYE',
  'MORNING', 'AFTERNOON', 'NIGHT', 'NAME', 'HOW', 'ARE', 'YOU', 'WHAT', 'WHO',
  'WHERE', 'WHEN', 'WHY', 'WHICH', 'FINE', 'GREAT', 'NICE', 'MEET', 'LOVE', 'PEACE',
  'SIGN', 'LANGUAGE', 'FRIEND', 'FAMILY', 'HAVE', 'WANT', 'NEED', 'LIKE', 'TIME',
  'TODAY', 'WORK', 'SCHOOL', 'HOME', 'CAR', 'DAY', 'WEEK', 'YEAR', 'PEOPLE', 'WORLD'
];

export function getWordSuggestions(partialWord, maxSuggestions = 4) {
  if (!partialWord || partialWord.trim().length === 0) return [];
  const u = partialWord.trim().toUpperCase();

  const priorityMap = {
    H: ['HELLO', 'HI', 'HOW', 'HELP'],
    HE: ['HELLO', 'HELP', 'HERE', 'HEAR'],
    HEL: ['HELLO', 'HELP'],
    AL: ['ALL', 'ALSO', 'ALWAYS', 'ALONE'],
    TH: ['THANK', 'THANKS', 'THAT', 'THE'],
    PL: ['PLEASE', 'PLAY', 'PLAN', 'PLACE'],
    GO: ['GOOD', 'GOODBYE', 'GOING', 'GOAL'],
    YE: ['YES', 'YEAR', 'YET', 'YELLOW']
  };

  if (priorityMap[u]) return priorityMap[u].slice(0, maxSuggestions);

  const matches = COMMON_DICTIONARY.filter(w => w.startsWith(u));
  return matches.slice(0, maxSuggestions);
}

export function formatSentence(tokens) {
  const words = [];
  let currentChars = [];

  for (const t of tokens) {
    const tok = t.trim();
    if (!tok) continue;

    if (tok === 'DEL' || tok === 'BACKSPACE') {
      if (currentChars.length > 0) currentChars.pop();
      else if (words.length > 0) words.pop();
    } else if (tok === 'SPACE' || tok === ' ') {
      if (currentChars.length > 0) {
        words.push(currentChars.join(''));
        currentChars = [];
      }
    } else if (tok.length > 1) {
      if (currentChars.length > 0) {
        words.push(currentChars.join(''));
        currentChars = [];
      }
      words.push(tok.replace(/_/g, ' '));
    } else {
      currentChars.push(tok.toUpperCase());
    }
  }

  const currentWord = currentChars.join('');
  const allWords = [...words];
  if (currentWord) allWords.push(currentWord);

  const raw = allWords.join(' ');
  if (!raw.trim()) {
    return { sentence: '', currentWord: '', suggestions: [] };
  }

  // Capitalize sentence
  const formatted = allWords.map((w, i) => {
    if (i === 0 || w.toUpperCase() === 'I') {
      return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
    }
    return w.toLowerCase();
  }).join(' ');

  const suggestions = currentWord ? getWordSuggestions(currentWord) : [];

  return {
    sentence: formatted,
    currentWord,
    suggestions
  };
}
