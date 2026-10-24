"""Higgsfield toplu üretim istekleri (MCP batch araçlarına yapıştırılacak JSON).

  python -m uh.batch images ep007 1,2,3          # klip sahnelerinin başlangıç görselleri
  python -m uh.batch stills ep007 4,5,6          # görsel sahnelerin tüm still'leri (index = n*10+k)
  python -m uh.batch clips ep007 1,2,3           # Seedance klipleri
"""
from __future__ import annotations

import json
import sys

from . import config as C
from . import state as S
from .cli import full_prompt, ref_media, rules


def _still_prompt(ep: dict, s: dict, text: str) -> str:
    """Kısa şablon: sahne + POV + kısa stil + sahne kuralları + kısa yasak listesi (ep['compact'])."""
    pov = " First-person view: the narrator's own hands or sleeves may show in the foreground." if s.get("pov") else ""
    lead = "Keep the same faces and clothes as the attached reference images; new scene: " if s.get("refs") else ""
    c = ep.get("compact")
    if not c:
        style = ep.get("style", C.STYLE)
        return f"{lead}{text}.{pov} {ep['setting']}. Style: {style}.{rules(ep, s)}"
    must = "; ".join(s.get("must", []))
    extra = "; ".join(s.get("must_not", []))
    style = c["style"] if not s.get("own_rules") else "Hand-painted gouache and watercolor storybook illustration, visible brush texture, cold blue winter light, cinematic."
    return (f"{lead}{text}.{pov} {style}" + (f" Must show: {must}." if must else "")
            + f" Avoid: {c['avoid']}" + (f"; {extra}" if extra else "") + ".")


def _img_params(ep: dict, s: dict, prompt: str) -> dict:
    p = dict(C.IMAGE_PARAMS)
    p["model"] = C.IMAGE_MODEL
    p["prompt"] = prompt
    if s.get("refs"):
        p["medias"] = [{"role": C.IMAGE_REF_ROLE, "value": m["value"]} for m in ref_media(ep, s["refs"], "image")]
    return p


def main():
    what, ep_id, spec = sys.argv[1], sys.argv[2], sys.argv[3]
    ep = S.load_episode(ep_id)
    ns = [int(x) for x in spec.split(",")]
    out = []
    for n in ns:
        s = S.scene(ep, n)
        if what == "images":
            out.append({"index": n, "params": _img_params(ep, s, _still_prompt(ep, s, s["image_prompt"]))})
        elif what == "stills":
            for k, t in enumerate(s["still_prompts"], 1):
                out.append({"index": n * 10 + k, "params": _img_params(ep, s, _still_prompt(ep, s, t))})
        elif what == "clips":
            p = dict(C.VIDEO_PARAMS)
            p["model"] = C.VIDEO_MODEL
            p["prompt"] = full_prompt(ep, s, "clip")
            p["medias"] = [{"role": "start_image", "value": S.asset(s, "image")["job_id"]}]
            chars = [r for r in s.get("refs", []) if ep["refs"][r]["kind"] == "character"]
            p["medias"] += ref_media(ep, chars[:3], "image_references")
            out.append({"index": n, "params": p})
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
