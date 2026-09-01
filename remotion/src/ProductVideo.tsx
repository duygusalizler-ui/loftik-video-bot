import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { productVideoSchema } from "./Root";

type Props = z.infer<typeof productVideoSchema>;

/**
 * PODYUM SAHNESI v2:
 * - Podyum TAMAMEN kod ile cizilmis -- gercek degil, sadece sahne prop'u.
 *   Uzerinde donen bir isik yansimasi var ("donuyormus" hissi).
 * - Urun fotografi artik bir KUTU/KART icinde degil -- arka plani
 *   kaldirilmis (rembg ile, AI degil, sadece on/arka plan ayrimi) sekilde
 *   DOGRUDAN podyumun uzerine oturuyor, hafif bir 3D sallanma ile
 *   "donuyor" hissi veriyor.
 * - URUNUN KENDI PIKSELLERI hicbir zaman degistirilmiyor/uretilmiyor --
 *   sadece konumlandirma + hafif rotasyon kod ile yapiliyor.
 */

const Podium: React.FC<{ frame: number }> = ({ frame }) => {
  const sweepAngle = (frame / 90) * 360;
  return (
    <svg
      viewBox="0 0 1080 400"
      width={1080}
      height={400}
      style={{ position: "absolute", left: 0, top: 1360 }}
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

      <ellipse cx="540" cy="110" rx="430" ry="95" fill="url(#shadow)" />
      <rect x="160" y="90" width="760" height="60" fill="#8f8f8f" />
      <ellipse cx="540" cy="150" rx="380" ry="80" fill="#7c7c7c" />
      <ellipse cx="540" cy="90" rx="380" ry="80" fill="url(#podiumTop)" />

      <g clipPath="url(#ellipseClip)">
        <g transform={`rotate(${sweepAngle} 540 90)`}>
          <ellipse cx="540" cy="90" rx="130" ry="28" fill="rgba(255,255,255,0.85)" />
        </g>
        <g transform={`rotate(${sweepAngle + 180} 540 90)`}>
          <ellipse cx="540" cy="90" rx="90" ry="18" fill="rgba(255,255,255,0.5)" />
        </g>
      </g>

      <ellipse cx="540" cy="90" rx="380" ry="80" fill="none" stroke="#ffffff" strokeOpacity="0.4" strokeWidth="2" />
    </svg>
  );
};

export const ProductVideo: React.FC<Props> = ({ title, brand, priceText, images }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const productSrc = staticFile(images[0] || "assets/img0.jpg");

  // Urun podyumda hafifce "donuyor" (3D sallanma) -- gercek 360 acisi yok
  // (elimizde tek acidan foto var), ama surekli, yumusak bir hareket
  // "canli sergileniyor" hissini veriyor.
  const swayY = Math.sin(frame / 55) * 14; // derece
  const swayX = Math.sin(frame / 70) * 3;

  // Podyumla birlikte cok hafif yukari-asagi "yuzme"
  const floatY = Math.sin(frame / 40) * 8;

  // Sahnenin geneli cok yavas yakinlasiyor
  const sceneScale = interpolate(frame, [0, durationInFrames], [1, 1.08], {
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
  const productIn = interpolate(frame, [0, 18], [40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 30%, #2a2a2a 0%, #0d0d0d 70%)",
      }}
    >
      <AbsoluteFill style={{ transform: `scale(${sceneScale})`, transformOrigin: "50% 60%" }}>
        <Podium frame={frame} />

        {/* Urun -- podyumun tam ustunde, arka plani kaldirilmis gercek foto */}
        <div
          style={{
            position: "absolute",
            left: 0,
            width: 1080,
            bottom: 1920 - 1400 + floatY - productIn,
            display: "flex",
            justifyContent: "center",
            perspective: 1400,
          }}
        >
          <div
            style={{
              transform: `rotateY(${swayY}deg) rotateX(${swayX}deg)`,
              transformStyle: "preserve-3d",
              filter: "drop-shadow(0 30px 40px rgba(0,0,0,0.6))",
            }}
          >
            <Img
              src={productSrc}
              style={{
                maxWidth: 760,
                maxHeight: 950,
                width: "auto",
                height: "auto",
                objectFit: "contain",
              }}
            />
          </div>
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
