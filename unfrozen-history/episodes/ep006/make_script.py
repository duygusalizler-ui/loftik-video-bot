import json, re, sys
sys.path.insert(0, "/home/user/loftik-video-bot/unfrozen-history")
from uh import state as S

# Kurgusal karakterler (Dorj ailesi). Moğol bozkırında kış göçebeliği, zud (felaket kışı), otor, dokuz dokuzlar gerçek;
# aile ve o kışın kendisi hayalî. Yaklaşık 1900, kuzeybatı Moğolistan (Uvs havzası çevresi, ülkenin en soğuk bölgesi).
# KARMA YÖNTEM (STRATEGY §17, kullanıcı onayı 8 Eki): mode="clip" sahneler Seedance klibi (ilk ~60 sn + kilit anlar),
# mode="stills" sahneler 2K gpt_image_2 görselleri + Ken Burns (assemble.build_stills), ortam sesi ambience_from klibinden.
# Kurallar: kanca ilk 5 sn, ~%45'te orta seçim sorusu (beğeni/yorum), kapanış CTA'sında "kill" yok.
DO = "Dorj (Mongolian herder about 40, weathered sun-browned face, thin black moustache, narrow eyes creased from wind, dark brown sheepskin-lined winter deel robe tied with an orange silk sash, pointed fox-fur hat with ear flaps, black leather gutal boots with upturned toes)"
OY = "Oyun (his wife about 36, calm round face, red wind-burned cheeks, two long black braids, dark blue felt-lined winter deel with a green sash, round fur-trimmed hat, leather boots)"
BA = "Bat (their son, 11, thin, short black hair, quick bright eyes, small brown sheepskin deel with a yellow sash, fur hat with ear flaps, small leather boots)"
SA = "Saran (their daughter, 7, chubby cheeks, two short black braids, little red deel with a blue sash, round fur hat, small felt boots)"

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

GER_IN = "inside the family's round felt ger: wooden lattice walls, red-painted roof poles meeting at the round wooden roof ring, an open hearth in the centre with an iron fire-ring and a kettle, felt rugs on the floor, low painted wooden chests and beds around the walls, the door facing south"

