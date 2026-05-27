#!/usr/bin/env node
/**
 * Builds Textures/Birthsigns/Tx_birth_bonebiter.tga (256×128, 24-bit TGA).
 *
 * 1. Load tools/source/bonebiter_birthsign.png (must be PNG; 2:1 aspect works best)
 * 2. Contrast-enhance the wraith plate
 * 3. Draw vanilla-style blue constellation lines (bow motif)
 * 4. Scale to birthsign size and write TGA
 *
 * Run: node tools/build_bonebiter_birthsign_texture.mjs
 */

import { inflateSync } from 'node:zlib';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const MOD_ROOT = join(__dirname, '..');
const OUT = join(MOD_ROOT, 'Textures', 'Birthsigns', 'Tx_birth_bonebiter.tga');
const SOURCE = join(__dirname, 'source', 'bonebiter_birthsign.png');

const OUT_W = 256;
const OUT_H = 128;

const BLACK_POINT = 8;
const WHITE_POINT = 220;
const GAMMA = 0.76;
const CONTRAST = 1.3;
const PIVOT = 0.14;

// Muted steel-blue like vanilla birthsign constellation strokes.
const LINE_RGB = [100, 125, 160];
const LINE_WIDTH = 4;
const NODE_RGB = [150, 175, 210];
const NODE_RADIUS = 5;

// Normalized bow constellation over the upper starfield (x/y in 0..1, origin top-left).
const NODES = {
  leftTip: [0.17, 0.12],
  leftCluster: [0.28, 0.22],
  apex: [0.50, 0.08],
  rightCluster: [0.82, 0.30],
  rightTip: [0.90, 0.18],
  grip: [0.50, 0.34],
};

const SEGMENTS = [
  ['leftTip', 'leftCluster'],
  ['leftCluster', 'apex'],
  ['apex', 'rightCluster'],
  ['rightCluster', 'rightTip'],
  ['leftCluster', 'grip'],
  ['grip', 'rightCluster'],
];

const TGA_FOOTER = Buffer.from('000000000000000054525545564953494f4e2d5846494c452e00', 'hex');

function clampByte(v) {
  return Math.max(0, Math.min(255, Math.round(v)));
}

function assertPng(buf) {
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (!buf.subarray(0, 8).equals(sig)) {
    throw new Error(
      `${SOURCE} must be a PNG file (got JPEG or other format). ` +
      'Re-save the source as PNG before building.',
    );
  }
}

function enhanceWraithContrast(image) {
  const out = new Uint8Array(image.pixels.length);
  const inMin = BLACK_POINT / 255;
  const inMax = WHITE_POINT / 255;
  const inRange = inMax - inMin;

  for (let i = 0; i < image.pixels.length; i += 4) {
    for (let ch = 0; ch < 3; ch++) {
      let v = image.pixels[i + ch] / 255;
      v = (v - inMin) / inRange;
      v = Math.max(0, Math.min(1, v));
      v = v ** GAMMA;
      v = (v - PIVOT) * CONTRAST + PIVOT;
      v = Math.max(0, Math.min(1, v));
      out[i + ch] = clampByte(v * 255);
    }
    out[i + 3] = image.pixels[i + 3];
  }

  return { ...image, pixels: out };
}

function blendPixel(pixels, width, height, x, y, r, g, b, alpha) {
  const px = Math.round(x);
  const py = Math.round(y);
  if (px < 0 || py < 0 || px >= width || py >= height) return;
  const i = (py * width + px) * 4;
  const inv = 1 - alpha;
  pixels[i] = clampByte(pixels[i] * inv + r * alpha);
  pixels[i + 1] = clampByte(pixels[i + 1] * inv + g * alpha);
  pixels[i + 2] = clampByte(pixels[i + 2] * inv + b * alpha);
}

function drawDisc(pixels, width, height, cx, cy, radius, rgb, alpha) {
  const [r, g, b] = rgb;
  const r2 = radius * radius;
  for (let y = Math.floor(cy - radius); y <= Math.ceil(cy + radius); y++) {
    for (let x = Math.floor(cx - radius); x <= Math.ceil(cx + radius); x++) {
      const dx = x - cx;
      const dy = y - cy;
      if (dx * dx + dy * dy <= r2) {
        blendPixel(pixels, width, height, x, y, r, g, b, alpha);
      }
    }
  }
}

function drawLine(pixels, width, height, x0, y0, x1, y1, rgb, thickness, alpha) {
  const dx = x1 - x0;
  const dy = y1 - y0;
  const steps = Math.max(Math.abs(dx), Math.abs(dy), 1);
  const half = thickness / 2;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = x0 + dx * t;
    const y = y0 + dy * t;
    drawDisc(pixels, width, height, x, y, half, rgb, alpha);
  }
}

function drawConstellationLines(image) {
  const out = new Uint8Array(image.pixels);
  const { width, height } = image;

  for (const [a, b] of SEGMENTS) {
    const [x0, y0] = NODES[a];
    const [x1, y1] = NODES[b];
    drawLine(
      out, width, height,
      x0 * width, y0 * height,
      x1 * width, y1 * height,
      LINE_RGB, LINE_WIDTH, 0.92,
    );
  }

  for (const [nx, ny] of Object.values(NODES)) {
    drawDisc(out, width, height, nx * width, ny * height, NODE_RADIUS, NODE_RGB, 0.95);
  }

  return { ...image, pixels: out };
}

