import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { productVideoSchema } from "./Root";

type Props = z.infer<typeof productVideoSchema>;

const OVERLAP = 0; // net kesme (hard cut) -- yumusak gecis/hayalet karisma yok

/**
 * PODYUM SAHNESI:
 * - Podyum (taban) TAMAMEN kod ile cizilmis bir grafik -- gercek degil,
 *   sadece bir "sahne" prop'u. Uzerinde donen bir isik yansimasi var,
 *   boylece "donuyormus" hissi veriyor.
 * - Urun fotografi bu podyumun USTUNDE yuzen bir "kart" icinde gosteriliyor,
 *   kartin icinde hafif yakinlasma (Ken Burns) var.
 * - URUNUN KENDISI (fotograf) hicbir sekilde degistirilmiyor/uretilmiyor --
 *   sadece kod ile konumlandirilip yakinlastiriliyor. Hallucination riski
 *   sifir, cunku ortada hicbir AI/goruntu uretimi yok.
 */

type ShotPreset = {
  originX: string;
  originY: string;
  scaleFrom: number;
  scaleTo: number;
};

const SHOT_PRESETS: ShotPreset[] = [
  { originX: "50%", originY: "45%", scaleFrom: 1.0, scaleTo: 1.14 },
  { originX: "30%", originY: "70%", scaleFrom: 1.08, scaleTo: 1.24 },
  { originX: "70%", originY: "30%", scaleFrom: 1.06, scaleTo: 1.22 },
  { originX: "50%", originY: "85%", scaleFrom: 1.08, scaleTo: 1.2 },
];

const CARD_W = 860;
const CARD_H = 1040;

const Podium: React.FC<{ frame: number }> = ({ frame }) => {
  // Podyum yuzeyindeki isik yansimasi yavasca doner -- "donen podyum" hissi
  const sweepAngle = (frame / 90) * 360;

  return (
    <svg
      viewBox="0 0 1080 400"
      width={1080}
      height={400}
      style={{ position: "absolute", left: 0, top: 1330 }}
    >
      <defs>
        <radialGradient id="podiumTop" cx="50%" cy="35%" r="65%">
          <stop offset="0%" stopColor="#e9e9e9" />
          <stop offset="55%" stopColor="#c9c9c9" />
          <stop offset="100%" stopColor="#9a9a9a" />
        </radialGradient>
        <radialGradient id="shadow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgba(0,0,0,0.55)" />
          <stop offset="100%" stopColor="rgba(0,0,0,0)" />
        </radialGradient>
        <clipPath id="ellipseClip">
          <ellipse cx="540" cy="90" rx="380" ry="80" />
        </clipPath>
      </defs>

      {/* zemin golgesi */}
      <ellipse cx="540" cy="110" rx="430" ry="95" fill="url(#shadow)" />

      {/* podyum govdesi (yan taraf, hafif silindir hissi) */}
      <rect x="160" y="90" width="760" height="60" fill="#8f8f8f" />
      <ellipse cx="540" cy="150" rx="380" ry="80" fill="#7c7c7c" />

      {/* podyum ust yuzeyi */}
      <ellipse cx="540" cy="90" rx="380" ry="80" fill="url(#podiumTop)" />

      {/* donen isik yansimasi -- "spin" hissini veren tek gercek hareket */}
      <g clipPath="url(#ellipseClip)">
        <g transform={`rotate(${sweepAngle} 540 90)`}>
          <ellipse cx="540" cy="90" rx="130" ry="28" fill="rgba(255,255,255,0.85)" />
        </g>
        <g transform={`rotate(${sweepAngle + 180} 540 90)`}>
          <ellipse cx="540" cy="90" rx="90" ry="18" fill="rgba(255,255,255,0.5)" />
        </g>
      </g>

      {/* ust yuzey kenar cizgisi */}
      <ellipse cx="540" cy="90" rx="380" ry="80" fill="none" stroke="#ffffff" strokeOpacity="0.4" strokeWidth="2" />
    </svg>
  );
};