scenes = [
 # ───────── İLK ~60 SN: TAMAMI KLİP ─────────
 dict(title="Fifty below", mode="clip", pov=True, beat="SOĞUK AÇILIŞ (0:00) — kanca ilk 5 sn", mood="tense",
  v="Fifty degrees below zero. My eyelashes freeze together when I blink. And the only thing between my children and this cold... is a tent made of FELT. Out here, there are no walls, no forests, no cellars. Just my family, two hundred animals... and a winter that wants all of us.",
  img=f"The open Mongolian steppe at dawn in deep winter, about 1900, extreme cold, ice fog glittering in the air: {DO} stands beside his shaggy horse, frost white on his eyelashes, moustache and fur hat, his breath a cloud; behind him a single round white felt ger with smoke rising from its roof ring, a herd of sheep and goats huddled in a stone pen",
  shots=["frost-white eyelashes and moustache, the herder blinks slowly in the icy dawn",
         "a shaggy horse's muzzle and mane hung with frost, breath steaming",
         "a lone white felt ger on the endless snowy plain, smoke rising from its roof ring"],
  sound="howling steppe wind, a horse snorting, ice crystals crackling",
  refs=["dorj", "steppe"], must=["exactly one person in the frame", "a traditional white felt ger with no stove pipe"]),
 dict(title="Who I am", mode="clip", pov=True, mood="warm",
  v="My name is Dorj. I am a herder, like my father, and his father before him. We live in the far north-west of Mongolia, in one of the coldest places on Earth. We own no house and no field. Everything we have walks on four legs: horses, camels, cattle, sheep and goats. We call them the five snouts.",
  img=f"Late autumn on the Mongolian steppe, about 1900, golden dry grass and the first snow on the far mountains: {DO} on horseback with a long wooden lasso pole, driving a mixed herd of horses, two-humped Bactrian camels, shaggy cattle, sheep and goats across the plain, a white felt ger far behind",
  shots=["the herder rides at a calm trot behind his mixed herd, lasso pole over his shoulder",
         "two-humped camels and shaggy cattle walk through golden grass",
         "a flowing river of sheep and goats crosses the open plain"],
  sound="hooves on frozen ground, bleating sheep, a man's short whistle",
  refs=["dorj", "steppe"], must=["exactly one rider", "Bactrian camels have two humps"]),
 dict(title="My family", mode="clip", pov=True, mood="warm",
  v="My wife Oyun knows every animal in the herd by its face. Our son Bat is eleven. He has been riding since he was four, and he already rides better than me. And our daughter Saran is seven. Her job is the baby goats... and she gives every single one a name.",
  img=f"Bright cold morning beside the family's white felt ger on the steppe, about 1900: {OY} milking a goat by the pen, {BA} sitting confidently on a small shaggy horse, {SA} kneeling in the snow hugging a small baby goat and laughing",
  shots=["Oyun milks a goat into a wooden pail, her breath steaming",
         "Bat sits straight on a small shaggy horse and grins",
         "Saran hugs a baby goat in the snow and laughs"],
  sound="a goat bleating, milk splashing into a pail, a little girl laughing",
  refs=["oyun", "bat", "saran", "steppe"], must=["exactly one woman, one boy and one girl"]),
 # ───────── HAZIRLIK (görseller) ─────────
 dict(title="A house of felt", mode="stills", ambience_from=1, pov=False, mood="intrigue",
  v="Our home is a ger. A round frame of wooden lattice, with roof poles meeting at a ring in the centre, all wrapped in thick felt. Two of us can take it down in an hour and load it onto camels. The door always faces south, away from the cold north wind.",
  img="A round white felt ger on the snowy Mongolian steppe, about 1900, its low painted wooden door facing the low winter sun, smoke rising from the roof ring, ropes of horsehair tied around the felt",
  stills=["Close painterly view of the structure of a Mongolian ger being raised on the steppe, about 1900: an expanding wooden lattice wall in a circle, thin red-painted roof poles meeting at a round wooden roof ring held up by two painted posts, a rolled bundle of white felt waiting on the ground, NO people, autumn grass",
          "A round white felt ger alone on the snowy Mongolian steppe, about 1900, seen from the south: its small painted orange wooden door facing the low winter sun, smoke rising from the roof ring, horsehair ropes wrapped around the felt, long blue shadows on the snow, NO people"],
  sound="wind over snow, wooden poles knocking softly",
  refs=["steppe"], must=["no stove pipe, smoke rises only through the roof ring"]),
 dict(title="The winter camp", mode="stills", ambience_from=2, pov=True, mood="intrigue",
  v="We move four times a year, following the grass. But the winter camp is the most important choice of the whole year. We set it on the south side of a hill, so the hill takes the north wind for us. The animals sleep in a pen of stone, on a floor of their own dried dung. It sounds strange, but that dung floor keeps them warm all winter.",
  img="A Mongolian winter camp on the sheltered south side of a low rocky hill: one white felt ger, a low stone-walled animal pen beside it, sheep and goats inside, snow on the hill above",
  stills=["Wide painterly view of a Mongolian winter camp about 1900, set on the sheltered south side of a low rocky snowy hill: one white felt ger with smoke from the roof ring, a low dry-stone animal pen beside it, the hill rising behind to the north, the snowy plain open to the south, NO people",
          "Inside a low dry-stone animal pen in winter: sheep and goats lying close together on a thick dark floor of packed dried dung, pale steam rising from their backs in the cold, snow on top of the stone walls, NO people"],
  sound="wind blocked by a hill, sheep breathing and shuffling",
  refs=["steppe"], must=["a single ger, not a village"]),
 dict(title="Autumn: the extra felt", mode="stills", ambience_from=3, pov=True, mood="warm",
  v="All autumn, we get ready. Oyun and I make new felt from the summer's wool. We lay the wool on the ground, soak it, roll it inside a wet hide, and drag it behind a horse until it becomes one thick sheet. In summer our ger has one layer of felt. In winter, it has three.",
  img=f"Autumn felt-making on the steppe: {OY} and {DO} spreading sheep's wool on a wet hide on the ground",
  stills=[f"Autumn on the Mongolian steppe, about 1900: {OY} kneels and spreads fluffy white sheep's wool evenly on a large wet hide laid on the ground, a bucket of water beside her, a white felt ger behind",
          f"Felt-making on the autumn steppe, about 1900: {DO} on horseback drags a long tightly rolled bundle of hide and wool behind his horse on a rope across the grass, the ger in the distance",
          f"{OY} and {BA} lift a thick new sheet of white felt over the wooden roof poles of their ger, adding an extra winter layer, autumn steppe behind"],
  sound="wind, a horse walking slowly, a heavy roll thumping on grass",
  refs=["oyun", "dorj", "bat", "steppe"], must=["at most two people in each image"]),
 dict(title="Fire without wood", mode="stills", ambience_from=1, pov=True, mood="intrigue",
  v="There are no trees here. So our fire burns dung. All summer, Saran and Bat walk the pastures with baskets on their backs, picking up dried cow dung. It burns clean and slow. But for the coldest nights, we save the sheep dung... small, dark, and it burns HOT.",
  img=f"{SA} and {BA} with wicker baskets on their backs collecting dried dung on the summer steppe",
  stills=[f"Late summer on the Mongolian steppe, about 1900: {SA} and {BA} walk across the grass with tall wicker baskets on their backs, Bat tossing a flat piece of dried cow dung over his shoulder into his basket with a small wooden fork",
          "Beside a white felt ger in autumn: a tall neat stack of dried flat dung cakes, the winter fuel store, a wicker basket leaning against it, snowy mountains far away, NO people"],
  sound="footsteps in dry grass, wicker creaking, crickets",
  refs=["saran", "bat", "steppe"], must=["exactly one boy and one girl"]),
 dict(title="The winter meat", mode="stills", ambience_from=3, pov=True, mood="intrigue",
  v="When the first real cold comes in early winter, we prepare the winter meat. We call it idesh. The meat freezes outside on its own, and it stays frozen until spring. Oyun also cuts beef into long thin strips and hangs them inside the ger to dry. Dried like this, the meat of a whole cow becomes so light that a man can carry it on his horse.",
  img=f"{OY} hanging thin strips of beef to air-dry on a cord inside the ger",
  stills=[f"Inside the family's ger in early winter, about 1900, {GER_IN}: {OY} hangs long thin strips of dark red beef on a cord stretched between the roof poles to air-dry, warm firelight",
          "Outside a white felt ger in early winter: frozen pieces of meat wrapped in cloth and stored in a wooden box on a low cart beside the ger, frost on everything, NO people"],
  sound="fire crackling, a knife on wood, wind outside the felt",
  refs=["oyun", "ger_in"], must_not=["blood", "animal carcasses or butchering"]),
 dict(title="Counting the nines", mode="stills", ambience_from=1, pov=True, beat="⚡ KIRILMA 1: gerçek soğuk başlıyor", mood="tense",
  v="On the shortest day of the year, the real winter begins. We count it in nines. Nine nines... eighty-one days. In the first nines, the milk vodka freezes. Then the strong vodka. And in the fourth nine, they say, even the horns of an ox can freeze. This is when the cold reaches fifty below.",
  img="The Mongolian steppe at the winter solstice: a lone ger under a deep blue night sky full of stars, everything white with frost",
  stills=["Night on the snowy Mongolian steppe at the winter solstice, about 1900: a lone white felt ger with a faint warm glow at its roof ring and smoke rising straight up in the still cold air, a sky full of stars, a thin crescent moon, NO people",
          "Dawn after the coldest night: a shaggy ox standing in a stone pen, its horns, eyelashes and long hair thick with white frost, ice fog in the air, NO people"],
  sound="total silence, a faint crackle of frost, distant wolf howl",
  refs=["steppe"]),
 # ───────── KURALLAR ─────────
 dict(title="Rule one: the horses go first", mode="clip", pov=False, beat="Kural 1", mood="intrigue",
  v="My first rule: the horses go first. Every morning, I take the horses out onto the snow. They dig through it with their hooves, down to the dry grass underneath. Behind them, the sheep and goats eat what the horses have uncovered. Without the horses... the sheep would starve on top of their own food.",
  img=f"Morning on the snowy Mongolian steppe, about 1900: a herd of shaggy Mongolian horses pawing through deep snow with their front hooves to reach yellow grass underneath, behind them a flock of sheep and goats grazing in the dug patches, {DO} on horseback watching",
  shots=["a shaggy horse strikes the snow with its front hoof, sending powder flying",
         "yellow grass appears under the snow and the horse lowers its head to eat",
         "sheep and goats move into the dug patches behind the horses"],
  sound="hooves striking snow, horses snorting, sheep bleating",
  refs=["dorj", "steppe"], must=["exactly one rider", "horses dig with front hooves"]),
 dict(title="Rule two: the goats lead", mode="stills", ambience_from=10, pov=True, beat="Kural 2", mood="intrigue",
  v="My second rule: keep the sheep and the goats together. Sheep are calm, but in a blizzard they stand still and freeze. Goats are clever and always moving, so the goats lead and the sheep follow. And our sheep carry their own food: a big fat tail. All winter, they live on the fat they stored in summer.",
  img="A mixed flock of Mongolian fat-tailed sheep and goats walking through snow, goats in front",
  stills=["A mixed flock walking in a line through snow on the Mongolian steppe, about 1900: a few long-haired goats with curved horns lead in front, a long line of thick-woolled fat-tailed sheep follows behind, NO people",
          "Close painterly view from behind of several Mongolian sheep in the snow, their broad fat tails clearly visible, frost on their thick wool, NO people"],
  sound="hooves in snow, goats calling, wind",
  refs=["steppe"]),
 dict(title="Water from ice", mode="stills", ambience_from=1, pov=True, mood="intrigue",
  v="When the river freezes, we still need water: for tea, for cooking, for the animals. So Bat and I ride to the river with an axe and cut blocks of ice. We carry them home on a camel. In the ger, the ice melts in the kettle... and becomes salty milk tea.",
  img=f"{DO} and {BA} cutting blocks of ice from a frozen river with an axe, a camel waiting",
  stills=[f"A frozen river in a snowy Mongolian valley, about 1900: {DO} chops a block of clear blue ice with an axe while {BA} holds a rope, a two-humped Bactrian camel with a wooden frame on its back waits behind them",
          f"Inside the family's ger, {GER_IN}: {OY} pours milk from a wooden bucket into a big iron pot on the hearth fire, pieces of ice melting in it, steam rising, warm light"],
  sound="axe on ice, cracking ice, a camel groaning",
  refs=["dorj", "bat", "oyun", "ger_in"], must=["a two-humped Bactrian camel", "at most two people in each image"]),
 dict(title="Rule three: the fire never sleeps", mode="stills", ambience_from=3, pov=True, beat="Kural 3", mood="warm",
  v="My third rule: at night, one of us stays awake to feed the fire. When the fire is burning, the ger is warm enough to sleep in our robes. But if the fire dies at fifty below... the cold comes through three layers of felt in less than an hour. We take turns, all night, every night.",
  img=f"Night inside the ger: {DO} sitting by the hearth feeding dung into the fire while the family sleeps under their robes",
  stills=[f"Deep night inside the family's ger, {GER_IN}: {DO} sits awake cross-legged by the low glowing hearth, placing a piece of dried dung on the fire, his face lit orange, cold blue moonlight falling through the roof ring",
          f"Deep night inside the ger, warm low firelight: {OY}, {BA} and {SA} asleep side by side on low wooden beds along the lattice wall, covered with their thick sheepskin robes, frost on the inside of the felt near the door"],
  sound="low crackling fire, soft breathing, wind pressing on the felt",
  refs=["dorj", "oyun", "bat", "saran", "ger_in"], must=["each person appears only once"]),
 dict(title="The wolves", mode="stills", ambience_from=1, pov=True, mood="tense",
  v="And there are the wolves. Winter makes them hungry and brave. Our dogs sleep outside, against the pen, and when they bark in the night, I go out with a burning stick. One night, the dogs went quiet... and in the morning, there were tracks all around the pen.",
  img="Wolf tracks in the snow around a stone pen at dawn, a big dark Mongolian herding dog standing guard",
  stills=["Night on the snowy steppe beside a stone animal pen, about 1900: a big shaggy black-and-tan Mongolian herding dog stands guard and stares into the darkness, two pairs of glowing eyes far away in the dark, NO people",
          "Dawn beside a dry-stone animal pen: a line of large wolf paw prints circling the pen in fresh snow, frost on the stones, NO people, NO wolves visible"],
  sound="dogs barking, a distant wolf howl, wind",
  refs=["steppe"], must_not=["wolves attacking", "blood"]),
 dict(title="Horses or sheep?", mode="stills", ambience_from=10, pov=True, beat="❓ ORTA SORU (~%45) — seçim CTA (beğeni + yorum)", mood="tense",
  v="Now, let me ask YOU something. If the grass ran out, and you could only save one: the horses that dig the snow for everyone... or the sheep that feed and clothe your children. Which would you save? Tell me in the comments. And if you'd have saved the horses, tap the like button, so I know.",
  img=f"{DO} standing between his horses and his sheep in the snow, looking from one to the other",
  stills=[f"Grey winter afternoon on the steppe: {DO} stands alone in the snow between a group of shaggy horses on the left and a flock of sheep on the right, looking thoughtfully from one to the other, his hand on his chin",
          "A painterly close view: the frosty face of a shaggy Mongolian horse beside the frosty face of a Mongolian sheep, both looking toward the viewer, soft snowfall, NO people"],
  sound="soft wind, a horse snorting, a sheep bleating",
  refs=["dorj", "steppe"], must=["exactly one person"]),
 # ───────── ZUD ─────────
 dict(title="The warm wind", mode="stills", ambience_from=1, pov=True, beat="⚡ KIRILMA 2: sahte bahar", mood="hopeful",
  v="Then, in the fifth nine, something strange happens. A warm wind comes from the south. For two days, the sun is soft and the snow starts to melt. Saran runs outside without her hat. Bat says winter is over. But my father taught me to be afraid... of a warm day in winter.",
  img=f"{SA} running outside the ger without her hat in soft warm sunshine, melting snow",
  stills=[f"A surprisingly mild sunny winter day on the steppe: {SA} runs and laughs outside the ger with her fur hat in her hand, the snow wet and slushy, water dripping from the felt",
          f"{DO} stands at the ger door looking up at the soft sun with a worried frown, wet melting snow at his feet"],
  sound="dripping water, a little girl laughing, a gentle warm wind",
  refs=["saran", "dorj", "steppe"], must=["exactly one person in each image"]),
 dict(title="The iron winter", mode="clip", pov=False, beat="⚡ KIRILMA 3: buz zırhı (demir zud)", mood="tense",
  v="On the third night, the cold returns. All that melted snow freezes into one sheet of ice, as hard as iron. We call it the iron dzud. The grass is still there... locked under glass. The horses strike it with their hooves and slip. The sheep lick the ice. And they can't reach anything.",
  img="The Mongolian steppe after a freezing rain: the whole plain covered in a shiny hard crust of ice with dry grass frozen underneath, shaggy horses slipping and striking the ice with their hooves, a white felt ger in the distance under a grey sky",
  shots=["a horse's hoof strikes a shiny sheet of ice and slides",
         "dry yellow grass frozen beneath clear ice like glass",
         "a flock of sheep stands still on the glittering ice plain, heads down"],
  sound="hooves clattering on ice, a cold wind, an uneasy bleat",
  refs=["steppe"], must=["no people"], must_not=["dead animals"]),
 dict(title="Breaking the ice", mode="stills", ambience_from=17, pov=True, mood="sad",
  v="For days, we try everything. Bat and I break the ice with axes and sticks, one small patch at a time. Oyun gives the weakest sheep the dried curd and flour we kept for ourselves. But every morning, the animals are thinner. And I know that if we stay here... we lose them all.",
  img=f"{DO} and {BA} breaking a crust of ice on the steppe with axes so the sheep can reach the grass",
  stills=[f"Grey freezing day on the ice-crusted steppe: {DO} and {BA} break the hard ice crust with an axe and a thick stick, uncovering small patches of yellow grass, thin sheep crowding close behind them",
          f"Inside the stone pen: {OY} kneels and feeds a thin weak sheep from her hand, her face tired and worried, frost on her hat"],
  sound="axes on ice, heavy breathing, wind",
  refs=["dorj", "bat", "oyun", "steppe"], must=["at most two people in each image"], must_not=["dead animals"]),
 dict(title="Otor: we must move", mode="stills", ambience_from=1, pov=True, mood="tense",
  v="So we do what herders have always done in a dzud. We call it otor. The strongest animals must walk to a far pasture, to the mountains, where the wind has blown the snow away. Bat and I will take them. Oyun and Saran will stay at the camp, with the weakest animals... alone.",
  img=f"{DO} and {OY} talking seriously inside the ger by the fire",
  stills=[f"Inside the family's ger at night, {GER_IN}: {DO} and {OY} sit close by the low fire talking seriously, Oyun's hand on his arm, the firelight on their worried faces",
          f"Dawn outside the ger: {OY} hands {BA}, already on his small horse, a leather bag of food, frost in the air, the herd gathering behind"],
  sound="low fire, quiet voices, a horse stamping",
  refs=["dorj", "oyun", "bat", "ger_in"], must=["exactly two people in each image"]),
 dict(title="The long ride", mode="clip", pov=False, mood="tense",
  v="We ride for four days. Bat in front, the horses behind him, the sheep and goats in the middle, and me at the back. At night we sleep on the ground in our robes, back to back, with the horses standing around us like a wall. Bat doesn't complain once.",
  img=f"A snowy mountain valley in Mongolia: {DO} and {BA} on horseback driving a herd of horses, sheep and goats through deep snow toward wind-swept mountain slopes under a pale cold sky",
  shots=["the boy rides in front through deep snow, the herd following in a long line",
         "the herd crosses a white valley toward bare wind-swept slopes",
         "at dusk, father and son sit back to back by a tiny fire, the horses standing around them"],
  sound="hooves in deep snow, wind, a crackling small fire",
  refs=["dorj", "bat", "steppe"], must=["exactly two riders", "each person appears only once"]),
 dict(title="Wind-swept grass", mode="clip", pov=False, beat="⚡ KIRILMA 4: umut", mood="hopeful",
  v="And on the fifth morning... we find it. A mountain slope where the wind has scraped the snow away. Grass. Dry, yellow, beautiful grass. The horses run to it. The sheep follow. I sit down in the snow, and I laugh like a fool. Bat laughs with me.",
  img=f"A sunny wind-swept mountain slope in Mongolia with yellow grass free of snow, a herd of horses, sheep and goats running to graze, {DO} sitting in the snow laughing beside {BA}",
  shots=["horses gallop up a slope of bare yellow grass in bright sun",
         "sheep and goats spread out and graze hungrily",
         "father and son sit in the snow and laugh together"],
  sound="galloping hooves, happy bleating, a man's laughter",
  refs=["dorj", "bat", "steppe"], must=["exactly one man and one boy"]),
 dict(title="At the camp", mode="stills", ambience_from=3, pov=True, mood="warm",
  v="At the camp, Oyun was not alone after all. We camp close to two other families, as herders always do. Their sons helped her break the ice and fetch water. And every evening, Saran sang to the baby goats inside the ger, to keep them warm.",
  img=f"{OY} and a neighbour's son breaking ice by the camp; {SA} singing to baby goats inside the ger",
  stills=["A small Mongolian winter camp of three white felt gers close together on the sheltered side of a hill, smoke rising from all three roof rings, a shared stone pen, two young men in deels carrying ice blocks, about 1900",
          f"Inside the family's ger in warm firelight, {GER_IN}: {SA} sits on a felt rug singing softly to three small baby goats curled up on a sheepskin beside her"],
  sound="distant voices, a little girl humming, fire crackling",
  refs=["saran", "ger_in", "steppe"], must=["the girl appears only once"]),
 # ───────── BAHAR ─────────
 dict(title="The ninth nine", mode="stills", ambience_from=1, pov=True, mood="hopeful",
  v="After a month in the mountains, the ninth nine ends. The snow turns soft, and the ice breaks. Bat and I bring the herd home. We lost thirty sheep and two old horses. But almost two hundred animals walk back into the pen. And Oyun runs out of the ger... without her hat.",
  img=f"{DO} and {BA} returning to the camp with the herd in late winter, {OY} running out to meet them",
  stills=[f"Late winter, melting snow on the steppe: {DO} and {BA} ride slowly home behind a long herd of thin but living horses, sheep and goats, the white ger in the distance",
          f"Outside the ger in pale spring sunshine: {OY} runs out of the door bareheaded, her braids flying, her hands open, laughing with relief"],
  sound="hooves on wet ground, sheep bleating, a woman's joyful cry",
  refs=["dorj", "bat", "oyun", "steppe"], must=["at most two people in each image"]),
 dict(title="White Moon", mode="stills", ambience_from=3, pov=True, mood="warm",
  v="Then comes Tsagaan Sar, the White Moon, our new year. We greet each other with open arms, the young holding up the arms of the old. We eat steamed dumplings until we cannot move. And we say: we have crossed the winter. Because here, that is the greatest thing you can say.",
  img=f"Tsagaan Sar inside the ger: {DO} and {OY} greeting each other with the traditional arm greeting",
  stills=[f"Lunar New Year morning inside the family's ger, {GER_IN}: {BA} holds up the forearms of {DO} from underneath in the traditional respectful greeting, both in their best deels, a long blue silk scarf over Bat's hands",
          "Close painterly view of a low painted wooden table inside a ger covered with festive food: a plate piled with steamed meat dumplings, a tall layered stack of traditional biscuits, bowls of milk tea, warm light, NO people"],
  sound="cheerful voices, cups clinking, fire crackling",
  refs=["dorj", "bat", "ger_in"], must=["exactly two people in the first image"]),
 dict(title="The first lamb", mode="clip", pov=False, beat="⚡ DUYGUSAL DORUK", mood="warm",
  v="In spring, the lambs are born. Some arrive on cold nights, too weak to stand. So we bring them inside, by the fire, wrapped in old felt. The first one this year is tiny and black. Saran names it Iron. Because it was born after the iron winter... and it lived.",
  img=f"Inside the family's ger at night, {GER_IN}: {SA} kneels by the hearth holding a tiny newborn black lamb wrapped in a piece of grey felt, {OY} beside her smiling, warm firelight",
  shots=["a tiny black lamb wrapped in felt lifts its head by the fire",
         "the little girl strokes the lamb's head and whispers to it",
         "the mother smiles in the warm firelight"],
  sound="soft crackling fire, a tiny lamb bleating, a child whispering",
  refs=["saran", "oyun", "ger_in"], must=["exactly one woman and one girl", "exactly one lamb"]),
 dict(title="How we survive", mode="stills", ambience_from=1, pov=True, beat="ÖZET: kurallar", mood="warm",
  v="So that is how we survive fifty below. A home that moves. A camp behind a hill. Felt, dung and dried meat, prepared in summer. Horses that dig. Goats that lead. A fire that never sleeps. Neighbours who help. And when the ice comes... the courage to leave. Families on the steppe still cross the winter this way today.",
  img="Spring on the Mongolian steppe: the white ger and the whole herd grazing on new green grass, mountains behind",
  stills=["Early spring on the Mongolian steppe, about 1900: a white felt ger on the first green grass, a whole mixed herd of horses, camels, cattle, sheep and goats grazing peacefully around it, snow only on the far mountains, soft golden light, NO people",
          f"The whole family outside their ger in the soft spring evening: {DO}, {OY}, {BA} and {SA} standing together, Saran holding the little black lamb"],
  sound="gentle spring wind, birds, distant bleating",
  refs=["dorj", "oyun", "bat", "saran", "steppe"], must=["exactly four people in the second image: one man, one woman, one boy, one girl"]),
 dict(title="Subscribe", mode="stills", ambience_from=3, pov=True, beat="CTA + abone vaadi (kanal adı yok)", mood="warm",
  v="If you've crossed this winter with me, thank you. Every week, I bring you one more winter that pushed ordinary people to their limit, told by the people who lived through it. If you want the next one, subscribe. And tell me: horses or sheep... which would you have saved?",
  img=f"{DO}'s weathered hands holding a steaming bowl of milk tea by the fire",
  stills=["Close warm painterly view of a herder's weathered hands holding a steaming wooden bowl of milk tea in front of a glowing ger hearth, an orange silk sash at the edge of the frame, NO face visible",
          "The roof ring of a ger seen from inside at night, red roof poles radiating out, stars visible through the opening, a thin line of smoke rising, NO people"],
  sound="soft crackling fire",
  refs=["ger_in"]),
 dict(title="What comes next", mode="stills", ambience_from=1, pov=False, beat="SONRAKİ BÖLÜM", mood="intrigue", own_rules=True,
  v="Far to the west, in medieval Europe, there were people who lived inside walls of stone a metre thick... and still froze. No glass in the windows. One fire for a hall full of people. How did they get through a winter night in a castle? That story is next. And here... the fire is still burning.",
  img="A medieval stone castle in deep winter snow at dusk, a few small windows glowing with firelight",
  stills=["A medieval European stone castle on a snowy hill at dusk in deep winter, thick stone walls and towers, a few narrow window slits glowing with orange firelight, heavy snow falling, NO people, NO modern objects",
          "Inside a medieval castle great hall in winter: a huge stone fireplace with a roaring fire at one end of a long stone hall, long wooden tables, tapestries on the walls, cold blue light at the narrow unglazed windows, NO people"],
  sound="howling wind against stone, a roaring fire",
  refs=[], must=["Romanesque or Gothic medieval European castle"], must_not=["Mongolia", "gers", "modern objects"]),
]

