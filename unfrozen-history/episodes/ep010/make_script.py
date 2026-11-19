import json, re, sys
sys.path.insert(0, "/home/user/loftik-video-bot/unfrozen-history")
from uh import state as S

# ep010 Shackleton / Endurance, 1914-1916. Anlatıcı KURGUSAL: Nils Halvorsen, Stromness balina istasyonunda çalışan 24 yaşında
# Norveçli; 20 Mayıs 1916'da dağdan inen üç adamı görüyor ve hikâyeyi onlardan dinlediği gibi anlatıyor (gerçek mürettebata
# birinci tekil söz yazılmaz). Gerçek olaylar: Endurance (Norveç, Sandefjord yapımı) 5 Ara 1914 Grytviken'den çıktı; 18-19 Oca 1915
# Weddell Denizi'nde buza hapsoldu (Vahsel Körfezi'ne ~1 günlük mesafe); kutup gecesi (May-Tem 1915), köpekler buz üstünde
# "dogloo"larda, buz üstünde futbol; 27 Eki 1915 gemi terk ("She's going, boys"); kişi başı 2 pound eşya, Shackleton altın
# paraları kara attı, Hussey'nin banjosu kaldı; 21 Kas 1915 gemi battı ("She's gone, boys"); Ocean Camp / Patience Camp; 9 Nis 1916
# buz kırıldı, 3 filika (James Caird, Dudley Docker, Stancomb Wills); 15 Nis 1916 Elephant Island — 497 gün sonra ilk kara;
# 24 Nis 1916 James Caird (22,5 ft) 6 kişi ~800 deniz mili; Worsley birkaç güneş ölçümüyle seyir; dev dalga (Shackleton'ın "South");
# 10 May 1916 King Haven (adanın yanlış tarafı); Shackleton, Worsley, Crean 36 saatte haritasız dağları aştı; sabah 7 düdüğü;
# 20 May 1916 Stromness, müdür Sørlle; Frank Wild her sabah "Lash up and stow, boys, the Boss may come today";
# 4. denemede Şili römorkörü Yelcho (Kaptan Luis Pardo) 30 Ağu 1916 — 22 kişinin hepsi sağ. Endurance'ın 28 kişisinin tamamı yaşadı.
# Gerçek kişilerin (Shackleton, Worsley, Crean, Wild...) yüzü GÖRÜNMEZ: arkadan, siluet, başlık/kar maskesiyle kapalı.
# 9 Kas iyileştirmesi (Valley Forge 72 sa: ort. 55 sn / %10,5, browse ağırlıklı): ilk cümle ≤ 8 sn ve şok edici gerçek ilk cümlede;
# 2 harita sahnesi (maps/, 0 kredi) izleyiciye "nerede" sorusunun cevabını veriyor.
NH = "Nils Halvorsen (Norwegian whaling station worker of 24, broad shoulders, ruddy weathered face, short reddish-blond beard, pale blue eyes, knitted grey wool cap, thick dark wool sweater under a worn oilskin coat, leather work gloves)"
CREW = "polar explorers of 1915 in heavy wool jumpers and pale gabardine windproof smocks, wool balaclavas and hoods, frost-covered beards, faces mostly hidden by hoods and scarves"
SHIP = "a black-hulled wooden three-masted barquentine of 1914 (square yards only on the foremast, gaff rig on the main and mizzen) with a white deckhouse and a tall thin funnel"

