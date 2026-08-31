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

const OVERLAP = 15; // gecis (crossfade) icin komsu sahnelerin ortustugu kare sayisi

/**
 * Her "cekim" (shot), AYNI fotografin farkli bir bolgesine (genel gorunum,
 * burun detayi, baglama detayi, taban/topuk detayi) farkli bir yakinlasma
 * ile "kamera" gibi davranir -- boylece tek fotografla bile cok parcali,
 * "kurgulanmis" bir video hissi verir. Hepsi GERCEK fotografin uzerinde
 * kod ile hareket -- hicbir AI/hayal etme yok.
 */
type ShotPreset = {
  originX: string;
  originY: string;
  scaleFrom: number;
  scaleTo: number;
  panX: number;
  panY: number;
};

const SHOT_PRESETS: ShotPreset[] = [
  { originX: "50%", originY: "45%", scaleFrom: 1.0, scaleTo: 1.24, panX: -22, panY: 0 },
  { originX: "30%", originY: "75%", scaleFrom: 1.18, scaleTo: 1.44, panX: 16, panY: -18 },
  { originX: "70%", originY: "28%", scaleFrom: 1.15, scaleTo: 1.4, panX: -18, panY: 16 },
  { originX: "50%", originY: "90%", scaleFrom: 1.18, scaleTo: 1.38, panX: 10, panY: -14 },
];

const ShotImage: React.FC<{
  src: string;
  preset: ShotPreset;
  localFrame: number;
  durationInFrames: number;
  isFirst: boolean;
}> = ({ src, preset, localFrame, durationInFrames, isFirst }) => {
  const scale = interpolate(localFrame, [0, durationInFrames], [preset.scaleFrom, preset.scaleTo], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateX = interpolate(localFrame, [0, durationInFrames], [0, preset.panX], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(localFrame, [0, durationInFrames], [0, preset.panY], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const fadeIn = isFirst
    ? 1
    : interpolate(localFrame, [0, OVERLAP], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const fadeOut = interpolate(
    localFrame,
    [durationInFrames - OVERLAP, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill
        style={{
          transform: `scale(${scale}) translateX(${translateX}px) translateY(${translateY}px)`,
          transformOrigin: `${preset.originX} ${preset.originY}`,
        }}
      >
        <Img
          src={src}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const ProductVideo: React.FC<Props> = ({ title, brand, priceText, images }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const safeImages = images.length > 0 ? images : ["assets/img0.jpg"];

  // Az fotograf olsa bile en az 3 farkli "cekim" -- ayni fotograf farkli
  // bolgelerle tekrar kullanilir, boylece video hep hareketli/kurgulanmis
  // hisseder, asla tek bir sabit yakinlasma gibi "sade" durmaz.
  const numShots = Math.max(3, Math.min(4, safeImages.length === 1 ? 3 : safeImages.length));
  const shots = Array.from({ length: numShots }).map((_, i) => ({
    image: safeImages[i % safeImages.length],
    preset: SHOT_PRESETS[i % SHOT_PRESETS.length],
  }));

  const perShot = Math.floor(durationInFrames / shots.length);

  // Metin animasyonu: ilk 20 karede yukari kayarak belirir
  const textIn = interpolate(frame, [0, 20], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const textOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#111111" }}>
      {shots.map((shot, i) => {
        const start = i * perShot;
        const dur = i === shots.length - 1 ? durationInFrames - start : perShot + OVERLAP;
        const seqStart = Math.max(0, start - (i > 0 ? OVERLAP : 0));
        return (
          <Sequence key={i} from={seqStart} durationInFrames={dur}>
            <ShotImage
              src={staticFile(shot.image)}
              preset={shot.preset}
              localFrame={frame - seqStart}
              durationInFrames={dur}
              isFirst={i === 0}
            />
          </Sequence>
        );
      })}

      {/* Alt taraf icin karartma (metnin okunakli olmasi icin) */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.35) 28%, rgba(0,0,0,0) 55%)",
        }}
      />

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

      {/* Urun bilgisi -- alt */}
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
