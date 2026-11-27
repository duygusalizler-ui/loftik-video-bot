import json, re, sys
sys.path.insert(0, "/home/user/loftik-video-bot/unfrozen-history")
from uh import state as S

# Kurgusal anlatıcı: Danny Moore (19, er, 7. Deniz Piyade Alayı, 1. Deniz Piyade Tümeni) ve siper arkadaşı Ray.
# Olaylar gerçek: Chosin Rezervuarı muharebesi, 27 Kas – 11 Ara 1950 (Kuzey Kore). Kitle verisi (STRATEGY §25):
# 55+ erkek, ABD ağırlıklı → sıcaklık °F ağırlıklı (°C parantezde), askerî ayrıntı, sade anlatım.
# Doğrulama notları: Tootsie Roll'ların "yanlışlıkla atıldığı" hikâyesi tartışmalı → kesin söylenmiyor;
# köprü atma tarihi ve Koto-ri yıldızının saati kaynaklarda farklı → tarih verilmiyor; kayıp sayısı verilmiyor.
# Gerçek kişiler (Gen. O. P. Smith vb.) GÖSTERİLMEZ. Şiddet: kan/ceset yok, çatışma ışık-ses ile anlatılır.
# KARMA YÖNTEM: mode="clip" Seedance klibi, mode="stills" 2K görsel + Ken Burns (STRATEGY §17).
DA = "Danny (fictional American Marine private, 19, thin boyish face, light stubble, blue-grey eyes, red cheeks chapped by cold, wearing a long olive-drab hooded field parka with the hood down, an olive-drab pile cap with fur-lined ear flaps tied under the chin under a plain M1 steel helmet, olive wool gloves, rubber-bottomed shoepac boots)"
RA = "Ray (fictional American Marine private, 22, broad dark-haired, thick black eyebrows, dark stubble, same long olive-drab hooded parka, pile cap with ear flaps under a plain M1 steel helmet, a Browning Automatic Rifle slung on his shoulder)"
MAR = "American Marines of 1950 in long olive-drab hooded parkas, pile caps with ear flaps under plain M1 steel helmets, rubber-bottomed shoepac boots, M1 rifles"
CPV = "Chinese soldiers of 1950 in thick padded cotton winter uniforms of faded mustard-khaki, padded caps with ear flaps, thin canvas shoes"