SHEET = ("Character reference sheet: on the left a full-body front view standing, "
         "on the right a chest-up portrait of the same person; identical original character in both views, single "
         "character only, no other people. ")
refs = {
 "dorj": {"kind": "character", "prompt": SHEET + DO},
 "oyun": {"kind": "character", "prompt": SHEET + OY},
 "bat": {"kind": "character", "prompt": SHEET + BA},
 "saran": {"kind": "character", "prompt": SHEET + SA},
 "ger_in": {"kind": "location", "prompt": "Location reference, single image, NO people: " + GER_IN + ", Mongolia about 1900, warm firelight, smoke rising through the roof ring, no stove pipe"},
 "steppe": {"kind": "location", "prompt": "Location reference, single image, NO people: the north-western Mongolian steppe in winter about 1900, a single round white felt ger with smoke from its roof ring on the sheltered south side of a low rocky hill, a low dry-stone animal pen beside it, endless snowy plain, distant snowy mountains, icy pale blue sky"},
}
for k, r in refs.items():
    r["n"] = k

ep = {
 "id": "ep006", "version": 1,
 "title": "How Do Mongolian Nomads Survive −50°C Winters?",
 "title_alt": "You're a Nomad on the Mongolian Steppe. It's −50°C.",
 "title_c": "The Iron Winter: How One Nomad Family Kept 200 Animals Alive",
 "thumbnail": "Bright painterly close-up: the herder's face with thick white frost on his eyelashes, moustache and fox-fur hat, a white felt ger and frosty horses behind on a blue icy steppe; one big word '−50°C' (B: 'FELT', C: no text)",
 "hook_description": "On the Mongolian steppe, winter can fall to fifty degrees below zero, and a family lives through it in a tent of felt, with two hundred animals that must all survive until spring. Dorj, a herder, tells how nomads cross the winter: the winter camp, the felt, the dung fire, the horses that dig, and the iron dzud.",
 "character": "Dorj, a fictional Mongolian herder in north-western Mongolia about 1900; his wife Oyun, son Bat (11) and daughter Saran (7)",
 "setting": "North-western Mongolia (around the Uvs basin, one of the coldest regions), from autumn to spring, about 1900: a nomadic herding family's winter camp, an iron dzud and an otor migration",
 "style": ("Hand-painted gouache and watercolor storybook illustration, visible brush texture, warm amber firelight "
           "against cold blue winter light, cinematic composition, historically accurate Mongolia about 1900: "
           "long deel robes tied with silk sashes, sheepskin-lined winter deels, fur hats with ear flaps, leather gutal "
           "boots with upturned toes; round white felt gers with wooden lattice walls, red roof poles and a roof ring, "
           "an open hearth with an iron fire-ring, shaggy Mongolian horses, two-humped Bactrian camels, fat-tailed sheep, "
           "no modern objects, soft painterly detail, no text, no letters, no watermark"),
 "ref_style": ("Hand-painted gouache and watercolor storybook character reference sheet, same painterly look as the episode, "
               "even neutral lighting, plain warm parchment background, historically accurate Mongolian herder clothing "
               "of about 1900, original person, no text, no labels, no watermark"),
 "motion_suffix": ("Gentle natural motion, soft cuts between shots, painterly style and characters stay consistent across shots, "
                   "no text; historically accurate Mongolia about 1900: felt gers, deel robes, fur hats, horses, camels, "
                   "sheep and goats, no modern objects, no stove pipes, no motorbikes, no cars, no electric lights"),
 "cast": {"Dorj": DO, "Oyun": OY, "Bat": BA, "Saran": SA},
 "preview_scenes": [1, 2, 3],
 "gates": {},
 "hybrid": {"still_resolution": "2k", "still_quality": "medium", "clip_start_resolution": "1k",
            "note": "mode=clip → Seedance; mode=stills → 2K görseller + Ken Burns, ortam sesi ambience_from klibinden"},
 "must": ["historically accurate Mongolia about 1900 only (except the final teaser scene)",
          "the same faces, hair and clothes as in the reference images for every named character",
          "painterly gouache look in every frame"],
 "must_not": ["any text, letters, numbers, captions, logos or watermark",
              "modern objects: stove pipes, iron stoves, solar panels, satellite dishes, motorbikes, cars, trucks, plastic, zippers, electric lights, metal buckets",
              "modern clothing: jeans, puffer jackets, sneakers, baseball caps",
              "Chinese, Tibetan or Native American clothing or tents instead of Mongolian; tipis; yurts with Central Asian decoration",
              "Bactrian camels with one hump (they always have two)",
              "gore, blood, corpses, skeletons, dead animals",
              "extra fingers, deformed hands, duplicated faces, animals with extra legs",
              "the same person appearing twice in one frame (clones, twins, duplicated characters)",
              "collage, multiple panels, split screen, several pictures in one image: it must be ONE single continuous scene"],
 "sources": [
  "Caroline Humphrey & David Sneath — The End of Nomadism? Society, State and the Environment in Inner Asia (Duke University Press, 1999)",
  "Sevyan Vainshtein — Nomads of South Siberia: The Pastoral Economies of Tuva (Cambridge University Press, 1980)",
  "Slawomir Szynkiewicz — 'Mongolia's Nomads Build a New Society Again' / works on Mongolian pastoral seasonal migration",
  "Troy Sternberg — 'Unravelling Mongolia's extreme winter disaster of 2010' (Nomadic Peoples, 2010) — on dzud types",
  "Daniel J. Murphy — 'Going on otor: disaster, mobility, and the political ecology of vulnerability in Uguumur, Mongolia' (PhD, Univ. of Kentucky, 2011)",
  "National Museum of Mongolia — collections and notes on the ger, felt-making and Tsagaan Sar",
 ],
 "disclosure": ("Dorj, Oyun, Bat and Saran are fictional characters, built from historical and ethnographic accounts of "
                "Mongolian nomadic herding. Illustrations and animation were created with AI tools; narration uses a "
                "synthetic voice."),
 "refs": refs,
 "music": [],
 "next_episode_tease": "A winter night inside a medieval castle: thick stone walls, no glass in the windows, one fire for the whole hall",
 "voice_engine": None,
 "scenes": [],
}
for s in scenes:
    if "dorj" in s["refs"]: s["pov"] = False  # anlatıcı görünüyorsa POV ifadesi çelişir
