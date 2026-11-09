// Harita animasyonunu MP4'e çevirir (headless Chromium, kare kare, ffmpeg'e boru).
//   node maps/render.mjs maps/specs/ep010_route.json build/ep010/map_route.mp4 [--preview] [--from A --to B --len L]
// --preview: 4 sn'de bir kare alıp tek bir kontrol görüntüsü (PNG) üretir.
import { createRequire } from "node:module";
import { spawn, execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const { chromium } = createRequire(import.meta.url)("playwright"); // ortamda global kurulu
const CACHE = path.join(HERE, "..", "build", "maps_cache");
const CDN = "https://cdn.jsdelivr.net/npm/";
const FILES = {
  "d3.js": "d3@7.9.0/dist/d3.min.js",
  "topojson.js": "topojson-client@3.1.0/dist/topojson-client.min.js",
  "land.json": "world-atlas@2.0.2/land-50m.json",
  "g500.woff2": "@fontsource/eb-garamond@5.0.18/files/eb-garamond-latin-500-normal.woff2",
  "g500i.woff2": "@fontsource/eb-garamond@5.0.18/files/eb-garamond-latin-500-italic.woff2",
  "g700.woff2": "@fontsource/eb-garamond@5.0.18/files/eb-garamond-latin-700-normal.woff2",
};

fs.mkdirSync(CACHE, { recursive: true });
for (const [name, p] of Object.entries(FILES)) {
  const out = path.join(CACHE, name);
  if (!fs.existsSync(out)) execFileSync("curl", ["-sSf", "-o", out, CDN + p]);
}
const rd = (n) => fs.readFileSync(path.join(CACHE, n));
const font = (n, style, weight) =>
  `@font-face{font-family:Garamond;font-style:${style};font-weight:${weight};src:url(data:font/woff2;base64,${rd(n).toString("base64")})}`;

const [specPath, outPath] = process.argv.slice(2);
fs.mkdirSync(path.dirname(outPath), { recursive: true });
const preview = process.argv.includes("--preview");
const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? Number(process.argv[i + 1]) : d; };
// --from A --to B --len L: harita zamanının A..B aralığını L saniyelik videoya yayar (anlatım süresine uydurmak için)
const A = arg("--from", 0), B = arg("--to", spec.duration), L = arg("--len", B - A);
const [W, H] = spec.size, fps = spec.fps, N = Math.round(L * fps);
const tAt = (i) => A + (B - A) * (N > 1 ? i / (N - 1) : 0);

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
${font("g500.woff2", "normal", 500)}${font("g500i.woff2", "italic", 500)}${font("g700.woff2", "normal", 700)}
html,body{margin:0;background:#000}canvas{display:block}</style></head><body><canvas id="c"></canvas>
<script>${rd("d3.js")}</script><script>${rd("topojson.js")}</script>
<script>${fs.readFileSync(path.join(HERE, "chart.js"), "utf8")}</script></body></html>`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: W, height: H } });
await page.setContent(html);
await page.evaluate(async ([s, l]) => { await document.fonts.load("700 40px Garamond"); await document.fonts.load("italic 500 40px Garamond"); window.setup(s, l); },
  [spec, JSON.parse(rd("land.json"))]);
const frame = async (t) => {
  const b64 = await page.evaluate((t) => { window.draw(t); return document.getElementById("c").toDataURL("image/jpeg", 0.95).slice(23); }, t);
  return Buffer.from(b64, "base64");
};

if (preview) {
  const dir = fs.mkdtempSync(path.join(path.dirname(outPath), "prev-"));
  const ts = []; for (let t = 1; t < spec.duration; t += spec.duration / 6) ts.push(t);
  for (const [i, t] of ts.entries()) fs.writeFileSync(path.join(dir, `${i}.jpg`), await frame(t));
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", path.join(dir, "%d.jpg"), "-vf", "scale=640:-1,tile=3x2", "-frames:v", "1", outPath]);
  fs.rmSync(dir, { recursive: true });
} else {
  const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", outPath], { stdio: ["pipe", "inherit", "inherit"] });
  for (let i = 0; i < N; i++) {
    const buf = await frame(tAt(i));
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
}
await browser.close();
console.log("ok", outPath);
