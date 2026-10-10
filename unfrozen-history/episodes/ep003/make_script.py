import json, re, sys
sys.path.insert(0, "/home/user/loftik-video-bot/unfrozen-history")
from uh import state as S

L = "Luc (French conscript soldier about 20, thin young face, dark curly hair, light stubble, dark blue French line infantry coat with white lapels under a worn grey-brown greatcoat, black shako with a brass plate)"
LW = "Luc (French conscript soldier about 20, thin frostbitten young face, dark curly hair, frost in his stubble, wrapped in a worn grey-brown greatcoat with a lady's dark fur-lined cloak over his shoulders, a wool scarf tied over his shako and ears)"
M = "Sergeant Morel (French veteran sergeant about 50, thick grey moustache, scarred weathered face, grey-brown greatcoat with sergeant's stripes on the sleeve, black shako, later a shaggy sheepskin coat)"
A = "Antoine (French conscript about 19, freckled face, short red hair, dark blue line infantry coat, grey-brown greatcoat, black shako)"
T = "Thérèse (French army cantinière about 35, strong face, dark hair under a red headscarf, short blue jacket, striped wool skirt, a small brandy keg on a leather strap)"

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

scenes = [
 dict(title="Never sit down", pov=True, beat="SOĞUK AÇILIŞ + FRAGMAN (0:00)", mood="tense",
  v="Thirty degrees below zero. My breath freezes on my scarf. All around me, men are sitting down in the snow... and they do NOT get up again. My sergeant gave me one rule: never sit down. My name is Luc. I am twenty years old, a soldier in Napoleon's army... and this is how I survived the Russian winter of 1812.",
  img="POV at night on a snowy Russian road in December 1812: the narrator's hands wrapped in rags held toward a small campfire, exhausted French soldiers in ragged greatcoats and furs huddled around other small fires in the snow, snow-covered shapes of men sitting motionless, dark birch forest",
  shots=["the narrator's rag-wrapped hands tremble over a small fire in the snow",
         "soldiers in ragged greatcoats huddle around small fires along a snowy road at night",
         "snow slowly covers a motionless figure sitting by a dying fire"],
  sound="howling wind, crackling fire, boots crunching on frozen snow", refs=["luc", "bivouac"]),
 dict(title="June 1812", pov=False, mood="intrigue",
  v="Six months earlier. June 1812. The biggest army the world has ever seen crosses the river Niemen into Russia. More than four hundred thousand men: French, Poles, Germans, Italians, Dutch. Nobody thinks about winter. It is so HOT that men faint on the road. 'We'll be home before the leaves fall,' everyone says.",
  img="Summer 1812: endless columns of Napoleonic infantry in dark blue coats and white trousers, cavalry and wagons crossing pontoon bridges over a wide river under a hot hazy sky, dust rising, flags and drums, green fields beyond",
  shots=["long columns of soldiers march across pontoon bridges over a wide river",
         "drummers beat drums, regimental flags wave in the hot wind",
         "dust rises from the road as the army marches east into green fields"],
  sound="drums, thousands of marching feet, horses, distant cheering", refs=[]),
 dict(title="My company", pov=False, mood="warm",
  v="I am a fusilier from a little village in the Auvergne mountains. Next to me marches Antoine, my friend since we were children. Our sergeant is Morel. He fought in Egypt, and he complains about everything. And behind us rolls the cart of Thérèse, our cantinière. She sells brandy, sews buttons... and knows everything.",
  img=f"On a dusty summer road in Lithuania: {L} and {A} marching side by side and laughing, {M} walking ahead with a grumpy face, {T} driving a small covered cart pulled by a brown horse behind them",
  shots=[f"{L} and {A} march side by side, laughing at a joke",
         f"{M} turns around and grumbles at them",
         f"{T} drives her small covered cart and waves"],
  sound="marching feet, cart wheels creaking, laughter, a horse snorting", refs=["luc", "antoine", "morel", "therese", "cart"]),
 dict(title="An empty land", pov=True, mood="intrigue",
  v="But Russia does not fight us. Russia just... goes away. Every village we reach is empty, the barns burned, the food gone. We march hundreds of kilometres in the heat and the dust. The horses die first, thousands of them, from bad fodder and storms. Morel looks at them and says: 'Remember this, boy. The horses always tell you what's coming.'",
  img="POV marching into an abandoned Russian village in summer 1812: empty wooden log houses, a burned barn still smoking, dead horses at the roadside, soldiers in blue coats looking around, hot dusty light",
  shots=["the column passes empty wooden log houses with open doors",
         "a burned barn smokes beside the road",
         f"{M} stops beside a fallen horse and looks back at the narrator"],
  sound="cicadas, distant smoke crackling, flies buzzing, tired footsteps", refs=["morel"]),
 dict(title="Morel's rules", pov=False, mood="intrigue", lipsync=True,
  v="Let me tell you about Sergeant Morel. He has rules. A rule for EVERYTHING. Sleep with your boots under your head. Never drink water you haven't boiled. And the most important one... I didn't understand it in the summer. But I will. Soon.",
  img=f"Medium close-up of {L} sitting on a wooden crate at a summer army camp at dusk, looking straight into the camera as if talking to the viewer, a campfire glowing beside him, tents and soldiers softly out of focus behind",
  shots=["Luc looks straight into the camera and speaks to the viewer"],
  sound="a campfire crackling, distant voices of a camp", refs=["luc"]),
 dict(title="Moscow", pov=False, mood="intrigue",
  v="In September, after one terrible battle near a village called Borodino, the road to Moscow is open. On the fourteenth of September we march into the city... and it is EMPTY. Golden domes, palaces, streets full of shops, and almost no people. We think the war is over. We think we have won.",
  img="September 1812: French infantry columns marching into an empty Moscow street, golden onion domes and white churches, grand houses with closed shutters, no residents, soldiers looking around in wonder",
  shots=["golden onion domes shine above an empty street",
         "French soldiers march between grand houses with closed shutters",
         f"{A} stares up at the domes with his mouth open"],
  sound="echoing footsteps in an empty street, church bells silent, wind", refs=["moscow", "antoine"]),
 dict(title="Moscow burns", pov=True, beat="⚡ KIRILMA 1 (~1:50): Moskova yanıyor", mood="tense",
  v="That night, the fires start. One, then ten, then hundreds. The wind carries them from street to street. For four days, Moscow burns, and most of the city is gone. And we, the soldiers... we run INTO the burning houses, and grab whatever we can carry.",
  img="Night in Moscow, September 1812: whole streets of wooden and stone houses in flames, a red sky full of sparks and smoke, French soldiers running out of burning houses carrying loot",
  shots=["flames climb the walls of wooden houses under a red sky",
         "the wind blows a storm of sparks across the street",
         "soldiers run out of a burning house carrying silver, silk and paintings"],
  sound="roaring fire, collapsing timber, shouting, wind", refs=["moscow"]),
 dict(title="Furs, not silver", pov=False, mood="intrigue",
  v="Antoine fills his pack with silver spoons and a little golden icon. Others take paintings, silk, wine. Morel takes something strange: a heavy, ugly sheepskin coat. We laugh at him. It is September, the sun is warm. He just says: 'Take furs, boys. Silver won't keep you warm.' So I go back... and find a lady's fur-lined cloak. Antoine laughs at me all night.",
  img=f"Inside a half-burned Moscow mansion: {A} stuffing silver spoons into his pack, {M} holding up a shaggy sheepskin coat, {L} holding a lady's dark fur-lined cloak and looking embarrassed",
  shots=[f"{A} stuffs silver spoons and a small golden icon into his pack",
         f"{M} holds up a shaggy sheepskin coat with a serious face",
         f"{A} laughs and points at {L}, who holds a lady's fur-lined cloak"],
  sound="clinking silver, laughter, distant fire crackling", refs=["antoine", "morel", "luc"]),
 dict(title="The Emperor's weather", pov=False, mood="intrigue",
  v="We wait in Moscow for five weeks. The Emperor waits for the Tsar to ask for peace. The Tsar never answers. The autumn is mild and sunny. 'The Emperor's weather,' we call it. And every day we stay... winter comes one day closer.",
  img="Golden autumn light over the burned ruins of Moscow, October 1812: blackened chimneys of burned houses among surviving churches, French soldiers sitting idly in the sun playing cards, yellow leaves on the ground",
  shots=["soldiers play cards in the sun among blackened ruins",
         "yellow leaves blow across an empty square",
         "a single snowflake drifts down past a golden dome"],
  sound="gentle wind, cards slapping, distant church bells, leaves rustling", refs=["moscow"]),
 dict(title="The retreat", pov=True, mood="tense",
  v="On the nineteenth of October, we finally leave. About a hundred thousand men, and behind us a river of carts full of loot, kilometres long. Morel looks at the carts and spits. 'They're carrying their own graves.' We march west, back the way we came, through a land we have already stripped bare.",
  img="October 1812: the French army leaving Moscow on a muddy road, a long column of soldiers followed by an endless line of overloaded carts, carriages and wagons piled with loot, grey sky, bare birch trees",
  shots=["an endless line of carts piled with loot rolls out of the city",
         f"{M} watches the carts and shakes his head",
         "the column marches west across a bare grey plain"],
  sound="wheels creaking, mud squelching, horses straining, a cold wind rising", refs=["morel", "cart"]),
 dict(title="First snow", pov=False, beat="⚡ KIRILMA 2 (~3:40): İlk kar, buzda atlar", mood="tense",
  v="At the beginning of November... the first snow. At first, it is almost beautiful. The next day, the road is ICE. Our horses' shoes have no spikes for ice. They slip, they fall, and they cannot get up. In one day, I see more dead horses than in my whole life.",
  img="Early November 1812: heavy snow falling on a Russian road, horses slipping and falling on the icy road, soldiers trying to pull them up, overturned carts, grey white sky",
  shots=["the first snowflakes fall on the marching column",
         "a horse slips on the ice and crashes down, soldiers try to lift it",
         "dead horses and overturned carts line the white road"],
  sound="wind with snow, a horse neighing in panic, hooves sliding on ice", refs=["bivouac"]),
 dict(title="Leaving Moscow behind", pov=True, mood="tense",
  v="Without horses, the carts stop. The cannons stop. The loot stays in the snow. Antoine drops his silver spoons on the road one by one, because they are too heavy. Paintings, chandeliers, gold... half of Moscow lies along the road. And it is getting colder.",
  img=f"A snowy road in November 1812 littered with abandoned treasures: an overturned carriage, a gilded painting frame, a chandelier half-buried in snow; {A} dropping silver spoons into the snow as he walks",
  shots=["an abandoned carriage and a gilded painting lie in the snow",
         f"{A} lets silver spoons fall one by one into the snow",
         "snow slowly covers a crystal chandelier lying on the road"],
  sound="wind, snow crunching, metal clinking softly into snow", refs=["antoine", "bivouac"]),
 dict(title="Horse meat", pov=False, mood="intrigue",
  v="Now the horses become our food. When one falls, men run to it with knives. We roast the meat over the fire, black outside, raw inside. We have no salt, so some men sprinkle gunpowder on it. I tried it once. It tastes like... a battle.",
  img=f"Evening bivouac in the snow: {M} roasting pieces of meat on a bayonet over a small fire, {L} and {A} watching hungrily, a powder horn beside them",
  shots=[f"{M} holds a piece of meat on a bayonet over the flames",
         "a pinch of black gunpowder is sprinkled over the roasting meat",
         f"{L} bites the meat and makes a face"],
  sound="fire crackling, meat sizzling, wind, a soldier coughing", refs=["morel", "luc", "antoine", "bivouac"]),
 dict(title="Rule number one", pov=False, mood="tense", lipsync=True,
  v="And here it is. Morel's first rule. Never. Sit. Down. When you are this tired and this cold, the snow feels soft. Even warm. You sit down for one minute, just to rest... and you fall asleep. And you never wake up. Walk. Always walk.",
  img=f"Medium close-up of {LW} standing on a snowy road in grey daylight, looking straight into the camera as if talking to the viewer, snow falling, the retreating column passing softly out of focus behind him",
  shots=["Luc looks straight into the camera and speaks to the viewer"],
  sound="wind, falling snow, distant marching", refs=["luc", "bivouac"]),
 dict(title="Nights in the open", pov=True, mood="intrigue",
  v="At night, we sleep around fires in the open. No tents, no houses. Men fight for a place near the flames. The ones in front burn their coats, the ones behind freeze. Morel makes us lie close together, back to back, under one blanket, feet toward the fire. In the morning... we count who is still alive.",
  img=f"Night bivouac in deep snow: {M}, {A}, {T} and the narrator lying back to back under one blanket with their feet toward a fire, other soldiers crowding around fires in the darkness",
  shots=["soldiers push and shove for a place near the fire",
         f"{M}, {A} and {T} lie back to back under one blanket, feet to the fire",
         "grey dawn light over a silent snowy camp"],
  sound="fire crackling, wind, men coughing, snow hissing in the flames", refs=["morel", "antoine", "therese", "bivouac"]),
 dict(title="Smolensk", pov=False, mood="intrigue",
  v="Everyone dreams of Smolensk. There are warehouses there, they say: flour, biscuits, brandy, enough for the whole army. When we arrive, the first soldiers have already broken in. Men fight over sacks in the street. Thérèse trades her last keg of brandy for half a sack of flour. That half sack keeps four people alive for ten days.",
  img=f"November 1812, a snowy street of Smolensk below old fortress walls: starving soldiers fighting over flour sacks outside a broken warehouse door, {T} handing over a small brandy keg for half a sack of flour",
  shots=["soldiers break down a warehouse door and fight over sacks",
         f"{T} hands over her small brandy keg",
         f"{T} hugs half a sack of flour, {L} and {A} beside her"],
  sound="shouting, wood splintering, wind, coins clinking", refs=["therese", "luc", "antoine"]),
 dict(title="Frozen hands", pov=True, mood="intrigue",
  v="Then the cold drops again. Twenty below. Twenty-five. Ears and noses turn white... then black. The army's surgeon, Baron Larrey, warns us: never put a frozen hand straight into the fire. Rub it with snow, warm it slowly. The men who run to the flames... lose their fingers.",
  img="POV close-up: the narrator's white frostbitten fingers being rubbed with snow by the hands of an older soldier, a fire glowing at a distance, other soldiers in the background holding hands too close to the flames",
  shots=["the narrator's fingers are white and stiff with frost",
         "an older soldier rubs the frozen hand gently with snow",
         "in the background, a soldier pushes his hands right into the flames"],
  sound="wind, snow scrunching between hands, a man groaning in pain", refs=["bivouac"]),
 dict(title="Lice", pov=False, mood="intrigue",
  v="And there is another enemy. A tiny one. Lice. We haven't washed in months. They live in our coats, our hair, our beards. With them comes the fever: typhus. It kills more men than all the Russian armies. Every evening, Thérèse makes us shake our shirts over the fire. They crackle... like grains of salt.",
  img=f"Evening by a fire in the snow: {T} holding a shirt over the flames and shaking it, {L} and {A} scratching their heads, sparks rising",
  shots=[f"{T} shakes a shirt over the fire, tiny sparks crackling",
         f"{A} scratches his head and neck",
         f"{T} hands the shirt back with a firm look"],
  sound="fire crackling and popping, wind, a woman muttering", refs=["therese", "luc", "antoine", "bivouac"]),
 dict(title="Antoine", pov=False, beat="⚡ KIRILMA 3 (~6:20): Antoine", mood="tense",
  v="In the middle of November, Antoine gets the fever. He shivers, then burns, then shivers again. Morel and I carry him between us for two days. On the third night, he gives me his little golden icon. 'Take it home to my mother.' Then he sits down by the fire... and in the morning, he doesn't wake up.",
  img=f"Night by a fire in the snow: pale feverish {A} wrapped in a blanket, pressing a small golden icon into {L}'s hand, {M} watching in silence",
  shots=[f"{L} and {M} carry {A} between them along the snowy road",
         f"{A} presses a small golden icon into {L}'s hand by the fire",
         "in grey dawn light, snow lies untouched on a blanket by a cold fire"],
  sound="wind, a weak cough, a fire dying out", refs=["antoine", "luc", "morel", "bivouac"]),
 dict(title="Walking for two", pov=True, mood="tense",
  v="I put his icon inside my shirt, next to my heart. I want to stop. I want to sit down too. Morel grabs me by the collar. 'You're walking for two now, boy. WALK.' And so I walk. Every step... for Antoine.",
  img=f"On a grey snowy road: {M} gripping the narrator's collar with both hands and shouting into his face, the column marching past, snow falling",
  shots=[f"{M} grabs the narrator by the collar and shouts",
         "the narrator's hand presses a small golden icon to his chest",
         "the narrator's feet, wrapped in rags, step forward into deep snow"],
  sound="wind, a gruff shout, boots crunching on snow", refs=["morel", "bivouac"]),
 dict(title="Cossacks", pov=False, mood="tense",
  v="We are never alone. Cossacks ride beside the column, like wolves following a herd. Anyone who falls behind, anyone who wanders off to find firewood... disappears. So we march in a group, muskets ready. Alone, you are dead. Together, you might live.",
  img="A snowy plain at dusk: a small group of Cossack horsemen with long lances watching from the edge of a birch forest as the ragged French column marches past, soldiers in a tight group with muskets ready",
  shots=["Cossack riders with long lances watch from the edge of the forest",
         "a straggler alone in the snow looks over his shoulder",
         "soldiers close ranks with muskets raised"],
  sound="wind, distant hoofbeats, muskets clicking", refs=["bivouac"]),
 dict(title="The Berezina", pov=False, beat="⚡ KIRILMA 4 (~7:30): Berezina", mood="tense",
  v="At the end of November we reach the river Berezina. The bridge is burned, and Russian armies are closing in from every side. We are trapped. Then the engineers do something impossible. They walk into the freezing river, up to their chests in water full of ice, and build two bridges.",
  img="November 1812, the Berezina river: engineers standing chest-deep in icy black water among floating ice, hammering wooden trestles for a bridge, crowds of soldiers waiting on the snowy bank, grey sky",
  shots=["ice floats on the black water of a wide river",
         "engineers wade into the river up to their chests carrying beams",
         "men hammer wooden trestles in the freezing water"],
  sound="water lapping against ice, hammering, wind, men gasping from cold", refs=[]),
 dict(title="The engineers", pov=False, mood="tense",
  v="Most of them are Dutch, these engineers. For hours they stand in the black water, hammering wood while the ice cuts their skin. When they come out, some are frozen too stiff to move. Most of them won't live to see the spring. But because of them... thousands of us will.",
  img="Close view of exhausted engineers climbing out of the icy river, their clothes frozen stiff, ice in their beards, comrades wrapping them in blankets by a fire on the bank",
  shots=["an engineer climbs out of the water, his clothes stiff with ice",
         "comrades wrap him in a blanket by a fire",
         "the finished wooden bridge stretches across the icy river"],
  sound="dripping water, teeth chattering, fire crackling", refs=[]),
 dict(title="The crossing", pov=True, mood="tense",
  v="The crossing is chaos. Thousands push toward the bridges at once: soldiers, wounded, women, children. Cannonballs fall among us. Thérèse's cart can't pass, so she cuts her horse free and walks. Morel holds my belt and shouts, 'Don't let go!' We cross. Behind us, the bridges burn.",
  img=f"POV in a desperate crowd crossing a narrow wooden bridge over an icy river in the snow, {M} ahead gripping the narrator's belt, {T} leading her horse, smoke and snow in the air",
  shots=["a huge crowd pushes toward a narrow wooden bridge",
         f"{M} looks back and holds the narrator's belt tight",
         "behind them, the wooden bridge goes up in flames"],
  sound="crowd shouting, distant cannon fire, wood creaking, fire", refs=["morel", "therese"]),
 dict(title="Minus thirty", pov=False, mood="tense",
  v="December. The worst cold anyone can remember. Thirty below zero. Birds fall frozen from the sky. Our breath freezes in our beards. I wear everything I have: my greatcoat, the lady's fur cloak from Moscow... and pieces of blanket wrapped around my feet, because my boots have fallen apart.",
  img=f"December 1812, a frozen white landscape: {LW} trudging through deep snow, his feet wrapped in rags and blanket strips, frost on his eyebrows and stubble, a small frozen bird on the snow",
  shots=["a small frozen bird lies on the white snow",
         f"{LW} trudges forward, frost on his eyebrows",
         "his rag-wrapped feet sink into deep snow"],
  sound="deep silent cold, snow creaking underfoot, faint wind", refs=["luc", "bivouac"]),
 dict(title="Vilnius", pov=False, mood="tense",
  v="On the fifth of December, the Emperor leaves us, racing back to Paris in a sleigh. A few days later we reach Vilnius. There is food there at last. But many men are so hungry and so frozen that they die in the streets... within sight of the bread.",
  img="Night, December 1812: a small sleigh with a closed carriage body and a few escort riders speeding away across the snow, seen from far away; in the distance, the towers of a snowy city",
  shots=["a sleigh with escort riders races away across the snow at night",
         "the ragged column approaches the snowy towers of Vilnius",
         "soldiers crowd at the door of a bakery, bread passed out over heads"],
  sound="sleigh bells fading, wind, a crowd murmuring", refs=[]),
 dict(title="The Niemen again", pov=False, mood="relief",
  v="In the middle of December, I cross the river Niemen again: the same river we crossed in June with music and flags. In June, I was one of more than four hundred thousand. Now, I can count the men around me. Morel limps beside me. Thérèse walks behind us. We are three. But we are ALIVE.",
  img=f"December 1812, the frozen Niemen river: a handful of ragged survivors crossing the ice in the grey dawn, {M} limping, {T} wrapped in a shawl, {LW} between them",
  shots=["a handful of ragged survivors cross the frozen river at dawn",
         f"{M} limps forward leaning on a musket",
         f"{T} puts a hand on {L}'s shoulder"],
  sound="ice creaking, wind, slow footsteps", refs=["morel", "therese", "luc"]),
 dict(title="How I survived", pov=False, mood="warm", lipsync=True,
  v="So how did I survive the Russian winter? I took furs, not silver. I never sat down. I warmed my frozen hands slowly. I shook the lice into the fire. I ate horse... with gunpowder. And I never, ever walked alone.",
  img=f"Medium close-up of {LW} sitting by a small fire in a quiet snowy forest at dusk, looking straight into the camera as if talking to the viewer, warm firelight on his tired face",
  shots=["Luc looks straight into the camera and speaks to the viewer"],
  sound="soft fire crackling, quiet forest, light wind", refs=["luc", "bivouac"]),
 dict(title="Home", pov=False, mood="outro",
  v="In the spring of 1813, I come home to my village in the Auvergne. I've lost two toes... and my youth. The first thing I do is climb the hill to Antoine's mother, and give her the little golden icon. My name is Luc Bastien, and I survived the winter of 1812. But mine was not the only hard winter in history.",
  img=f"Spring 1813 in a green mountain village of the Auvergne: thin {L} in a worn greatcoat handing a small golden icon to an old woman in a black shawl at the door of a stone farmhouse, spring flowers",
  shots=[f"{L} walks up a green hill path toward a stone farmhouse",
         "an old woman in a black shawl opens the door",
         "the small golden icon passes from his hand into hers"],
  sound="birdsong, a gentle breeze, a door creaking", refs=["luc"]),
 dict(title="What comes next", pov=False, beat="BİTİŞ EKRANI (son 20 sn)", mood="outro",
  v="Thirty-four years later, on the other side of the world, a family of American settlers takes a shortcut through the mountains of California. Then the snow begins to fall... and it does not stop. How did they survive? That story is next. And here, the fire is still burning.",
  img="1846: a small wagon train of covered wagons climbing toward snowy mountain passes under a darkening sky, the first snowflakes falling, a campfire glowing beside the wagons",
  shots=["covered wagons climb a mountain trail toward snowy peaks",
         "the first snowflakes fall on the white canvas of a wagon",
         "a campfire glows beside the wagons as night falls"],
  sound="wind in pine trees, wagon wheels creaking, a gentle fire", refs=[]),
]