def plain(v):
    s = re.sub(r"\.\.\.\s*(?=[a-z])", " ", v)
    s = re.sub(r"\.\.\.\s*(?=['A-Z])", ". ", s).replace("...", ".").replace(" — ", ", ").replace("—", ", ")
    def fix(m):
        w = m.group(0)
        return w if w in ("I", "A", "BAR") else w.lower()
    s = re.sub(r"\b[A-Z]{2,}\b", fix, s)
    s = re.sub(r"([.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), s)
    s = re.sub(r"\.\s*\.", ".", s)
    return s[0].upper() + s[1:]

ROAD = "a narrow frozen dirt road winding through steep snow-covered mountains of North Korea, bare rocky ridges, scattered dark pine trees, a frozen reservoir glimpsed below"

scenes = [
 # ───────── İLK ~60 SN: KLİP ─────────
 dict(title="Thirty-five below", mode="clip", pov=False, beat="SOĞUK AÇILIŞ (0:00) — kanca ilk 3 sn", mood="tense",
  v="Thirty-five degrees below zero. My rifle is frozen. My canteen is a block of ice. And somewhere in those hills... there are more than a hundred thousand men who want us off this mountain. The only way out is one narrow road. Seventy-eight miles long.",
  img=f"Night on a snowy mountain ridge in North Korea, December 1950, extreme cold, snow falling in the glow of a hanging white flare: {DA} crouches in a shallow snow-covered foxhole, frost white on his eyebrows and ear flaps, his breath a thick cloud, gripping an M1 rifle, dark ridges behind",
  shots=["a hard gust of wind throws snow across the young Marine's frost-white face, he squints and tightens his grip on the rifle",
         "a white parachute flare drifts down over a dark snowy ridge, lighting the falling snow",
         "a long column of tiny dark figures and trucks on a winding mountain road far below, in the snow"],
  sound="howling mountain wind, a distant bugle call, snow hissing",
  refs=["danny", "ridge"], must=["exactly one person in the foreground", "a plain M1 steel helmet with no cover"]),
 dict(title="Who I am", mode="clip", pov=False, mood="warm",
  v="My name is Danny Moore. I'm nineteen, a private in the Seventh Marines, First Marine Division. Back home in Pennsylvania, my dad works in the steel mill. I joined the Marines to see the world. I didn't know the world could get this cold.",
  img=f"A cold grey morning in a Marine camp in North Korea, November 1950: {DA} sits on an ammunition crate beside a canvas squad tent, reading a folded letter from home, other Marines and a jeep blurred in the background, light snow on the ground",
  shots=["the young Marine reads a letter and smiles a little, his breath steaming",
         "his gloved hand folds the letter and tucks it inside his parka",
         "he looks up at the snowy mountains to the north"],
  sound="wind flapping canvas, distant engines, boots crunching on snow",
  refs=["danny", "camp"], must=["one main person in focus"]),
 dict(title="Home by Christmas", mode="clip", pov=False, mood="warm",
  v="That November, we thought the war was almost over. We were pushing north toward the Chinese border, and the word was we'd be home by Christmas. We even got turkey for Thanksgiving. My buddy Ray said the toughest thing up north would be the mail service.",
  img=f"Thanksgiving 1950 at a Marine camp in North Korea: {RA} laughing and {DA} grinning as they eat turkey from metal mess kits, sitting on crates outside a tent, steam rising from the food, snowy hills behind",
  shots=["Ray laughs with his mouth full, turkey steaming in his mess kit",
         "Danny grins and raises his tin cup",
         "a line of Marines waits with mess kits beside a field kitchen, steam rising"],
  sound="men laughing, metal mess kits clinking, wind",
  refs=["danny", "ray", "camp"], must=["exactly two main people in front"]),
 # ───────── YUKARI (görseller) ─────────
 dict(title="How we got here", mode="stills", ambience_from="Who I am", pov=False, mood="intrigue",
  v="Here's how we got there. In June of nineteen-fifty, North Korea invaded the South. By September, we Marines had landed at Inchon, behind their lines, and the whole North Korean army fell apart. We chased them north, all the way up the peninsula. It looked like the war was won.",
  img="A painterly scene of landing craft approaching a harbour city",
  stills=["Painterly view of US Navy landing craft full of Marines approaching a harbour sea wall at Inchon, Korea, September 1950, smoke over the city, grey sea, NO legible text",
          f"Autumn 1950: a long column of {MAR.replace('long olive-drab hooded parkas, pile caps with ear flaps under ', 'olive-drab field jackets and ')} marching north along a dirt road between golden rice fields and low hills in Korea, NO text"],
  sound="waves, boat engines, distant marching boots",
  refs=[], must=["1950 equipment only", "no snow in these two images"]),
 dict(title="The road north", mode="stills", ambience_from="Who I am", pov=False, mood="intrigue",
  v="Our road climbed north into the mountains, toward a frozen lake the maps called the Chosin Reservoir. One narrow dirt track, cut into the cliffs, with a drop on one side and rock on the other. Every truck, every tank, every man went up that one road.",
  img=f"A long column of olive-drab trucks and Marines on foot climbing {ROAD}",
  stills=[f"Wide painterly view of a long column of olive-drab US Army trucks, jeeps and {MAR} on foot climbing {ROAD}, late November 1950, grey sky",
          "A narrow frozen dirt road cut into a steep cliff face in the snowy North Korean mountains, a sheer drop on one side and rock on the other, an olive-drab truck edging along it, 1950, NO close-up faces"],
  sound="truck engines straining, wind, gravel crunching",
  refs=["road"], must=["1950 military vehicles only: jeeps and deuce-and-a-half trucks"]),
 dict(title="The Siberian wind", mode="stills", ambience_from="Thirty-five below", pov=True, mood="tense",
  v="Then the wind came down from Siberia. The temperature dropped below zero and kept on falling. Some nights it hit thirty-five below. That's minus thirty-seven Celsius. Your breath froze on your scarf. Your eyelashes stuck together when you blinked.",
  img=f"Night on a snowy ridge, a fierce wind blowing snow sideways across a line of foxholes",
  stills=[f"Night on a high snowy ridge above the Chosin Reservoir, late November 1950: a fierce wind drives snow sideways across a line of small foxholes, {MAR} hunched low with their backs to the wind, moonlight on the frozen lake far below",
          f"Extreme close-up of a young Marine's face in the cold, 1950: thick white frost on his eyelashes and eyebrows, ice on the wool scarf over his mouth, the fur-lined ear flaps of his pile cap white with frost"],
  sound="howling wind, snow hissing",
  refs=["ridge"], must=["no faces of real people", "night"]),
 dict(title="Feet that sweat", mode="stills", ambience_from="Thirty-five below", pov=True, mood="intrigue",
  v="They gave us shoepacs: boots with rubber bottoms and leather tops. Great for mud. But when you marched, your feet sweated inside the rubber. And when you stopped... that sweat turned to ice. That's how most of us got frostbite. Not from the snow. From our own feet.",
  img="Close-up of rubber-bottomed shoepac boots in the snow",
  stills=["Close painterly view of a Marine's rubber-bottomed shoepac boots with laced leather uppers standing in deep snow, 1950, frost on the laces, the hem of a long olive parka above",
          "First-person view at night: a young Marine's chapped hands unlace a frozen shoepac boot beside a snow-covered foxhole, a thick wool sock steaming faintly in the cold, 1950"],
  sound="boots crunching in snow, wind",
  refs=[], must=["rubber-bottomed boots with leather uppers"]),
 dict(title="Rule one: the socks", mode="stills", ambience_from="Who I am", pov=True, mood="warm",
  v="So rule one: keep a dry pair of socks inside your shirt, against your chest. Every night, no matter what, you change them. The wet pair goes against your chest to dry, the dry pair goes on your feet. The guys who skipped it... lost toes.",
  img="A Marine tucking a pair of wool socks inside his shirt",
  stills=[f"First-person view: a young Marine's hands tuck a folded pair of grey wool socks inside his open parka and shirt, against his chest, snow falling, 1950",
          f"Inside a shallow snowy foxhole at dusk, 1950: {RA} pulls a dry wool sock onto his bare foot, his shoepac boot beside him, his face tight with cold, his BAR leaning on the snow wall"],
  sound="wind, rustling fabric",
  refs=["ray"], must=["exactly one person or only hands"]),
 dict(title="Never zip the bag", mode="stills", ambience_from="Thirty-five below", pov=True, mood="tense",
  v="We had good sleeping bags, thick and warm. And that was the danger. Rule two: you never zipped yourself all the way in. If trouble came in the night, you had to be out of that bag and on your rifle in a second. So we slept half-in, boots on, rifle in our arms.",
  img="A Marine sleeping half-out of a sleeping bag in a snowy foxhole with his rifle",
  stills=[f"Night in a snowy foxhole, 1950: {RA} sleeps sitting half inside an open olive-drab mountain sleeping bag, boots on, his BAR held across his chest, frost on his eyebrows, moonlight on the snow",
          "Close painterly view of an open olive-drab mountain sleeping bag in a snowy foxhole at night, its zipper left wide open, an M1 rifle lying on top of it, frost glittering, NO people"],
  sound="wind, a man breathing slowly",
  refs=["ray"], must=["the sleeping bag is open, not zipped"]),
 dict(title="Frozen dinner", mode="stills", ambience_from="Home by Christmas", pov=True, mood="intrigue",
  v="Our C-rations froze solid in the can. Beans, hash, fruit cocktail... all ice. If there was a fire, we heated them. If there wasn't, we stuck the cans under our armpits and waited. Half-frozen beans for breakfast. You ate it anyway. Empty stomachs freeze faster.",
  img="A Marine holding a frozen ration can",
  stills=["Close painterly view of a small open olive-drab C-ration can in a Marine's gloved hand, its beans frozen solid with ice crystals on top, a spoon stuck upright in them, snowy background, 1950, no readable text on the can",
          f"Two Marines in parkas crouch around a tiny fire in the snow, warming olive-drab ration cans on the embers, steam rising, dark snowy hills behind, 1950, faces half hidden by hoods"],
  sound="crackling small fire, wind, a spoon scraping a tin can",
  refs=[], must=["no readable text or labels on the cans"]),
 dict(title="Guns that freeze", mode="clip", pov=True, mood="tense",
  v="And the cold went after our weapons. Gun oil turned thick as glue. Carbines jammed. Ray's BAR fired slow, when it fired at all. So we wiped our rifles almost dry, and we worked the bolts every hour, all night long, so the metal never had a chance to freeze.",
  img=f"Night in a snowy foxhole, December 1950: first-person view, a Marine's gloved hands work the bolt of an M1 rifle, frost on the metal, {RA} beside him wiping his BAR with a rag",
  shots=["gloved hands pull back the frosted bolt of an M1 rifle and let it slam forward",
         "Ray rubs his Browning Automatic Rifle with a rag, frost on the barrel",
         "close-up of white frost creeping across a rifle's metal receiver"],
  sound="metal clicking, wind, a rag rubbing metal",
  refs=["ray", "ridge"], must=["M1 Garand rifle and Browning Automatic Rifle only, 1950 weapons"]),
 # ───────── SALDIRI ─────────
 dict(title="Ground like iron", mode="stills", ambience_from="Guns that freeze", pov=True, mood="intrigue",
  v="We tried to dig foxholes. The ground was frozen a foot deep, hard as iron. Our little shovels just bounced off it. So we chipped out what we could, and built up walls of rocks and packed snow around us. It wasn't much. But it was all we had between us and the wind.",
  img="Marines trying to dig into frozen rocky ground on a snowy ridge",
  stills=[f"A snowy ridge at dusk, November 1950: {MAR} swing small entrenching shovels at frozen rocky ground, chips of ice flying, breath steaming, faces strained",
          "First-person view: gloved hands stack rocks and blocks of packed snow into a low wall around a shallow foxhole on a snowy ridge at dusk, 1950"],
  sound="shovels clanging on frozen ground, wind",
  refs=["ridge"], must=["small folding entrenching shovels"]),
 dict(title="The bugles", mode="clip", pov=True, beat="ÇATIŞMA (ışık+ses, kan yok)", mood="tense",
  v="On the night of November twenty-seventh, we heard bugles. Then whistles. Then the whole hillside came alive. The Chinese army had been hiding in those mountains for weeks, moving only at night. Now they hit us from every direction at once.",
  img="Night on a snowy ridge: white flares hanging in the sky, the snow lit up, dark figures far away on the slope",
  shots=["white parachute flares burst over a dark snowy hillside, lighting the falling snow",
         "first-person view over the rim of a foxhole: tiny dark figures appear along a distant snowy ridge line in the flare light",
         "orange muzzle flashes flicker along a line of foxholes in the snow at night"],
  sound="bugle calls echoing, shrill whistles, distant gunfire, wind",
  refs=["ridge"], must=["no blood, no wounds, no bodies", "figures distant and small"]),
 dict(title="Surrounded", mode="stills", ambience_from="The bugles", pov=False, mood="tense",
  v="By morning, we understood. It wasn't a few Chinese soldiers. It was whole armies. More than a hundred thousand men, all around our road. And about thirty thousand of us, Marines, Army soldiers and a few British commandos... surrounded, at the top of a frozen mountain.",
  img="A painted map-like view of the snowy mountains around the frozen reservoir",
  stills=["A wide painterly bird's-eye view at dawn of snowy North Korean mountains around a long frozen reservoir, 1950, a thin dark road winding along the valley, tiny clusters of tents and trucks at a few points along it, smoke rising, dark ridges all around, NO text, NO map labels",
          f"Dawn on a snowy ridge, 1950: {MAR} stand in a shallow trench line looking out at the endless white mountains around them, breath steaming, grim faces half-hidden by hoods"],
  sound="wind, distant artillery rumble",
  refs=[], must=["no text, no map labels, no arrows"]),
 dict(title="As cold as we were", mode="stills", ambience_from="The bugles", pov=False, mood="sad",
  v="Later, I saw the men we'd been fighting. Most wore padded cotton uniforms... and thin canvas shoes, in thirty-five below. Thousands of them froze in those hills. Whatever else they were, they were just as cold as we were. Colder.",
  img=f"{CPV} huddled together in the snow at dawn",
  stills=[f"Dawn in the snowy North Korean mountains, 1950: a small group of {CPV} huddle together behind a rock in the snow, faces gaunt and frost-bitten, breath steaming, seen from a distance with respect, NO weapons pointed, NO blood",
          "Close painterly view of a pair of thin worn canvas shoes in deep snow, frost on the cloth, 1950"],
  sound="wind, silence",
  refs=[], must=["respectful, non-violent depiction"], must_not=["caricature", "blood, wounds, bodies"]),
 dict(title="Fox Hill", mode="stills", ambience_from="Thirty-five below", pov=False, mood="intrigue",
  v="Up at Toktong Pass, one company, Fox Company, about two hundred and forty Marines, held a single hill for five days and five nights. If they had lost it, the road would have been cut, and none of us would have come home. They didn't lose it.",
  img="A lone snowy hill above a mountain pass at night, a few foxholes on top",
  stills=["A lone steep snowy hill above a narrow mountain pass road in North Korea, December 1950, at dusk: a ring of small foxholes along its top, tiny figures of Marines in parkas, flare light in the sky",
          "First light over a snowy hilltop, 1950: a few exhausted Marines in parkas sit in their foxholes looking at the sunrise over the mountains, breath steaming, faces hidden by hoods"],
  sound="wind across a ridge, distant flares popping",
  refs=[], must=["no blood, no bodies"]),
 dict(title="Morphine in our mouths", mode="stills", ambience_from="Guns that freeze", pov=False, beat="ORTA SORU (~%45)", mood="sad",
  v="Our Navy corpsmen had it worst. The morphine froze in the little tubes, so they carried them in their mouths to keep them thawed. The blood plasma froze in the bottles. So tell me in the comments: if you could keep only one thing warm against your body... what would it be?",
  img="A Navy corpsman in the snow with a medical bag",
  stills=["A US Navy corpsman of 1950 in a hooded parka kneels in the snow beside a wounded Marine lying covered with a blanket, his hand on the man's shoulder, a canvas medical bag open beside him, night, NO blood visible",
          "Close painterly view of a canvas medical bag in the snow, 1950, a small glass bottle of plasma with ice crystals inside it, frost on the canvas, NO text"],
  sound="wind, a low voice murmuring",
  refs=[], must=["no blood, no wounds visible", "no text on bottles"]),
 # ───────── ÇIKIŞ ─────────
 dict(title="Another direction", mode="clip", pov=False, mood="warm",
  v="On the first of December, we started out. Our general put it in a way we never forgot: we weren't retreating. We were attacking in another direction. We loaded our wounded onto the trucks, and anybody who could still walk... walked.",
  img=f"A column of Marines and trucks setting out down the snowy mountain road at dawn",
  shots=[f"a long column of {MAR} walks beside olive-drab trucks down the snowy mountain road, wounded men wrapped in blankets riding on the trucks",
         "Danny walks in the column, rifle on his shoulder, and glances back at the hills",
         "the column winds away between snowy ridges under a grey sky"],
  sound="boots crunching in snow, truck engines idling, wind",
  refs=["danny", "road"], must=["no real people's faces", "1950 trucks only"]),
 dict(title="Walking at night", mode="stills", ambience_from="Another direction", pov=True, mood="tense",
  v="We fought for every mile. In daylight, our planes, the Corsairs, came in low over the ridges and kept the hills clear. At night, we kept moving. If you sat down in the snow to rest, you might not get up. So you didn't sit down.",
  img="A dark-blue gull-winged Corsair fighter plane flying low over the snowy column",
  stills=[f"Daylight over the snowy mountains, December 1950: a dark-blue gull-winged F4U Corsair fighter plane flies low along a ridge above a long column of {MAR} and trucks on the road, NO text or markings legible",
          f"Night on the frozen mountain road, 1950: first-person view of the back of a Marine walking ahead in the dark column, snow falling, moonlight on the snow, a truck's dim blackout lights behind"],
  sound="aircraft engine roaring past, then wind and boots",
  refs=["road"], must=["F4U Corsair with inverted gull wings"]),
 dict(title="Across the ice", mode="stills", ambience_from="Another direction", pov=False, mood="sad",
  v="On the other side of the reservoir, an Army task force had been cut off and torn apart. In the first days of December, their survivors came stumbling across the frozen lake toward Hagaru, a few at a time. Our men went out onto the ice with jeeps and sleds to bring them in. Hundreds of them made it.",
  img="Soldiers walking across a vast frozen reservoir toward a camp",
  stills=["A vast frozen reservoir in the North Korean mountains, early December 1950, grey light: small groups of exhausted American soldiers in parkas walk and help each other across the snowy ice toward a distant camp, NO blood",
          "A jeep with a wooden sled behind it drives out across the frozen reservoir ice to pick up tired soldiers, two Marines in parkas helping a man onto the sled, 1950, NO blood"],
  sound="wind across ice, a jeep engine, crunching snow",
  refs=[], must=["frozen lake surface", "no blood, no bodies"]),
 dict(title="The warming tent", mode="stills", ambience_from="Another direction", pov=True, mood="warm",
  v="At Hagaru, there were warming tents with little oil stoves inside. You got a few minutes, then the next man's turn. And here's a hard lesson: if your feet were frozen, the warmth made them swell up. Men took their boots off by the stove, and then couldn't get them back on.",
  img="Marines crowded inside a canvas tent around a small oil stove",
  stills=[f"Inside a crowded olive-drab canvas tent at Hagaru, December 1950: {MAR} without helmets sit shoulder to shoulder around a small round oil stove glowing orange, steam rising from wet gloves and socks hung above it, tired faces",
          "Close painterly view inside a warm tent: a pair of rubber-bottomed shoepac boots drying beside a small glowing oil stove, wool socks steaming on a line above, 1950"],
  sound="a stove ticking, men murmuring, wind outside canvas",
  refs=[], must=["1950 tent stove, no modern heaters"]),
 dict(title="The airstrip", mode="stills", ambience_from="Another direction", pov=False, mood="warm",
  v="Right there, our engineers had scraped an airstrip out of the frozen ground. Twin-engine transport planes landed on it, under fire, and carried out our wounded and frostbitten. Thousands of men flew out of that frozen field. The rest of us kept walking.",
  img="A small frozen airstrip in a mountain valley with a twin-engine transport plane",
  stills=["A rough frozen dirt airstrip in a snowy North Korean mountain valley, December 1950: an olive-drab twin-engine C-47 transport plane waits with its door open, wounded Marines on stretchers being carried toward it, tents and trucks nearby, NO legible markings",
          "A twin-engine C-47 transport plane lifting off from a short snowy airstrip between dark mountains, December 1950, snow blowing behind it"],
  sound="propeller engines roaring, wind",
  refs=[], must=["C-47 Skytrain twin-engine propeller plane"]),
 dict(title="Tootsie Rolls", mode="clip", pov=True, mood="warm",
  v="And then, the strangest thing. Parachutes came down full of Tootsie Rolls. Crates of them. Nobody's ever been sure exactly why. But frozen candy was food you could thaw in your mouth. And when it was soft, it plugged holes in fuel drums. For some of us, it was the only thing we ate for days.",
  img="Supply parachutes drifting down over a snowy Marine camp",
  shots=["colourful supply parachutes drift down over a snowy Marine camp in the mountains",
         "a Marine pries open a wooden crate in the snow and finds it packed with small wrapped candies",
         "first-person view: a gloved hand holds a small frozen chewy brown candy, the wrapper half open"],
  sound="wind, parachutes flapping, wood creaking open, a man laughing",
  refs=["camp"], must=["plain unbranded wrappers, no logos or readable text"]),
 dict(title="The blown bridge", mode="stills", ambience_from="A bridge from the sky", pov=False, mood="tense",
  v="Below Koto-ri, the road crossed a deep gorge in the Funchilin Pass. And the bridge was gone, blown up. On one side, a cliff. On the other, a long drop. Thousands of men, and every truck and tank we had... and no way across.",
  img="A blown-up concrete bridge over a deep snowy gorge on a mountain road",
  stills=["A narrow mountain road in the snowy Funchilin Pass, North Korea, December 1950, ending at a blown-up concrete bridge: a gap of empty air over a deep gorge, broken concrete hanging, sheer cliffs, snow falling, NO people",
          f"{MAR} and trucks stopped in a line on the snowy mountain road, looking at the broken bridge ahead, 1950, faces hidden by hoods"],
  sound="wind in a gorge, rushing water far below",
  refs=[], must=["no people on the bridge itself"]),
 dict(title="A bridge from the sky", mode="clip", pov=False, mood="intrigue",
  v="So the Air Force dropped us a bridge. Big twin-tailed cargo planes came over and dropped steel bridge sections by parachute, each one weighing about a ton. Our engineers bolted them together across the gap. I'd never seen anything like it. Nobody had.",
  img="Twin-boom cargo planes dropping large steel sections under parachutes over snowy mountains",
  shots=["a twin-boom C-119 cargo plane flies low over snowy mountains and drops a large steel bridge section hanging from big parachutes",
         "several large parachutes with heavy steel sections drift down toward a snowy valley",
         "Marine engineers in parkas swing a steel bridge section into place over a gorge, snow falling"],
  sound="heavy propeller engines, parachutes snapping open, metal clanging",
  refs=["road"], must=["C-119 Flying Boxcar with twin tail booms", "1950 equipment only"]),
 dict(title="The star", mode="clip", pov=False, mood="warm",
  v="At Koto-ri, it snowed and snowed. Our planes couldn't fly in it. Then one night, the clouds opened... and there was a single star, bright over the mountains. A lot of us took it as a sign. Today, that star is the badge of the men who came out of Chosin.",
  img=f"Night at a snowy camp, a single bright star appearing through a break in the clouds, {DA} looking up",
  shots=["snow stops falling over a dark camp of tents in the mountains, the clouds slowly part",
         "a single bright star shines through the gap in the clouds above a black ridge",
         "Danny looks up at the star, his face lit faintly, breath steaming, he smiles a little"],
  sound="wind dying down, silence, a soft murmur of men",
  refs=["danny", "camp"], must=["only one bright star"]),
 dict(title="Down the mountain", mode="stills", ambience_from="A bridge from the sky", pov=True, mood="tense",
  v="We crossed that bridge in the dark, one truck at a time, with the men walking beside them in single file. Down and down the mountain, through the last ambushes, toward the sea.",
  img="A narrow steel bridge over a gorge at night, trucks crossing slowly",
  stills=[f"Night in the Funchilin Pass, December 1950: an olive-drab truck crawls slowly across a narrow steel treadway bridge over a deep dark gorge, {MAR} walking in single file beside it, snow on the cliffs, dim light",
          f"Early dawn: a long line of {MAR} and trucks winding down a snowy mountain road toward a distant grey coastal plain and the sea, 1950"],
  sound="engines in low gear, boots, wind",
  refs=["road"], must=["steel treadway bridge"]),
 dict(title="The road behind us", mode="stills", ambience_from="A bridge from the sky", pov=False, mood="sad",
  v="Behind our column came thousands of Korean families. Old men, mothers with babies on their backs, children carrying bundles bigger than they were. They walked the same frozen road, through the same cold, to get away from the war. Some of us gave them whatever food we had left.",
  img="Korean civilian refugees walking behind a military column on a snowy road",
  stills=["A snowy mountain road in North Korea, December 1950: a long line of Korean civilian refugees in white and grey padded winter clothes walk behind a military truck column, a mother with a baby tied on her back, children carrying bundles, respectful painterly depiction, NO text",
          "A young Marine in a parka hands a small ration can to an elderly Korean man in a padded coat and black horsehair hat on a snowy roadside, 1950, warm respectful moment"],
  sound="wind, many footsteps in snow, a baby crying softly",
  refs=[], must=["respectful depiction of Korean civilians"]),
 dict(title="The sea", mode="stills", ambience_from="How I survived", pov=True, mood="warm",
  v="On December eleventh, we came down into the port of Hungnam. Hot chow. Tents. Ships in the harbour. I remember standing in line for coffee, holding the cup with both hands, and I couldn't stop shaking. Not from the cold, this time.",
  img="A coastal port in December with ships in the harbour and tents on the shore",
  stills=["The North Korean port of Hungnam in December 1950: grey navy transport ships anchored in the harbour, rows of tents and supply crates on the snowy shore, smoke from field kitchens, NO legible text",
          "First-person view: a young Marine's chapped, shaking hands wrap around a steaming tin cup of coffee, a field kitchen and other Marines blurred behind, 1950"],
  sound="seagulls, ship horns far away, men talking",
  refs=[], must=["1950 ships and equipment"]),
 dict(title="Dear Mom", mode="stills", ambience_from="How I survived", pov=True, mood="warm",
  v="That night, I wrote my first letter home in three weeks. I didn't tell my mother about the bugles, or the bridge, or the cold. I wrote: Dear Mom, I'm okay. Ate a hot meal today. Please send socks. Lots of socks. She sent me twelve pairs, and I gave most of them away.",
  img="A Marine writing a letter by lamplight in a tent",
  stills=[f"Night inside a canvas tent at Hungnam, December 1950: {DA.replace('under a plain M1 steel helmet', 'helmet off')} sits on a cot writing a letter with a pencil on a notepad on his knee, a small lamp glowing, other Marines asleep behind, NO readable writing",
          "Close painterly view of a small cardboard parcel opened on a cot, full of rolled grey and brown wool socks, a folded letter on top, warm lamplight, 1950, NO readable text"],
  sound="pencil scratching on paper, a lamp hissing, wind on canvas",
  refs=["danny"], must=["no readable writing on the paper"]),
 dict(title="The cold took more", mode="stills", ambience_from="How I survived", pov=False, mood="sad",
  v="When they counted us up, there was a number nobody expected. More of us were carried off that mountain by the cold than by bullets. Frostbite took fingers, toes, sometimes whole feet. For the rest of their lives, a lot of the men I served with couldn't stand being cold, not even for a minute.",
  img="A field hospital tent with Marines having their frostbitten feet treated",
  stills=["Inside a field hospital tent at Hungnam, December 1950: a Navy doctor and corpsman examine the bandaged feet of a seated Marine, rows of cots behind, warm lamplight, NO blood, NO graphic injuries",
          "Close painterly view of a Marine's hands wrapped in white bandages, resting on a grey wool blanket, 1950, soft light"],
  sound="quiet voices, a stove, wind outside",
  refs=[], must=["no graphic injuries, no blood"]),
 dict(title="Fourteen thousand", mode="stills", ambience_from="How I survived", pov=False, mood="warm",
  v="We weren't the only ones leaving. Almost a hundred thousand Korean civilians came down to that harbour, hoping for a place on a ship. One cargo ship, built for a small crew, took fourteen thousand of them on board. It sailed just before Christmas. Not one of them was lost.",
  img="Thousands of Korean refugees in winter clothes on a snowy shore boarding a cargo ship",
  stills=["The snowy shore of Hungnam harbour, December 1950: thousands of Korean civilian refugees in padded winter clothes, carrying bundles, waiting to board a large grey cargo ship, mothers holding children, NO modern objects, NO text",
          "A large grey cargo ship crowded with Korean refugees on every deck sailing out of a winter harbour at dusk, 1950, a low sun on the sea"],
  sound="sea, a ship's horn, many quiet voices",
  refs=[], must=["respectful depiction of Korean refugees"]),
 # ───────── KAPANIŞ ─────────
 dict(title="How I survived", mode="clip", pov=False, mood="warm",
  v="So how did I survive Chosin? Dry socks against my chest. A rifle I never let freeze. Frozen beans, eaten anyway. Never sitting down in the snow. And a buddy named Ray, who never let me fall asleep in a foxhole.",
  img=f"{DA} and {RA} sitting side by side on the deck of a ship at sea, wrapped in blankets, December 1950",
  shots=["Danny and Ray sit side by side on a ship's deck wrapped in blankets, the grey sea behind",
         "Ray nudges Danny with his elbow and they both laugh tiredly",
         "the ship sails away from the snowy mountains of the coast"],
  sound="sea wind, waves against a hull, two men laughing softly",
  refs=["danny", "ray"], must=["exactly two people in front"]),
 dict(title="The Chosin Few", mode="stills", ambience_from="How I survived", pov=False, mood="warm",
  v="The ships took us south. We spent Christmas of nineteen-fifty in a tent camp the Marines called the Bean Patch. Years later, those of us who walked out of those mountains started calling ourselves the Chosin Few.",
  img="A transport ship at sea at dusk, then a tent camp at Christmas",
  stills=["A grey transport ship at sea at dusk, December 1950, the snowy mountains of North Korea fading on the horizon behind it, calm water, a pale star in the sky",
          f"A muddy tent camp in a valley in South Korea, Christmas 1950, light frost, olive-drab squad tents, {MAR} without helmets gathered around a small pine tree decorated with scraps of red cloth and ration-tin lids, warm lamp light from a tent, tired smiles"],
  sound="waves, a low ship engine hum, a harmonica softly",
  refs=[], must=["1950 tent camp, no snow-covered mountains close by"]),
 dict(title="Still here", mode="stills", ambience_from="How I survived", pov=False, mood="warm",
  v="For years, we didn't talk about it much. Then the reunions started. Old men in caps, swapping stories and a little bit of candy, because the Tootsie Roll company kept sending boxes to every reunion. Ray and I went to every one we could. My name is Danny Moore, and I was one of the Chosin Few.",
  img="Elderly veterans at a reunion table with small candies",
  stills=["A warm community hall in America, about 1985: a few elderly men in plain caps and windbreakers laugh together around a table with coffee cups and a bowl of small wrapped chewy candies, a framed photograph of snowy mountains on the wall, NO text, NO logos, NO real people",
          f"Two elderly American veterans about 1985, one thin with blue-grey eyes and one broad with thick grey eyebrows, sit side by side on a porch bench in winter, coffee cups in hand, smiling quietly at the snow"],
  sound="soft laughter, cups clinking, a clock ticking",
  refs=[], must=["no readable text, no logos", "no real people"]),
 dict(title="If you stayed", mode="stills", ambience_from="How I survived", pov=False, beat="KAPANIŞ CTA (kill yok)", mood="warm",
  v="If you've stayed with me all the way down that mountain, thank you. Every week, I bring you one more winter that pushed ordinary people to their limit, told by the people who lived through it. If you want the next one, subscribe. And tell me: what would you have kept warm?",
  img="A snowy mountain road at sunrise, empty and quiet",
  stills=["The empty snowy mountain road in North Korea at sunrise, quiet and peaceful, the frozen reservoir glowing below, NO people, NO vehicles"],
  sound="soft wind, silence",
  refs=[], must=["no people"]),
 dict(title="What comes next", mode="stills", ambience_from="Thirty-five below", pov=False, beat="SONRAKİ BÖLÜM", mood="intrigue", own_rules=True,
  v="Far to the north-west, on the open steppe of Mongolia, winter falls to fifty below. There are no walls, no forests, no cellars. Only felt tents, herds of horses... and a family that must keep every animal alive until spring. How do they do it? That story is next. And here... the fire is still burning.",
  img="A lone white felt ger on the snowy Mongolian steppe at dawn",
  stills=["A single round white felt ger alone on the endless snowy Mongolian steppe at dawn, about 1900, smoke rising from its roof ring, a herd of shaggy horses nearby, icy pale blue sky, NO people close up, NO modern objects"],
  sound="howling steppe wind",
  refs=[], must=["traditional Mongolian felt ger with no stove pipe"], must_not=["modern objects", "soldiers", "Korea"]),
]

SHEET = ("Character reference sheet: on the left a full-body front view standing, "
         "on the right a chest-up portrait of the same person; identical original character in both views, single "
         "character only, no other people. ")
refs = {
 "danny": {"kind": "character", "prompt": SHEET + DA},
 "ray": {"kind": "character", "prompt": SHEET + RA},
 "ridge": {"kind": "location", "prompt": "Location reference, single image, NO people: a high snowy ridge above the frozen Chosin Reservoir in North Korea, late November 1950, a line of small foxholes dug into the snow along the ridge, dark pine trees, steep white mountains all around, cold blue night light"},
 "road": {"kind": "location", "prompt": "Location reference, single image, NO people: " + ROAD + ", December 1950, olive-drab trucks parked along it, grey winter sky"},
 "camp": {"kind": "location", "prompt": "Location reference, single image, NO people: a US Marine camp in a snowy valley in the North Korean mountains, 1950: olive-drab canvas squad tents, wooden ammunition crates, a jeep, smoke from a field kitchen, snowy hills all around"},
}
for k, r in refs.items():
    r["n"] = k

ep = {
 "id": "ep007", "version": 1,
 "title": "The Frozen Chosin: How Marines Survived −35°F in Korea (1950)",
 "title_alt": "You're a Marine at the Chosin Reservoir. It's 35 Below.",
 "title_c": "Surrounded at −35°F: The Marines' Breakout from Chosin",
 "thumbnail": "Close-up of the young Marine's face, thick white frost on his eyebrows and pile-cap ear flaps, M1 helmet, a white flare in the night snow behind; one big phrase 'FROZEN CHOSIN' (B: '−35°F', C: no text)",
 "hook_description": "Korea, November 1950. Fifteen thousand US Marines are surrounded by more than a hundred thousand Chinese soldiers at the top of a frozen mountain, at thirty-five below. Danny, a 19-year-old private, tells how they survived the cold and fought their way down one narrow road to the sea.",
 "character": "Danny Moore, a fictional 19-year-old private in the 7th Marines, 1st Marine Division; his buddy Ray (BAR man)",
 "setting": "The Chosin Reservoir campaign, North Korea, from Thanksgiving to Christmas 1950: the mountain road from Yudam-ni and Hagaru-ri through Koto-ri and the Funchilin Pass down to the port of Hungnam",
 "style": ('Hand-painted gouache and watercolor storybook illustration, visible brush texture, warm amber firelight and flare light against cold blue winter light, cinematic composition, historically accurate Korean War 1950 US Marine winter gear (long olive-drab hooded parkas, pile caps with fur-lined ear flaps under plain M1 steel helmets, rubber-bottomed shoepac boots, M1 rifles); show ONLY what the scene description asks for, do not add extra vehicles, aircraft, tanks or ships; any vehicle shown is a 1950 model; no modern objects, soft painterly detail, no text, no letters, no watermark'),
 "ref_style": ("Hand-painted gouache and watercolor storybook character reference sheet, same painterly look as the episode, "
               "even neutral lighting, plain warm parchment background, historically accurate 1950 US Marine winter field uniform, "
               "original fictional person, no text, no labels, no badges with writing, no watermark"),
 "pov_hint": "First-person point of view: we see through the narrator's own eyes, his olive wool gloves and parka sleeves may be visible in the foreground",
 "motion_suffix": ("Gentle natural motion, soft cuts between shots, painterly style and characters stay consistent across shots, "
                   "no text; historically accurate Korean War 1950: olive-drab parkas, M1 helmets, M1 rifles, 1950 trucks and "
                   "aircraft only, no modern vehicles, no modern weapons, no helicopters, no electric streetlights"),
 "cast": {"Danny": DA, "Ray": RA},
 "preview_scenes": [1, 2, 3],
 "gates": {},
 "hybrid": {"still_resolution": "2k", "still_quality": "medium", "clip_start_resolution": "1k",
            "note": "mode=clip → Seedance; mode=stills → 2K görseller + Ken Burns, ortam sesi ambience_from klibinden"},
 "must": ["historically accurate Korean War 1950 only (except the final teaser scene)",
          "the same faces and uniforms as in the reference images for every named character",
          "painterly gouache look in every frame"],
 "must_not": ["any text, letters, numbers, captions, logos, unit patches, name tapes or watermark",
              "modern objects: modern cars, SUVs, pickup trucks, helicopters, drones, plastic, digital watches, phones, electric streetlights, power lines",
              "modern military gear: camouflage patterns, body armor, plate carriers, modern helmets with covers or straps, modern rifles with optics, US flag patches",
              "World War I or Vietnam-era uniforms, tropical uniforms, green jungle",
              "gore, blood, wounds, corpses, skeletons",
              "extra fingers, deformed hands, duplicated faces",
              "the same person appearing twice in one frame (clones, twins, duplicated characters)",
              "collage, multiple panels, split screen, several pictures in one image: it must be ONE single continuous scene"],
 "sources": [
  "Lynn Montross & Nicholas A. Canzona — U.S. Marine Operations in Korea 1950–1953, Vol. III: The Chosin Reservoir Campaign (USMC Historical Branch, 1957)",
  "Brig. Gen. Edwin H. Simmons — Frozen Chosin: U.S. Marines at the Changjin Reservoir (Marine Corps Historical Center, 2002)",
  "Eric Hammel — Chosin: Heroic Ordeal of the Korean War (Vanguard, 1981)",
  "Martin Russ — Breakout: The Chosin Reservoir Campaign, Korea 1950 (Fromm, 1999)",
  "Bob Drury & Tom Clavin — The Last Stand of Fox Company (Atlantic Monthly Press, 2009)",
  "Hampton Sides — On Desperate Ground: The Marines at the Reservoir (Doubleday, 2018)",
 ],
 "disclosure": ("Danny Moore and Ray are fictional characters, built from the memoirs of Chosin veterans and from official "
                "histories; the battle, places and events are real. No real person is portrayed. Illustrations and animation "
                "were created with AI tools; narration uses a synthetic voice."),
 "refs": refs,
 "music": [],
 "next_episode_tease": "Mongolian nomads on the steppe at fifty below (ep006 script)",
 "voice_engine": None,
 "scenes": [],
}
for s in scenes:
    if "danny" in s["refs"]: s["pov"] = False
for i, s in enumerate(scenes, 1):
    sc = {"n": i, "title": s["title"], "mode": s["mode"], "pov": s["pov"], "narration": plain(s["v"]),
          "narration_voiced": s["v"], "image_prompt": s["img"], "sound": s["sound"], "refs": s["refs"],
          "voice_mood": s["mood"]}
    if s["mode"] == "clip":
        sc["shots"] = s["shots"]
    else:
        sc["still_prompts"] = s["stills"]
        sc["ambience_from"] = next(i for i, x in enumerate(scenes, 1) if x["title"] == s["ambience_from"])
    for k in ("beat", "must", "must_not", "own_rules"):
        if s.get(k):
            sc[k] = s[k]
    ep["scenes"].append(sc)
ep005 = S.load_episode("ep005")
ep["voice_engine"] = ep005["voice_engine"]
clips = [s for s in ep["scenes"] if s["mode"] == "clip"]
stills = sum(len(s["still_prompts"]) for s in ep["scenes"] if s["mode"] == "stills")
cost = len(clips) * (15 + 2.75) + stills * 2.75 + len(refs) * 2.75  # GPT Image 2.5 high 2K + Seedance 720p
ep["max_credits"] = 360  # kullanıcı onayı 20 Eki
if __name__ == "__main__" and "--force" in sys.argv:
    S.save_episode(ep)  # DİKKAT: kapıları ve üretilen varlıkları sıfırlar

w = [len(s["narration"].split()) for s in ep["scenes"]]
print(len(w), "sahne", sum(w), "kelime", min(w), max(w), "≈", round(sum(w)/2.81/1.06/60 + len(w)*0.6/60, 1), "dk")
print("klip:", [s["n"] for s in clips], "| still görsel:", stills, "| tahmini maliyet:", cost, "kredi")
