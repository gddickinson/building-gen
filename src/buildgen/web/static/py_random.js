// Bit-exact port of Python's random.Random (MT19937, CPython _randommodule.c + random.py) for the calls
// buildgen makes: Random(int seed), random(), uniform(a, b) and choice(seq). Same seed, same numbers as Python,
// so the building generated in the browser matches the Python package. Checked by py_random.test.mjs.
const N = 624, M = 397;

export class PyRandom {
  constructor(seed = 0) {
    this.mt = new Uint32Array(N);
    this.mti = N + 1;
    this.seed(seed);
  }

  initGenrand(s) {
    const mt = this.mt;
    mt[0] = s >>> 0;
    for (let i = 1; i < N; i++) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (Math.imul(prev, 1812433253) + i) >>> 0; // 1812433253 * prev + i, mod 2^32
    }
    this.mti = N;
  }

  // init_by_array: Python seeds an int with the 32-bit words of abs(seed), least significant first.
  seed(n) {
    if (!Number.isSafeInteger(n)) throw new Error('seed must be an integer below 2**53');
    let a = Math.abs(n);
    const key = [];
    while (a > 0) { key.push(a % 0x100000000); a = Math.floor(a / 0x100000000); }
    if (!key.length) key.push(0);
    this.initGenrand(19650218);
    const mt = this.mt;
    let i = 1, j = 0;
    for (let k = Math.max(N, key.length); k; k--) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (((mt[i] ^ Math.imul(prev, 1664525)) >>> 0) + key[j] + j) >>> 0;
      i++; j++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
      if (j >= key.length) j = 0;
    }
    for (let k = N - 1; k; k--) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (((mt[i] ^ Math.imul(prev, 1566083941)) >>> 0) - i) >>> 0;
      i++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
    }
    mt[0] = 0x80000000;
  }

  genrandUint32() {
    const mt = this.mt;
    if (this.mti >= N) {
      let kk = 0, y;
      for (; kk < N - M; kk++) {
        y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
        mt[kk] = mt[kk + M] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      for (; kk < N - 1; kk++) {
        y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
        mt[kk] = mt[kk + (M - N)] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      y = (mt[N - 1] & 0x80000000) | (mt[0] & 0x7fffffff);
      mt[N - 1] = mt[M - 1] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      this.mti = 0;
    }
    let y = mt[this.mti++];
    y ^= y >>> 11;
    y ^= (y << 7) & 0x9d2c5680;
    y ^= (y << 15) & 0xefc60000;
    y ^= y >>> 18;
    return y >>> 0;
  }

  // random.random(): 53-bit float in [0, 1)
  random() {
    const a = this.genrandUint32() >>> 5, b = this.genrandUint32() >>> 6;
    return (a * 67108864 + b) * (1 / 9007199254740992);
  }

  uniform(a, b) { return a + (b - a) * this.random(); }

  getrandbits(k) { // 1 <= k <= 32 (all buildgen needs)
    return this.genrandUint32() >>> (32 - k);
  }

  randbelow(n) {
    const k = Math.floor(Math.log2(n)) + 1; // n.bit_length()
    let r = this.getrandbits(k);
    while (r >= n) r = this.getrandbits(k);
    return r;
  }

  choice(seq) { return seq[this.randbelow(seq.length)]; }
}