SHEET = ("Character reference sheet: on the left a full-body view standing upright facing the viewer, head to toe, "
         "on the right a chest-up portrait of the same person; identical original character in both views, single "
         "character only, no other people, no props except those described. ")
refs = {
 "luc": {"kind": "character", "prompt": SHEET + "Luc, French conscript soldier of 1812 about 20, thin young face, dark curly hair, light stubble, brown eyes, dark blue French line infantry coat (habit-veste) with white lapels and red cuffs, white crossbelts, grey-brown greatcoat open over it, white trousers with black gaiters, black shako with a brass plate, musket on his shoulder"},
 "morel": {"kind": "character", "prompt": SHEET + "Sergeant Morel, French veteran infantry sergeant of 1812 about 50, thick grey moustache, scarred weathered face, grey-brown greatcoat with sergeant's stripes on the sleeves, black shako, white crossbelts, musket"},
 "antoine": {"kind": "character", "prompt": SHEET + "Antoine, French conscript soldier of 1812 about 19, freckled boyish face, short red hair, dark blue French line infantry coat with white lapels, white crossbelts, grey-brown greatcoat, black shako"},
 "therese": {"kind": "character", "prompt": SHEET + "Thérèse, French army cantinière of 1812 about 35, strong friendly face, dark hair under a red headscarf, short blue military-style jacket, striped wool skirt to mid-calf, boots, a small painted brandy keg on a leather strap"},
 "cart": {"kind": "location", "prompt": "Reference, a small canvas-covered two-wheeled cantinière's cart of the Napoleonic army pulled by one brown horse, barrels and bundles tied on the back, on a dirt road"},
 "moscow": {"kind": "location", "prompt": "Location reference, wide establishing view of Moscow in September 1812: golden and blue onion domes, white stone churches, grand houses and many wooden houses, wide streets, the Kremlin walls in the distance, no people, no modern buildings"},
 "bivouac": {"kind": "location", "prompt": "Location reference, wide establishing view of a snowy Russian road in November 1812: a flat white plain with dark birch and pine forest, the road trampled by an army, small campfires in the snow, abandoned wagons half-buried in snow, grey winter sky, no modern objects"},
}
for k, r in refs.items():
    r["n"] = k