const ShotImage: React.FC<{
  src: string;
  preset: ShotPreset;
  localFrame: number;
  durationInFrames: number;
}> = ({ src, preset, localFrame, durationInFrames }) => {
  const scale = interpolate(localFrame, [0, durationInFrames], [preset.scaleFrom, preset.scaleTo], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          transform: `scale(${scale})`,
          transformOrigin: `${preset.originX} ${preset.originY}`,
        }}
      >
        <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const ProductVideo: React.FC<Props> = ({ title, brand, priceText, images }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const safeImages = images.length > 0 ? images : ["assets/img0.jpg"];
  const numShots = Math.max(3, Math.min(4, safeImages.length === 1 ? 3 : safeImages.length));
  const shots = Array.from({ length: numShots }).map((_, i) => ({
    image: safeImages[i % safeImages.length],
    preset: SHOT_PRESETS[i % SHOT_PRESETS.length],
  }));
  const perShot = Math.floor(durationInFrames / shots.length);

  // Kart -- kucuk bir "yuzuyor" hissi icin cok hafif yukari-asagi salinim
  const floatY = Math.sin(frame / 40) * 10;

  // Sahne genel yakinlasmasi (kart + podyum birlikte, cok yavas)
  const sceneScale = interpolate(frame, [0, durationInFrames], [1, 1.06], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const textOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const textIn = interpolate(frame, [0, 20], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 30%, #2a2a2a 0%, #0d0d0d 70%)",
      }}
    >
      <AbsoluteFill style={{ transform: `scale(${sceneScale})`, transformOrigin: "50% 55%" }}>
        <Podium frame={frame} />

        {/* Urun karti -- gercek fotograf, sadece konum/yakinlasma kod ile */}
        <div
          style={{
            position: "absolute",
            left: (1080 - CARD_W) / 2,
            top: 300 + floatY,
            width: CARD_W,
            height: CARD_H,
            borderRadius: 28,
            overflow: "hidden",
            boxShadow: "0 40px 70px rgba(0,0,0,0.55)",
            border: "2px solid rgba(255,255,255,0.15)",
          }}
        >
          {shots.map((shot, i) => {
            const start = i * perShot;
            const dur = i === shots.length - 1 ? durationInFrames - start : perShot;
            return (
              <Sequence key={i} from={start} durationInFrames={dur}>
                <ShotImage
                  src={staticFile(shot.image)}
                  preset={shot.preset}
                  localFrame={frame - start}
                  durationInFrames={dur}
                />
              </Sequence>
            );
          })}
        </div>
      </AbsoluteFill>

      {/* Marka -- ust sol */}
      <div
        style={{
          position: "absolute",
          top: 70,
          left: 50,
          color: "white",
          fontSize: 46,
          fontWeight: 800,
          fontFamily: "Arial, sans-serif",
          textShadow: "0 2px 8px rgba(0,0,0,0.6)",
          opacity: textOpacity,
        }}
      >
        {brand || "LOFTİK AYAKKABI"}
      </div>

      {/* Urun bilgisi -- alt, karartma uzerinde */}
      <AbsoluteFill
        style={{
          background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 22%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 90 + textIn,
          left: 50,
          right: 50,
          color: "white",
          fontFamily: "Arial, sans-serif",
          opacity: textOpacity,
        }}
      >
        <div style={{ fontSize: 40, fontWeight: 700, textShadow: "0 2px 8px rgba(0,0,0,0.7)" }}>
          {title}
        </div>
        {priceText ? (
          <div
            style={{
              fontSize: 38,
              fontWeight: 700,
              color: "#ffc86e",
              marginTop: 10,
              textShadow: "0 2px 8px rgba(0,0,0,0.7)",
            }}
          >
            {priceText}
          </div>
        ) : null}
        <div style={{ fontSize: 30, marginTop: 18, textShadow: "0 2px 8px rgba(0,0,0,0.7)" }}>
          Sipariş vermek için bio'daki linke tıkla 👆
        </div>
      </div>
    </AbsoluteFill>
  );
};
