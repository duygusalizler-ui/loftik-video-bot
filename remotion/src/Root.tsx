import { Composition } from "remotion";
import { ProductVideo } from "./ProductVideo";
import { z } from "zod";

export const productVideoSchema = z.object({
  title: z.string(),
  brand: z.string().optional(),
  priceText: z.string().optional(),
  images: z.array(z.string()), // public/ klasörüne göre göreli yol, örn. "assets/img0.jpg"
});

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="ProductVideo"
      component={ProductVideo}
      durationInFrames={240}
      fps={30}
      width={1080}
      height={1920}
      schema={productVideoSchema}
      defaultProps={{
        title: "Örnek Ürün",
        brand: "LOFTİK AYAKKABI",
        priceText: "1.430,00 TL",
        images: ["assets/img0.jpg"],
      }}
    />
  );
};
