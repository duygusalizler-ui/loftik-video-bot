// Eski deniz haritası görünümünde, zamanla kendini çizen rota animasyonu.
// window.setup(spec, land) bir kez, window.draw(tSaniye) her kare için çağrılır (render.mjs).
(function () {
  const INK = "#3b2b1c", RED = "#8e1b17", PAPER = "#e9dcbf", LAND = "#cdb98f";
  let S, W, H, cv, ctx, land, grain, base, proj, path, legs;

  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const ease = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
  function rand(seed) { return () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296); }

  window.setup = function (spec, landTopo) {
    S = spec; [W, H] = spec.size;
    cv = document.getElementById("c"); cv.width = W; cv.height = H; ctx = cv.getContext("2d");
    land = topojson.feature(landTopo, landTopo.objects.land);
    proj = d3.geoStereographic().rotate([-spec.center[0], -spec.center[1]]).precision(0.2);
    const bb = { type: "MultiPoint", coordinates: spec.fit };
    proj.fitExtent([[W * 0.08, H * 0.08], [W * 0.92, H * 0.92]], bb);
    base = proj.scale();
    path = d3.geoPath(proj, ctx);
    // her ayağı büyük daire üzerinde sıklaştır
    legs = spec.segments.map((s) => {
      const pts = [];
      for (let i = 0; i < s.pts.length - 1; i++) {
        const f = d3.geoInterpolate(s.pts[i], s.pts[i + 1]);
        for (let k = 0; k < 24; k++) pts.push(f(k / 24));
      }
      pts.push(s.pts[s.pts.length - 1]);
      return { ...s, dense: pts };
    });
    // kâğıt dokusu (bir kez)
    grain = document.createElement("canvas"); grain.width = W; grain.height = H;
    const g = grain.getContext("2d"), r = rand(7), img = g.createImageData(W, H);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = 120 + r() * 135; img.data[i] = v; img.data[i + 1] = v * 0.95; img.data[i + 2] = v * 0.85; img.data[i + 3] = 22;
    }
    g.putImageData(img, 0, 0);
    for (let i = 0; i < 60; i++) { // lekeler
      g.fillStyle = `rgba(120,90,50,${0.006 + r() * 0.012})`;
      g.beginPath(); g.arc(r() * W, r() * H, 40 + r() * 260, 0, 7); g.fill();
    }
  };

  function camera(t) {
    const k = S.camera; let i = 0;
    while (i < k.length - 1 && t > k[i + 1].t) i++;
    const a = k[i], b = k[Math.min(i + 1, k.length - 1)];
    const u = b.t > a.t ? ease((t - a.t) / (b.t - a.t)) : 0;
    const at = d3.geoInterpolate(a.at, b.at)(u), z = a.zoom + (b.zoom - a.zoom) * u;
    proj.scale(base * z).translate([W / 2, H / 2]);
    const p = proj(at); const tr = proj.translate();
    proj.translate([tr[0] + W / 2 - p[0], tr[1] + H / 2 - p[1]]);
  }

  const STY = {
    sail: { w: 4.5, dash: [] }, drift: { w: 4, dash: [14, 10] }, boat: { w: 4.5, dash: [1, 9] },
    caird: { w: 5, dash: [] }, walk: { w: 4, dash: [6, 6] },
  };

  function drawLeg(L, t) {
    const f = clamp((t - L.t0) / (L.t1 - L.t0));
    if (f <= 0) return null;
    const n = Math.max(2, Math.round(f * (L.dense.length - 1)) + 1);
    const xy = L.dense.slice(0, n).map((q) => proj(q));
    const st = STY[L.style] || STY.sail;
    ctx.save(); ctx.lineCap = "round"; ctx.lineJoin = "round";
    ctx.strokeStyle = "rgba(233,220,191,0.85)"; ctx.lineWidth = st.w + 5; ctx.setLineDash([]);
    ctx.beginPath(); xy.forEach((p, i) => (i ? ctx.lineTo(...p) : ctx.moveTo(...p))); ctx.stroke();
    ctx.strokeStyle = RED; ctx.lineWidth = st.w; ctx.setLineDash(st.dash);
    ctx.beginPath(); xy.forEach((p, i) => (i ? ctx.lineTo(...p) : ctx.moveTo(...p))); ctx.stroke();
    ctx.restore();
    return f < 1 ? xy[xy.length - 1] : null;
  }

  function label(L, t) {
    const a = ease((t - L.t) / 0.8);
    if (a <= 0) return;
    const p = proj(L.at); if (!p) return;
    ctx.save(); ctx.globalAlpha = a * (L.style === "sea" ? 0.55 : 1);
    const dy = (1 - a) * 10;
    if (L.style === "event") {
      ctx.fillStyle = RED; ctx.beginPath(); ctx.arc(p[0], p[1], 7, 0, 7); ctx.fill();
      ctx.strokeStyle = RED; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(p[0], p[1], 13, 0, 7); ctx.stroke();
    } else if (L.style === "place") {
      ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(p[0], p[1], 5, 0, 7); ctx.fill();
    }
    const fonts = { note: "italic 500 36px Garamond", place: "700 34px Garamond", sea: "italic 500 54px Garamond", event: "italic 500 36px Garamond", land: "700 46px Garamond" };
    ctx.font = fonts[L.style] || fonts.place;
    ctx.letterSpacing = (L.style === "event" || L.style === "note") ? "0px" : (L.style === "sea" ? "10px" : "6px");
    ctx.textAlign = L.align || "left"; ctx.textBaseline = "middle";
    const x = p[0] + (L.dx ?? 22), y = p[1] + (L.dy ?? 0) + dy;
    ctx.lineWidth = 7; ctx.strokeStyle = "rgba(233,220,191,0.9)"; ctx.strokeText(L.text, x, y);
    ctx.fillStyle = (L.style === "event" || L.style === "note") ? RED : INK; ctx.fillText(L.text, x, y);
    ctx.restore();
  }

  function cartouche(t) {
    const d = S.dates; let i = 0;
    while (i < d.length - 1 && t >= d[i + 1].t) i++;
    const fade = clamp((t - d[i].t) / 0.5);
    const x = 70, y = H - 150, w = 520, h = 96;
    ctx.save();
    ctx.fillStyle = "rgba(233,220,191,0.92)"; ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = INK; ctx.lineWidth = 2.5; ctx.strokeRect(x, y, w, h);
    ctx.lineWidth = 1; ctx.strokeRect(x + 7, y + 7, w - 14, h - 14);
    ctx.font = "700 46px Garamond"; ctx.letterSpacing = "6px"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    if (i > 0 && fade < 1) { ctx.globalAlpha = 1 - fade; ctx.fillStyle = INK; ctx.fillText(d[i - 1].text, x + w / 2, y + h / 2 + 2); }
    ctx.globalAlpha = i > 0 ? fade : 1; ctx.fillStyle = INK; ctx.fillText(d[i].text, x + w / 2, y + h / 2 + 2);
    ctx.restore();
  }

  window.draw = function (t) {
    camera(t);
    ctx.setLineDash([]); ctx.globalAlpha = 1;
    ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H);
    // graticule
    ctx.beginPath(); path(d3.geoGraticule().step([5, 5])()); ctx.strokeStyle = "rgba(90,65,40,0.28)"; ctx.lineWidth = 1.2; ctx.stroke();
    // kıyı gölgesi + kara
    ctx.save(); ctx.translate(5, 6); ctx.beginPath(); path(land); ctx.fillStyle = "rgba(80,55,30,0.18)"; ctx.fill(); ctx.restore();
    ctx.beginPath(); path(land); ctx.fillStyle = LAND; ctx.fill();
    ctx.save(); ctx.clip(); // kara üzerinde ince tarama
    ctx.strokeStyle = "rgba(70,50,30,0.16)"; ctx.lineWidth = 1;
    for (let x = -H; x < W; x += 9) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + H, H); ctx.stroke(); }
    ctx.restore();
    ctx.beginPath(); path(land); ctx.strokeStyle = INK; ctx.lineWidth = 1.8; ctx.stroke();
    // rota
    let head = null;
    for (const L of legs) { const h = drawLeg(L, t); if (h) head = h; }
    for (const L of S.labels) label(L, t);
    if (head) {
      const pulse = 0.5 + 0.5 * Math.sin(t * 5);
      ctx.fillStyle = RED; ctx.beginPath(); ctx.arc(head[0], head[1], 8, 0, 7); ctx.fill();
      ctx.strokeStyle = `rgba(142,27,23,${0.6 - 0.4 * pulse})`; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(head[0], head[1], 14 + 10 * pulse, 0, 7); ctx.stroke();
    }
    cartouche(t);
    // doku, vinyet, kenar çerçevesi
    ctx.drawImage(grain, 0, 0);
    const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.95);
    v.addColorStop(0, "rgba(60,40,20,0)"); v.addColorStop(1, "rgba(60,40,20,0.45)");
    ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
    // ışık titremesi (projektör hissi)
    const fl = rand(Math.floor(t * 30) + 11)();
    ctx.fillStyle = `rgba(255,240,210,${0.02 * fl})`; ctx.fillRect(0, 0, W, H);
  };
})();