function decodePng(buf) {
  assertPng(buf);

  let width = 0;
  let height = 0;
  let bitDepth = 0;
  let colorType = 0;
  const idat = [];

  let pos = 8;
  while (pos + 8 <= buf.length) {
    const len = buf.readUInt32BE(pos);
    const type = buf.toString('ascii', pos + 4, pos + 8);
    const data = buf.subarray(pos + 8, pos + 8 + len);
    pos += 12 + len;

    if (type === 'IHDR') {
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      bitDepth = data[8];
      colorType = data[9];
      if (bitDepth !== 8 || (colorType !== 2 && colorType !== 6)) {
        throw new Error(`Unsupported PNG: depth=${bitDepth} colorType=${colorType}`);
      }
    } else if (type === 'IDAT') {
      idat.push(data);
    } else if (type === 'IEND') {
      break;
    }
  }

  const bpp = colorType === 6 ? 4 : 3;
  const stride = width * bpp;
  const raw = inflateSync(Buffer.concat(idat));
  const pixels = new Uint8Array(width * height * 4);
  const prev = new Uint8Array(stride);
  let src = 0;

  for (let y = 0; y < height; y++) {
    const filter = raw[src++];
    const row = raw.subarray(src, src + stride);
    src += stride;
    const recon = new Uint8Array(stride);

    for (let i = 0; i < stride; i++) {
      const left = i >= bpp ? recon[i - bpp] : 0;
      const up = prev[i];
      const upLeft = i >= bpp ? prev[i - bpp] : 0;
      const x = row[i];

      switch (filter) {
        case 0: recon[i] = x; break;
        case 1: recon[i] = (x + left) & 0xff; break;
        case 2: recon[i] = (x + up) & 0xff; break;
        case 3: recon[i] = (x + Math.floor((left + up) / 2)) & 0xff; break;
        case 4: {
          const p = left + up - upLeft;
          const pa = Math.abs(p - left);
          const pb = Math.abs(p - up);
          const pc = Math.abs(p - upLeft);
          const pr = pa <= pb && pa <= pc ? left : pb <= pc ? up : upLeft;
          recon[i] = (x + pr) & 0xff;
          break;
        }
        default:
          throw new Error(`Unsupported PNG filter ${filter}`);
      }
    }

    prev.set(recon);
    const di = y * width * 4;
    for (let x = 0; x < width; x++) {
      const si = x * bpp;
      pixels[di + x * 4] = recon[si];
      pixels[di + x * 4 + 1] = recon[si + 1];
      pixels[di + x * 4 + 2] = recon[si + 2];
      pixels[di + x * 4 + 3] = bpp === 4 ? recon[si + 3] : 255;
    }
  }

  return { width, height, pixels };
}

function sampleBilinear(rgba, width, height, fx, fy) {
  const x = Math.max(0, Math.min(width - 1, fx));
  const y = Math.max(0, Math.min(height - 1, fy));
  const x0 = Math.floor(x);
  const y0 = Math.floor(y);
  const x1 = Math.min(width - 1, x0 + 1);
  const y1 = Math.min(height - 1, y0 + 1);
  const tx = x - x0;
  const ty = y - y0;

  const c = (px, py) => {
    const i = (py * width + px) * 4;
    return [rgba[i], rgba[i + 1], rgba[i + 2], rgba[i + 3]];
  };

  const p00 = c(x0, y0);
  const p10 = c(x1, y0);
  const p01 = c(x0, y1);
  const p11 = c(x1, y1);
  const out = [0, 0, 0, 255];
  for (let ch = 0; ch < 3; ch++) {
    const top = p00[ch] * (1 - tx) + p10[ch] * tx;
    const bot = p01[ch] * (1 - tx) + p11[ch] * tx;
    out[ch] = Math.round(top * (1 - ty) + bot * ty);
  }
  return out;
}

function scaleTo(src, targetW, targetH) {
  const out = new Uint8Array(targetW * targetH * 4);
  for (let y = 0; y < targetH; y++) {
    for (let x = 0; x < targetW; x++) {
      const fx = (x + 0.5) * (src.width / targetW) - 0.5;
      const fy = (y + 0.5) * (src.height / targetH) - 0.5;
      const [r, g, b] = sampleBilinear(src.pixels, src.width, src.height, fx, fy);
      const di = (y * targetW + x) * 4;
      out[di] = r;
      out[di + 1] = g;
      out[di + 2] = b;
      out[di + 3] = 255;
    }
  }
  return { width: targetW, height: targetH, pixels: out };
}

function writeTga24(width, height, rgbaTopLeft) {
  const header = Buffer.alloc(18);
  header[2] = 2;
  header.writeUInt16LE(width, 12);
  header.writeUInt16LE(height, 14);
  header[16] = 24;
  header[17] = 0;

  const body = Buffer.alloc(width * height * 3);
  for (let y = 0; y < height; y++) {
    const srcY = height - 1 - y;
    for (let x = 0; x < width; x++) {
      const si = (srcY * width + x) * 4;
      const di = (y * width + x) * 3;
      body[di] = rgbaTopLeft[si + 2];
      body[di + 1] = rgbaTopLeft[si + 1];
      body[di + 2] = rgbaTopLeft[si];
    }
  }

  return Buffer.concat([header, body, TGA_FOOTER]);
}

function build() {
  const src = decodePng(readFileSync(SOURCE));
  const enhanced = enhanceWraithContrast(src);
  const lined = drawConstellationLines(enhanced);
  const canvas = scaleTo(lined, OUT_W, OUT_H);

  mkdirSync(dirname(OUT), { recursive: true });
  const outBuf = writeTga24(canvas.width, canvas.height, canvas.pixels);
  writeFileSync(OUT, outBuf);
  console.log(`Wrote ${OUT} from ${SOURCE} (${src.width}x${src.height} -> ${OUT_W}x${OUT_H}, ${outBuf.length} bytes)`);
}

build();