ep = {
 "id": "ep003", "version": 1,
 "title": "You're a Soldier in Napoleon's Army. It's −30°C.",
 "title_alt": "How Napoleon's Soldiers Survived the Russian Winter of 1812",
 "thumbnail": "Painterly close-up of Luc's young frost-covered face, ice in his eyebrows and stubble, wool scarf tied over his shako, night snow, lit from below by a small campfire; text: 'DON'T SIT DOWN' (A/B test against '−30°C')",
 "hook_description": "How did anyone survive Napoleon's retreat from Moscow in 1812, with no food, no shelter and thirty degrees below zero? Luc, a twenty-year-old French conscript, tells you how he made it home.",
 "character": "Luc Bastien, a fictional twenty-year-old French conscript (fusilier of the line) from the Auvergne, Russian campaign of 1812",
 "setting": "Napoleon's invasion of Russia and the retreat from Moscow, June to December 1812",
 "style": ("Hand-painted gouache and watercolor storybook illustration, visible brush texture, warm amber firelight against "
           "cold blue winter light, cinematic composition, historically accurate Napoleonic Wars 1812: French line infantry "
           "in dark blue coats with white lapels, grey-brown greatcoats and black shakos, flintlock muskets, Russian wooden "
           "log villages and onion-domed churches, horse-drawn carts, no modern objects, soft painterly detail, "
           "no text, no letters, no watermark"),
 "ref_style": ("Hand-painted gouache and watercolor storybook character reference sheet, same painterly look as the episode, "
               "even neutral lighting, plain warm parchment background, historically accurate 1812 Napoleonic military "
               "clothing, original fictional person, no text, no labels, no watermark"),
 "motion_suffix": ("Gentle natural motion, soft cuts between shots, painterly style and characters stay consistent across shots, "
                   "no text; historically accurate 1812: flintlock muskets, shakos, horse-drawn carts and sleighs, "
                   "no modern objects, no vehicles with engines, no electric lights"),
 "cast": {"Luc": L, "Morel": M, "Antoine": A, "Thérèse": T},
 "preview_scenes": [1, 2, 3],
 "gates": {},
 "sources": [
  "Adam Zamoyski — 1812: Napoleon's Fatal March on Moscow (HarperCollins, 2004)",
  "Dominic Lieven — Russia Against Napoleon (Allen Lane, 2009)",
  "Sergeant Adrien Bourgogne — Memoirs of Sergeant Bourgogne, 1812–1813 (first published 1898)",
  "Jakob Walter — The Diary of a Napoleonic Foot Soldier (ed. Marc Raeff, 1991)",
  "Armand de Caulaincourt — With Napoleon in Russia (memoirs, ed. 1933)",
  "Dominique-Jean Larrey — Memoirs of Military Surgery (1812–1817)",
  "Stephan Talty — The Illustrious Dead: The Terrifying Story of How Typhus Killed Napoleon's Greatest Army (2009)",
  "Philippe-Paul de Ségur — History of the Expedition to Russia, 1812 (1824)",
 ],
 "disclosure": ("Luc, Morel, Antoine and Thérèse are fictional characters, built from the memoirs of soldiers who survived the "
                "1812 campaign and from historical research. Illustrations and animation were created with AI tools; "
                "narration uses a synthetic voice."),
 "refs": refs,
 "music": [
  {"from": 1, "track": "Frozen_Star.mp3", "title": "Frozen Star", "mood": "soğuk açılış"},
  {"from": 2, "track": "Lost_Frontier.mp3", "title": "Lost Frontier", "mood": "yaz yürüyüşü"},
  {"from": 7, "track": "Darkest_Child.mp3", "title": "Darkest Child", "mood": "Moskova yanıyor"},
  {"from": 9, "track": "Ossuary_6_-_Air.mp3", "title": "Ossuary 6 - Air", "mood": "bekleyiş, geri çekiliş"},
  {"from": 11, "track": "Dark_Times.mp3", "title": "Dark Times", "mood": "ilk kar, açlık"},
  {"from": 16, "track": "Crossing_the_Chasm.mp3", "title": "Crossing the Chasm", "mood": "hayatta kalma kuralları"},
  {"from": 19, "track": "Winter_Reflections.mp3", "title": "Winter Reflections", "mood": "Antoine"},
  {"from": 22, "track": "Long_Note_Four.mp3", "title": "Long Note Four", "mood": "Berezina"},
  {"from": 27, "track": "Dreams_Become_Real.mp3", "title": "Dreams Become Real", "mood": "kurtuluş, eve dönüş"},
 ],
 "next_episode_tease": "The Donner Party, 1846–47: an American settler family trapped by snow in the Sierra Nevada",
 "voice_engine": None,
 "scenes": [],
}
for i, s in enumerate(scenes, 1):
    sc = {"n": i, "title": s["title"], "pov": s["pov"], "narration": plain(s["v"]), "narration_voiced": s["v"],
          "image_prompt": s["img"], "shots": s["shots"], "sound": s["sound"], "refs": s["refs"], "voice_mood": s["mood"]}
    if s.get("beat"):
        sc["beat"] = s["beat"]
    if s.get("lipsync"):
        sc.update(lipsync=True, min_speed=1.0, no_ambience=True)
    ep["scenes"].append(sc)
ep002 = S.load_episode("ep002")
ep["voice_engine"] = ep002["voice_engine"]
ep["max_credits"] = 330
ep["music_credit"] = ("Music by Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0 — "
                      + ", ".join(f"\"{m['title']}\"" for m in ep["music"]))
S.save_episode(ep)
w = [len(s["narration"].split()) for s in ep["scenes"]]
print(len(w), "sahne", sum(w), "kelime", min(w), max(w), "≈", round(sum(w)/2.81/1.06/60 + len(w)*0.6/60, 1), "dk")
print(S.estimate(ep))
