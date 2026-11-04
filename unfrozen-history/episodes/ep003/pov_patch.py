"""ep003: kullanıcı isteği — anlatım ağırlıklı olarak Luc'un gözünden (POV), izleyiciyi içine alan 'sen' cümleleri."""
import sys
sys.path.insert(0, ".")
from uh import state as S

ep = S.load_episode("ep003")
P = {
 2: dict(img="POV from the middle of a pontoon bridge over a wide river in hot summer 1812: the narrator's hands on the strap of his musket, the backs of marching infantry in dark blue coats and shakos ahead, flags and dust, green fields on the far bank",
         shots=["POV marching across a pontoon bridge among thousands of soldiers",
                "the narrator wipes sweat from his face with his sleeve, the sun blazing",
                "ahead, the column disappears east into green fields and dust"]),
 3: dict(img="POV marching on a dusty summer road: Antoine (French conscript about 19, freckled face, short red hair, dark blue line infantry coat, black shako) walking right beside the camera and grinning at it, Sergeant Morel (veteran about 50, thick grey moustache, grey-brown greatcoat, black shako) ahead looking back grumpily, Thérèse (cantinière about 35, red headscarf, blue jacket) on her small covered cart behind",
         shots=["Antoine walks beside the camera and grins at it",
                "Sergeant Morel turns around and grumbles at the camera",
                "Thérèse waves from her small covered cart"]),
 6: dict(img="POV marching into an empty Moscow street in September 1812: golden onion domes and white churches above grand houses with closed shutters, the shoulders and shakos of soldiers ahead, Antoine beside the camera staring up in wonder",
         shots=["POV looking up at golden onion domes shining above an empty street",
                "the camera passes grand houses with closed shutters",
                "Antoine beside the camera stares up with his mouth open"]),
 8: dict(img="POV inside a half-burned Moscow mansion: the narrator's hands holding up a lady's dark fur-lined cloak, Antoine laughing and pointing at it with silver spoons sticking out of his pack, Sergeant Morel in a shaggy sheepskin coat nodding approval",
         shots=["Antoine stuffs silver spoons and a small golden icon into his pack",
                "Sergeant Morel holds up a shaggy sheepskin coat with a serious face",
                "the narrator's hands lift a lady's fur-lined cloak; Antoine bursts out laughing"]),
 11: dict(pov=True, img="POV on an icy Russian road in early November 1812, heavy snow falling: a horse slipping and crashing down right in front of the camera, soldiers trying to pull it up, overturned carts beyond",
          shots=["snowflakes start falling on the marching column ahead",
                 "a horse right in front slips on the ice and crashes down",
                 "dead horses and overturned carts line the white road ahead"]),
 13: dict(pov=True, img="POV at an evening bivouac in the snow: the narrator's hand holding a piece of roasted meat on a bayonet over a small fire, Sergeant Morel sprinkling a pinch of black gunpowder on it from a powder horn, Antoine watching hungrily",
          shots=["the narrator holds a piece of meat on a bayonet over the flames",
                 "Morel sprinkles a pinch of black gunpowder over the meat",
                 "Antoine grins and waits for his turn"]),
 16: dict(pov=True, img="POV in a snowy street of Smolensk in November 1812: starving soldiers fighting over flour sacks outside a broken warehouse door, Thérèse (cantinière, red headscarf) beside the camera hugging half a sack of flour",
          shots=["soldiers break down a warehouse door and fight over sacks",
                 "Thérèse hands over her small brandy keg",
                 "Thérèse hugs half a sack of flour and nods at the camera"]),
 18: dict(pov=True, img="POV by a fire in the snow at evening: Thérèse (cantinière, red headscarf) holding a shirt over the flames and shaking it toward the camera, Antoine scratching his head, sparks rising",
          shots=["Thérèse shakes a shirt over the fire, tiny sparks crackling",
                 "Antoine scratches his head and neck",
                 "Thérèse hands the shirt to the camera with a firm look"]),
 19: dict(pov=True, img="POV at night by a fire in the snow: pale feverish Antoine (freckled, red hair) wrapped in a blanket, pressing a small golden icon into the narrator's open hand, Sergeant Morel watching in silence",
          shots=["the narrator and Morel carry Antoine between them along the snowy road",
                 "Antoine presses a small golden icon into the narrator's hand by the fire",
                 "in grey dawn light, snow lies on an empty blanket by a cold fire"]),
 21: dict(pov=True, img="POV from inside a tight group of ragged French soldiers on a snowy plain at dusk: muskets raised, a few Cossack horsemen with long lances watching from the edge of a birch forest",
          shots=["Cossack riders with long lances watch from the edge of the forest",
                 "a straggler alone in the snow looks over his shoulder at the camera",
                 "soldiers around the camera close ranks with muskets raised"]),
 22: dict(pov=True, img="POV from the crowded snowy bank of the Berezina river in November 1812: engineers wading chest-deep into icy black water among floating ice, hammering wooden trestles for a bridge",
          shots=["POV looking over a crowd at ice floating on the black river",
                 "engineers wade into the river up to their chests carrying beams",
                 "men hammer wooden trestles in the freezing water"]),
 25: dict(pov=True, img="POV looking down at the narrator's own feet wrapped in rags and blanket strips sinking into deep snow, December 1812, a small frozen bird lying on the snow ahead, the ragged column stretching away into a white haze",
          shots=["a small frozen bird lies on the white snow",
                 "the narrator's rag-wrapped feet sink into deep snow, step after step",
                 "the narrator's frosted breath clouds in front of the camera"]),
 27: dict(pov=True, img="POV crossing the frozen Niemen river at a grey dawn in December 1812: Sergeant Morel limping ahead leaning on a musket, Thérèse wrapped in a shawl beside the camera, a handful of ragged survivors on the ice",
          shots=["a handful of ragged survivors cross the frozen river at dawn",
                 "Morel limps forward ahead, leaning on a musket",
                 "Thérèse puts a hand on the camera's shoulder and smiles weakly"]),
 29: dict(pov=True, img="POV in spring 1813 at the door of a stone farmhouse in a green Auvergne mountain village: an old woman in a black shawl in the doorway, the narrator's hand holding out a small golden icon to her",
          shots=["POV walking up a green hill path toward a stone farmhouse",
                 "an old woman in a black shawl opens the door",
                 "the narrator's hand places the small golden icon into hers"]),
}
V = {  # izleyiciyi içine alan "sen" cümleleri
 4: ("But Russia does not fight us.", "Picture it: you march for weeks, and the enemy never stands still to fight."),
 15: ("At night, we sleep", "Now imagine your night. We sleep"),
 25: ("December. The worst cold", "December. Put your hand outside on the coldest day of your life. Now make it colder. The worst cold"),
}
for n, p in P.items():
    s = S.scene(ep, n)
    s["pov"] = True
    s["image_prompt"] = p["img"]
    s["shots"] = p["shots"]
for n, (a, b) in V.items():
    s = S.scene(ep, n)
    assert a in s["narration_voiced"], n
    s["narration_voiced"] = s["narration_voiced"].replace(a, b, 1)
    s["narration"] = s["narration"].replace(a.replace("...", "."), b.replace("... ", " "), 1) if a in s["narration"] else s["narration"]
S.save_episode(ep)
print(sum(1 for s in ep["scenes"] if s["pov"]), "POV sahne;", sum(1 for s in ep["scenes"] if s.get("lipsync")), "kameraya konuşma;",
      sum(len(s["narration"].split()) for s in ep["scenes"]), "kelime")
for n in V: print(n, S.scene(ep, n)["narration"][:140])