for i, s in enumerate(scenes, 1):
    sc = {"n": i, "title": s["title"], "mode": s["mode"], "pov": s["pov"], "narration": plain(s["v"]),
          "narration_voiced": s["v"], "image_prompt": s["img"], "sound": s["sound"], "refs": s["refs"],
          "voice_mood": s["mood"]}
    if s["mode"] == "clip":
        sc["shots"] = s["shots"]
    else:
        sc["still_prompts"] = s["stills"]
        sc["ambience_from"] = s["ambience_from"]
    for k in ("beat", "must", "must_not", "own_rules"):
        if s.get(k):
            sc[k] = s[k]
    ep["scenes"].append(sc)
ep005 = S.load_episode("ep005")
ep["voice_engine"] = ep005["voice_engine"]
ep["max_credits"] = 165
S.save_episode(ep)

# Karma bütçe (kredi): klip 7.5 + başlangıç görseli 1k (1) / 2K still 2 / ref 1
clips = [s for s in ep["scenes"] if s["mode"] == "clip"]
stills = sum(len(s["still_prompts"]) for s in ep["scenes"] if s["mode"] == "stills")
cost = len(clips) * (7.5 + 1) + stills * 2 + len(refs) * 1
w = [len(s["narration"].split()) for s in ep["scenes"]]
print(len(w), "sahne", sum(w), "kelime", min(w), max(w), "≈", round(sum(w)/2.81/1.06/60 + len(w)*0.6/60, 1), "dk")
print("klip:", [s["n"] for s in clips], "| still görsel:", stills, "| tahmini maliyet:", cost, "kredi")