def plain(v):
    s = re.sub(r"\.\.\.\s*(?=[a-z])", " ", v)
    s = re.sub(r"\.\.\.\s*(?=['A-Z])", ". ", s).replace("...", ".").replace(" — ", ", ").replace("—", ", ")
    def fix(m):
        w = m.group(0)
        return w if w in ("I", "A") else w.lower()
    s = re.sub(r"\b[A-Z]{2,}\b", fix, s)
    s = re.sub(r"([.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), s)
    s = re.sub(r"\.\s*\.", ".", s)
    return s[0].upper() + s[1:]

STATION = "the Stromness whaling station on South Georgia in 1916: wooden sheds and red-roofed huts, a tall brick chimney, rusty boilers, a wooden pier, snowy mountains rising steeply behind, grey sky"
ICE = "endless flat Antarctic pack ice under a pale grey polar sky, pressure ridges of broken blue ice, 1915"
CAMP = "a small camp of five worn canvas bell tents and three wooden lifeboats on a flat snowy ice floe in the Weddell Sea, 1916, pale grey sky"

scenes = [
 dict(title="Three men", beat="SOĞUK AÇILIŞ (0:00) — ilk cümle ≤8 sn", mood="tense",
  v="May 20th, 1916. Three men walked down out of the mountains into our whaling station. Their ship had sunk six months before.",
  img=f"{STATION}, early morning: three ragged exhausted men seen from behind walk slowly down a snowy slope toward the wooden sheds of the station, long matted hair, filthy torn clothes, one carrying a coiled rope",
  shots=["three ragged men seen from behind stumble down a snowy slope toward the whaling station",
         "close on their worn boots with screws sticking out of the soles, crunching through the snow",
         "two whalers by the sheds stop working and stare at the strangers"],
  sound="wind, boots in snow, distant steam whistle, gulls",
  refs=["station"], must=["the three men seen only from behind, faces never visible", "1916 whaling station"]),
 dict(title="Twenty-two more", mood="tense",
  v="They'd been gone almost two years. And twenty-two more of their men were still waiting on a frozen rock, eight hundred miles away. Over the next nights, they told us everything. How twenty-eight men survived something that should have killed them all.",
  img="A tiny rocky black beach under huge ice cliffs on Elephant Island, Antarctica, 1916, grey stormy sea, two upturned wooden boats on the stones, small distant figures of men huddled around a smoky fire",
  shots=["slow push over a grey stormy sea toward a black rocky beach under ice cliffs",
         "two upturned wooden boats on the stones with smoke rising beside them",
         "distant huddled figures by a small fire, wind tearing at the smoke"],
  sound="howling wind, waves on stones, a crackling fire",
  refs=[], must=["men only small and distant, no faces"]),
 dict(title="Who I am", mood="warm",
  v="My name's Nils Halvorsen. I came from Norway at eighteen to work the whale station at Stromness. Hard work... blood, smoke and cold. In 1914, their ship stopped at Grytviken, just down the coast. Nobody had heard a word from them since.",
  img=f"{STATION}, daytime: {NH} stands on the wooden pier with a long flensing knife on his shoulder, looking out at the grey bay",
  shots=["the young whaler stands on the wooden pier and looks out at the bay",
         "close on his weathered face, wind in his beard",
         "steam drifts from the station's boilers behind him"],
  sound="wind, gulls, creaking pier, distant machinery",
  refs=["nils", "station"], must=["exactly one man"]),
 dict(title="Endurance", mood="intrigue",
  v="She was called Endurance. A wooden ship, built in my own country, in Sandefjord. Their leader was Sir Ernest Shackleton. His plan was to land in Antarctica and cross the whole continent on foot. Nobody had ever done it.",
  img=f"Grytviken harbour, South Georgia, November 1914: {SHIP} lies at anchor in a calm grey bay beneath snowy mountains, small boats beside it",
  shots=["the wooden three-masted ship lies at anchor in a calm bay under snowy peaks",
         "slow move along her rigging and masts",
         "seen from behind, a man in a dark coat stands on deck looking south"],
  sound="water lapping, rigging creaking, gulls",
  refs=["ship"], must=["the man seen only from behind", "no readable name on the ship"]),
 dict(title="Into the ice", mood="intrigue", map=True,
  v="On December 5th, 1914, she sailed south into the Weddell Sea. Within days, they were pushing through thick pack ice. Then, on January 18th, 1915, the ice closed around her. Shut in tight, they said... like an almond in a piece of toffee.",
  img="(harita sahnesi — maps/specs/ep010_route.json, 0-12,5 sn)", shots=[], sound="", refs=[]),
 dict(title="One day from land", mood="tense",
  v="They were one day's sail from where they meant to land. They could see the coast. They waited for the ice to open again. It never did.",
  img=f"{ICE}: {SHIP} frozen fast in the pack ice, men in heavy coats stand on the ice beside her looking toward a faint line of land on the horizon",
  shots=["the ship sits frozen fast in a sea of white ice",
         "seen from behind, men stand on the ice and stare toward the horizon",
         "wide shot: the tiny ship alone in the endless white"],
  sound="polar wind, ice creaking softly",
  refs=["ship"], must=["men seen from behind or far away, faces never visible"]),
 dict(title="Life on the ice", mood="warm",
  v="So the ship became their home. They built little ice houses for the dogs out on the floe. They played football on the ice. They had a banjo, and on the bad nights, someone always played it.",
  img=f"{ICE}, daytime: {CREW} play football on the flat ice beside the frozen ship, sled dogs watching from small snow kennels",
  shots=["men in heavy wool clothes kick a ball across the flat ice, laughing",
         "sled dogs curled up beside small snow kennels",
         "the frozen ship in the background with smoke from her funnel"],
  sound="men laughing, dogs barking, a ball thudding on snow",
  refs=["ship"], must=["faces hidden by hoods or far away"]),
 dict(title="The long night", mood="tense",
  v="In May, the sun went down... and didn't come back for months. Twenty-eight men in the dark, drifting with the ice, a thousand miles from anyone. Shackleton kept them busy. Meals on time. Jobs every day. No man was allowed to give up.",
  img=f"Antarctic polar night, 1915: {SHIP} frozen in the ice under a starry sky with faint green aurora, warm lamplight glowing from her small portholes",
  shots=["the frozen ship under a dark starry sky, faint aurora overhead",
         "warm lamplight glows from the portholes",
         "snow blows across the dark ice"],
  sound="polar wind, faint banjo music from inside the ship",
  refs=["ship"], must=["no people visible or only tiny silhouettes"]),
 dict(title="The squeeze", mood="tense",
  v="When spring came, the ice began to move. Huge plates of it pushed against the ship from both sides. The men could hear her timbers groan and crack, day and night, like something alive in pain.",
  img=f"{ICE}: huge slabs of pack ice pile up and press against the wooden side of {SHIP}, the hull visibly bending",
  shots=["massive slabs of ice grind against the wooden hull",
         "close on wooden planks bending and splitting under pressure",
         "the ship's masts tilt as the ice pushes her over"],
  sound="deep groaning ice, cracking timber",
  refs=["ship"], must=["no people visible"]),
 dict(title="She's going", mood="dramatic",
  v="On October 27th, 1915, Shackleton gave the order to leave the ship. He said just: She's going, boys. They dragged the lifeboats, the tents and the food out onto the ice. Their home was dying in front of them.",
  img=f"{ICE}: men in heavy clothing seen from behind drag a wooden lifeboat across the ice away from {SHIP}, which tilts badly, crushed by ice",
  shots=["men seen from behind haul a heavy wooden lifeboat across the ice",
         "boxes of supplies dragged on sledges",
         "the crushed ship tilts behind them, her masts leaning"],
  sound="wind, men straining, ice cracking, timbers breaking",
  refs=["ship"], must=["men seen only from behind, faces never visible"]),
 dict(title="Two pounds", mood="reflective",
  v="Each man could keep two pounds of personal things. That's it. Shackleton pulled out his gold coins and threw them into the snow. But he made sure they kept the banjo. He said it was vital medicine for the mind.",
  img=f"{ICE}, overcast: close on a gloved hand dropping a few gold coins into the snow, beside a small pile of left-behind belongings",
  shots=["gold coins fall from a gloved hand into the snow",
         "a few left-behind belongings lie on the ice: books, a pocket watch, a shaving brush",
         "a wooden banjo is carefully wrapped in a blanket"],
  sound="wind, coins in snow",
  refs=[], must=["only hands visible, no faces", "no readable text on books"]),
 dict(title="Your choice", beat="YORUM SORUSU", mood="warm",
  v="So tell me in the comments... if you had two pounds to save from your whole life, what would you carry onto that ice?",
  img=f"{ICE}: a single worn canvas kitbag sits on the snow beside a wooden sledge, soft grey light",
  shots=["a worn canvas kitbag on the snow",
         "slow push in on the kitbag as snow drifts past",
         "wide view of the empty white ice"],
  sound="soft wind",
  refs=[], must=["no people"]),
 dict(title="She's gone", mood="dramatic",
  v="On November 21st, 1915, they watched her go. The stern rose up out of the ice... and she slid down into the black water. Shackleton said: She's gone, boys. They were alone on the ice, with three small boats and almost nothing else.",
  img=f"{ICE}, overcast: the stern of {SHIP} rises at a steep angle from a gap in the ice as she sinks, distant small figures of men watching from the ice",
  shots=["the ship's stern rises from a gap in the pack ice",
         "she slides slowly down into the dark water",
         "seen from behind, small figures stand on the ice watching the empty hole"],
  sound="ice groaning, water rushing, then silence and wind",
  refs=["ship"], must=["men only from behind and far away"]),
 dict(title="Living on a floe", mood="tense",
  v="For months they lived on a slab of ice, drifting north. They ate seal and penguin. They burned blubber in a stove made from scrap metal. Their sleeping bags never dried. And under them, the ice grew thinner every week.",
  img=f"{CAMP}: men in heavy clothing sit around a smoky blubber stove outside the tents, faces hidden by hoods",
  shots=["smoke rises from a crude blubber stove in front of the tents",
         "a man stirs a pot with his back to the camera",
         "wide view of the tiny camp on the vast drifting ice"],
  sound="wind, crackling blubber stove, distant penguins",
  refs=["camp"], must=["faces hidden or from behind"]),
 dict(title="The floe breaks", mood="dramatic",
  v="On April 9th, 1916, the floe cracked right through their camp. It was time. They launched the three boats into the freezing sea, rowing between the ice, with nowhere to go but the nearest land.",
  img=f"{CAMP}: a crack of black water splits the ice floe between the tents, men pushing a wooden lifeboat toward the water",
  shots=["a black crack splits the ice floe through the camp",
         "men seen from behind push a wooden lifeboat into the icy water",
         "three small boats row away between floating ice"],
  sound="ice splitting, shouting, oars in water",
  refs=["camp"], must=["faces never visible"]),
 dict(title="Seven days", mood="tense",
  v="Seven days and nights in open boats. Spray froze on their clothes. Some of them couldn't feel their feet. They had no fresh water, so they chewed on frozen seal meat. Nobody slept.",
  img="Grey stormy Southern Ocean, April 1916: a small open wooden lifeboat crowded with huddled men under a tattered sail, ice crusted on the gunwales, waves breaking over the bow",
  shots=["a small open boat climbs a grey wave, spray flying",
         "ice crusts the wooden gunwales",
         "huddled hooded figures bail water, faces hidden"],
  sound="crashing waves, wind, creaking wood",
  refs=[], must=["faces hidden by hoods"]),
 dict(title="Elephant Island", mood="hopeful",
  v="On April 15th, 1916, the boats hit the stones of Elephant Island. It was the first solid ground they'd stood on in four hundred and ninety-seven days. Some of them laughed. Some just picked up stones and held them.",
  img="A narrow black stony beach under dark cliffs on Elephant Island, 1916: three wooden lifeboats pulled up on the stones, exhausted men in ragged clothes on the beach, waves behind",
  shots=["three wooden boats run onto a black stony beach",
         "a gloved hand picks up a smooth stone and holds it tight",
         "seen from behind, exhausted men stand on the beach looking at the cliffs"],
  sound="waves on stones, wind, a man laughing",
  refs=[], must=["faces never visible"]),
 dict(title="Eight hundred miles", mood="tense", map=True,
  v="But nobody would ever look for them there. The nearest help was here, at South Georgia... eight hundred miles away, across the worst ocean on Earth. Shackleton decided to go and get it himself.",
  img="(harita sahnesi — maps/specs/ep010_route.json, 12-24 sn)", shots=[], sound="", refs=[]),
 dict(title="The James Caird", mood="intrigue",
  v="He picked the strongest boat, the James Caird. Twenty-two feet long. The carpenter built up her sides with wood from the other boats and covered the deck with canvas. On April 24th, six men sailed away.",
  img="Elephant Island stony beach, April 1916: a small wooden lifeboat with a canvas-covered deck and one short mast being pushed into the surf by men seen from behind",
  shots=["men seen from behind push the small boat into the waves",
         "the boat's patched canvas deck and short mast",
         "the boat sails away into the grey sea, figures on the beach waving"],
  sound="surf, wind, men shouting farewell",
  refs=[], must=["faces never visible", "no readable text"]),
 dict(title="The Boss may come today", mood="warm",
  v="Twenty-two men stayed behind, living under two upturned boats. Their second-in-command, Frank Wild, kept them going. Every morning he'd shout: Lash up and stow, boys... the Boss may come today.",
  img="Elephant Island, 1916, grey light: two upturned wooden boats on low stone walls form a crude hut on a black beach, smoke from a gap, snow falling",
  shots=["the crude hut made of two upturned boats on the beach",
         "a hooded man seen from behind looks out to sea",
         "snow falls on the boats as smoke rises"],
  sound="wind, waves, a man calling out",
  refs=[], must=["faces never visible"]),
 dict(title="The worst ocean", mood="tense",
  v="The boat was soaked every minute. Ice built up on her so thick she started to sink, and the men crawled out to chip it off. Their navigator, Worsley, saw the sun only a few times. Every reading was a guess.",
  img="Huge grey waves of the Southern Ocean, May 1916: the small canvas-decked lifeboat heavy with ice, a hooded man kneeling on the deck chipping ice with an axe",
  shots=["the small boat climbs a towering grey wave",
         "a hooded figure chips thick ice from the deck with an axe",
         "close on a brass sextant held up toward a pale sun in the clouds"],
  sound="huge waves, wind, axe on ice",
  refs=[], must=["faces hidden by hoods"]),
 dict(title="The wave", mood="dramatic",
  v="One night, Shackleton saw a white line in the sky and thought it was clearing weather. It wasn't. It was the top of the biggest wave he'd seen in twenty-six years at sea.",
  img="Night on the Southern Ocean, 1916: an enormous white-crested wave rises over a tiny wooden lifeboat in the dark",
  shots=["a pale line on the dark horizon",
         "the line grows into an enormous breaking wave",
         "the tiny boat is lifted and buried in white water"],
  sound="roaring wave, wind",
  refs=[], must=["no faces"]),
 dict(title="Wrong side", mood="tense",
  v="On May 10th, after sixteen days, they landed on South Georgia. But on the wrong side. The whaling stations were on the far coast. The boat was too broken to sail around. Between them and us... mountains no one had ever crossed.",
  img="A small rocky cove on the wild south coast of South Georgia, May 1916: the battered lifeboat pulled onto the shingle, steep glaciers and jagged snowy mountains rising behind",
  shots=["the battered boat lies on a rocky shingle beach",
         "slow tilt up to jagged snowy mountains and glaciers",
         "three figures seen from behind look up at the peaks"],
  sound="surf, wind, seabirds",
  refs=[], must=["faces never visible"]),
 dict(title="Over the mountains", mood="tense",
  v="Shackleton, Worsley and Tom Crean went on foot. Thirty-six hours without stopping. They put screws in their boots to grip the ice. Once, lost on a mountainside at dusk, they sat down on a coiled rope and slid down the slope in the dark.",
  img="Snowy mountain ridge on South Georgia at dusk, 1916: three roped men seen from behind cross a glacier under a pale moon",
  shots=["three roped men seen from behind trudge across a glacier",
         "close on a boot with screws in the sole biting into ice",
         "three figures slide down a long snowy slope at dusk"],
  sound="wind, crunching ice, heavy breathing",
  refs=[], must=["faces never visible"]),
 dict(title="The whistle", mood="hopeful",
  v="At seven in the morning, they heard it. The steam whistle at Stromness, calling us to work. The first sound from the outside world in seventeen months.",
  img=f"{STATION}, dawn: steam bursts from a whistle on top of a brick boiler house, the bay behind",
  shots=["a jet of white steam bursts from the station whistle at dawn",
         "the sound echoes across the bay and the mountains",
         "seen from behind, three ragged men on a high ridge look down at the station"],
  sound="loud steam whistle echoing, wind",
  refs=["station"], must=["men only from behind and far away"]),
 dict(title="My name is Shackleton", mood="warm",
  v="That was the morning I saw them. Our station manager knew Shackleton well. He looked at these three black-faced strangers and said: Who the hell are you? The man in the middle said quietly: My name is Shackleton. I saw grown men turn away and cry.",
  img=f"{STATION}, morning: {NH} stands by a wooden shed watching, behind him in soft focus three ragged men stand in front of the manager's house",
  shots=["the young whaler watches with wide eyes",
         "in soft focus behind him, three ragged men stand at the manager's door, seen from behind",
         "close on the whaler's face as his eyes fill with tears"],
  sound="quiet wind, a door opening",
  refs=["nils", "station"], must=["only Nils's face is visible; the three men seen only from behind"]),
 dict(title="All safe, all well", mood="hopeful",
  v="It took four tries to reach Elephant Island through the ice. On August 30th, 1916, a small Chilean steamer, the Yelcho, came into the bay. Shackleton counted the figures on the beach. Twenty-two. All safe. All well.",
  img="Elephant Island, 30 August 1916: a small steam tug with a single funnel anchored off a black beach under ice cliffs, a rowing boat heading toward the shore, small figures waving on the beach",
  shots=["a small steamer comes into view through the mist",
         "a rowing boat heads toward the beach",
         "tiny figures on the beach wave their arms"],
  sound="ship's horn, waves, distant cheering",
  refs=[], must=["men small and distant, no faces"]),
 dict(title="How they survived", mood="reflective",
  v="People ask me how they did it. I think it was this. Their leader never let a single man believe it was over. Not on the ice. Not in the boats. Not for one day.",
  img=f"{CAMP}, golden evening light: men in heavy clothing seen from behind stand together on the ice looking toward a low sun",
  shots=["men seen from behind stand shoulder to shoulder on the ice",
         "the low sun glows on the ice",
         "slow pull back over the tiny camp"],
  sound="soft wind",
  refs=["camp"], must=["faces never visible"]),
 dict(title="Endurance", mood="reflective",
  v="I stayed in the whaling trade for thirty more years. Whenever a hard winter came, I'd think of twenty-eight men on the ice... and one word. Endurance.",
  img=f"{STATION} in winter, 1940s: an older {NH.replace('of 24', 'of about 55').replace('short reddish-blond beard', 'grey beard')} stands on the pier looking out at the snowy bay at sunset",
  shots=["the older whaler stands on the pier at sunset",
         "close on his lined face, eyes on the horizon",
         "wide view of the snowy bay and the mountains"],
  sound="wind, gulls, water",
  refs=["nils", "station"], must=["exactly one man"]),
 dict(title="Subscribe", beat="SABİT KAPANIŞ ÇAĞRISI", mood="outro", own_rules=True,
  v="If you've stayed with me this far, I think this story stayed with you too. If it did, leave a like and subscribe. That's how I know you want more stories like this one, and it helps them reach more people.",
  img=f"{STATION}, golden hour: {NH} sits on a wooden crate by the pier and looks straight toward the viewer with a small warm smile",
  shots=["the young whaler looks toward the viewer and nods slightly",
         "gulls drift over the bay behind him",
         "the camera slowly pulls back over the quiet station"],
  sound="soft wind, gulls",
  refs=["nils", "station"], must=["exactly one man"]),
 dict(title="What comes next", beat="SONRAKİ BÖLÜM", mood="intrigue", own_rules=True,
  v="In 1897, a hundred thousand men set out for the Klondike gold fields in the Yukon. To get there, they had to haul a ton of supplies over a frozen mountain pass. Most never found any gold. That story is next.",
  img="Chilkoot Pass, Alaska, winter 1898: a long line of men carrying heavy packs climbs a steep snowy mountain slope in single file",
  shots=["a long line of men with heavy packs climbs a steep snowy slope",
         "close on boots cutting steps into the frozen snow",
         "wide view of the endless line disappearing into the clouds"],
  sound="wind, heavy breathing, boots in snow",
  refs=[], must=["1898 clothing and gear", "no recognizable faces"], must_not=["modern clothing or gear"]),
]

SHEET = ("Character reference sheet, photorealistic: on the left a full-body front view standing, on the right a chest-up "
         "portrait of the same person; identical original character in both views, single character only, plain neutral grey "
         "studio background. ")
refs = {
 "nils": {"kind": "character", "prompt": SHEET + NH},
 "station": {"kind": "location", "prompt": "Location reference, single photorealistic image, NO people: " + STATION},
 "ship": {"kind": "location", "prompt": "Location reference, single photorealistic image, NO people: " + SHIP + " frozen fast in " + ICE},
 "camp": {"kind": "location", "prompt": "Location reference, single photorealistic image, NO people: " + CAMP},
}
for k, r in refs.items():
    r["n"] = k

STYLE = ("Photorealistic cinematic film still, shot on 35mm film, natural light, muted cold polar colors, gritty realistic texture, "
         "shallow depth of field. Historically accurate 1914-1916 Antarctic expedition and South Georgia whaling station: "
         "heavy wool and gabardine polar clothing, wooden lifeboats, pack ice, black stony beaches")
ep = {
 "id": "ep010", "version": 1,
 "title": "Trapped in Antarctic Ice for 497 Days: How All 28 Men Survived (1915)",
 "title_alt": "Their Ship Sank in the Antarctic. 28 Men Were Left on the Ice.",
 "title_c": "Shackleton's Endurance: The Greatest Survival Story Ever Told",
 "thumbnail": "Photorealistic: a frost-bearded polar explorer seen from behind in the foreground, the wooden ship crushed and tilted in the pack ice behind; big words '28 MEN' (B: 'TRAPPED', C: no text)",
 "hook_description": "May 1916. Three ragged men walk out of the mountains into a whaling station on South Georgia. Their ship, the Endurance, sank in the Antarctic ice six months earlier, and 22 of their men are still waiting on a frozen rock 800 miles away.",
 "character": "Nils Halvorsen, a fictional Norwegian worker at the Stromness whaling station, who heard the story from the men themselves",
 "setting": "Weddell Sea, Elephant Island and South Georgia, December 1914 to August 1916",
 "style": STYLE,
 "ref_style": "Photorealistic reference, neutral light, historically accurate 1914-1916, original person, no text, no labels, no watermark",
 "motion_suffix": ("Photorealistic cinematic historical film, natural real-time motion, no slow motion, soft cuts between shots, "
                   "faces and clothing stay consistent across shots, no text; historically accurate 1914-1916 polar expedition, "
                   "no modern objects"),
 "cast": {"Nils": NH},
 "gates": {},
 "must": ["historically accurate 1914-1916 only (except the final teaser and the 1940s pier scene)",
          "the same face and clothing as in the reference image for Nils",
          "photorealistic cinematic look in every frame"],
 "must_not": ["any text, letters, numbers, captions, logos or watermark (including a name on the ship)",
              "a recognizable face of a real historical person (Shackleton, Worsley, Crean, Wild and the whole Endurance crew): show them only from behind, far away or with faces hidden by hoods",
              "modern objects, modern ships, modern clothing",
              "gore, blood, dead animals, corpses",
              "extra fingers, deformed hands, duplicated faces",
              "the same person appearing twice in one frame (clones, twins)",
              "collage, multiple panels, split screen: it must be ONE single continuous scene",
              "cartoon, painting or illustration style"],
 "sources": [
  "Ernest Shackleton, South: The Story of Shackleton's Last Expedition 1914-1917 (1919)",
  "Frank Worsley, Shackleton's Boat Journey (1940) and Endurance: An Epic of Polar Adventure (1931)",
  "Alfred Lansing, Endurance: Shackleton's Incredible Voyage (1959)",
  "Caroline Alexander, The Endurance: Shackleton's Legendary Antarctic Expedition (1998)",
  "Scott Polar Research Institute, University of Cambridge: Imperial Trans-Antarctic Expedition archive",
  "Royal Geographical Society: Frank Hurley's expedition photographs",
 ],
 "disclosure": ("Nils Halvorsen is a fictional character, a witness at the Stromness whaling station built from the accounts of the "
                "expedition. The events, people, places and dates are real. Video was created with AI tools; the maps are drawn "
                "from the expedition's recorded route (the drift track is approximate); narration uses a synthetic voice."),
 "refs": refs,
 "music": [
  {"from": 1, "track": "Frozen_Star.mp3", "title": "Frozen Star", "mood": "dağdan inen üç adam"},
  {"from": 3, "track": "Lost_Frontier.mp3", "title": "Lost Frontier", "mood": "istasyon, gemi, yola çıkış"},
  {"from": 7, "track": "Winter_Reflections.mp3", "title": "Winter Reflections", "mood": "buzda hayat, kutup gecesi"},
  {"from": 9, "track": "Darkest_Child.mp3", "title": "Darkest Child", "mood": "sıkışma, terk, batış"},
  {"from": 14, "track": "Long_Note_Four.mp3", "title": "Long Note Four", "mood": "buz üstünde aylar"},
  {"from": 15, "track": "Dark_Times.mp3", "title": "Dark Times", "mood": "buz kırılır, filikalar"},
  {"from": 17, "track": "Eternal_Hope.mp3", "title": "Eternal Hope", "mood": "Elephant Island"},
  {"from": 19, "track": "Crossing_the_Chasm.mp3", "title": "Crossing the Chasm", "mood": "James Caird, okyanus, dağlar"},
  {"from": 25, "track": "Echoes_of_Time.mp3", "title": "Echoes of Time", "mood": "düdük, Stromness"},
  {"from": 27, "track": "Healing.mp3", "title": "Healing", "mood": "kurtarma, sonrası"},
  {"from": 30, "track": "Dreams_Become_Real.mp3", "title": "Dreams Become Real", "mood": "kapanış"},
 ],
 "next_episode_tease": "The Klondike Gold Rush, 1897-1898",
 "compact": {"style": STYLE + ". Show only what is described.",
             "avoid": "text, letters, numbers, readable signs, logos, watermark, a name on the ship; recognizable faces of real historical people; modern objects, ships or clothing; gore, blood, dead animals, corpses; extra fingers, deformed hands, duplicated people; collage or split panels; painting, cartoon or illustration style"},
 "srt_replace": {},
 "voice_engine": None,
 "scenes": [],
}
CUES = [m["from"] for m in ep["music"]]
PAD = tuple(i for i, s in enumerate(scenes, 1) if i < len(scenes) and (i + 1) in CUES)
for i, s in enumerate(scenes, 1):
    sc = {"n": i, "title": s["title"], "mode": "clip", "pov": False, "narration": plain(s["v"]),
          "narration_voiced": s["v"], "image_prompt": s["img"], "shots": s["shots"], "sound": s["sound"],
          "refs": s["refs"], "voice_mood": s["mood"], "pad": 2.2 if i in PAD else 0.8}
    if i in (2, 15, 16, 17, 19, 20, 21, 22, 23, 24):  # QA: gpt_image arka plana hayalet gemi koyuyordu
        s.setdefault("must_not", []).append("any ship or sailing vessel at sea or in the background")
    for k in ("beat", "must", "must_not", "own_rules", "map"):
        if s.get(k):
            sc[k] = s[k]
    if s.get("map"):  # harita sahnesi: görsel/klip üretilmez, maps/render.mjs çıktısı clips/NNN.mp4 olarak konur
        sc["no_ambience"] = True
    ep["scenes"].append(sc)
ep["voice_engine"] = S.load_episode("ep009")["voice_engine"]
ep["max_credits"] = 600
if __name__ == "__main__" and "--force" in sys.argv:
    S.save_episode(ep)

w = [len(s["narration"].split()) for s in ep["scenes"]]
nclip = sum(1 for s in ep["scenes"] if not s.get("map"))
cost = nclip * (15 + 2.75) + len(refs) * 2.75
print(len(w), "sahne", sum(w), "kelime", min(w), max(w), "≈", round(sum(w) / 2.81 / 1.06 / 60 + len(w) * 0.9 / 60, 1), "dk",
      "| ilk sahne", w[0], "kelime | klip", nclip, "| tahmini", cost, "kredi")
