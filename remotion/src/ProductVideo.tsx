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
 * Tek bir fotografi "Ken Burns" (yavas yakinlasma) efektiyle gosterir.
 * SADECE gercek fotografin uzerinde kod ile hareket -- hicbir AI/hayal
 * etme yok, bu yuzden urun tasarimi asla degismez.
 */
const KenBurnsImage: React.FC<{
  src: string;
  localFrame: number;
  durationInFrames: number;
  isFirst: boolean;
}> = ({ src, localFrame, durationInFrames, isFirst }) => {
  const scale = interpolate(localFrame, [0, durationInFrames], [1, 1.12], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateX = interpolate(localFrame, [0, durationInFrames], [0, -18], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Sahne girisi/cikisinda crossfade icin opaklik
  // Ilk goruntu siyahtan baslamasin -- sadece SONRAKI goruntuler icin fade-in var
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
          transform: `scale(${scale}) translateX(${translateX}px)`,
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
  const perImage = Math.floor(durationInFrames / safeImages.length);

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
      {safeImages.map((img, i) => {
        const start = i * perImage;
        const dur = i === safeImages.length - 1 ? durationInFrames - start : perImage + OVERLAP;
        return (
          <Sequence key={img + i} from={Math.max(0, start - (i > 0 ? OVERLAP : 0))} durationInFrames={dur}>
            <KenBurnsImage
              src={staticFile(img)}
              localFrame={frame - Math.max(0, start - (i > 0 ? OVERLAP : 0))}
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
