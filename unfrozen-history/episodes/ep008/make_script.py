import json, re, sys
sys.path.insert(0, "/home/user/loftik-video-bot/unfrozen-history")
from uh import state as S

# Kurgusal karakterler (Eli Parker ve kulübe arkadaşları). Valley Forge kampı (19 Ara 1777 – 19 Haz 1778) ve olaylar gerçek:
# kulübe ölçüleri ve 12 dolar ödül (Genel Emir 18 Ara 1777), 18 Ara Şükran günü pirinç+sirke ve çiğ deri mokasen
# (Joseph Plumb Martin anıları), "No meat!" ve fire cake (cerrah Albigence Waldo günlüğü, 21 Ara 1777),
# 2.898 yalınayak asker (Washington'ın Laurens'e mektubu, 23 Ara 1777), Şubat açlığı, von Steuben talimi (Mart 1778),
# Fransız ittifakı kutlaması (6 Mayıs 1778), kamptan çıkış (19 Haz 1778). Ölümlerin çoğu soğuktan değil hastalıktan (~2.000).
# Gerçek kişiler (Washington, von Steuben) yüzü görünmeden: arkadan / uzaktan.
# Mongolia dersleri: ilk sahne ≤12 sn, olayın ortasından açılış, ağır çekim yok; ~%45'te yorum sorusu; CTA'da "kill" yok.
EL = "Eli Parker (Connecticut farm boy of 17 in the Continental Army, thin face, hollow cheeks, straight light-brown hair tied back, a few freckles, blue eyes, ragged brown wool coat with patched elbows over a dirty linen shirt, worn black cocked hat, an old grey wool blanket over his shoulders, threadbare grey breeches)"
JO = "Jonah Hale (his best friend, 19, big-shouldered, broad red-bearded face, curly red hair, faded blue wool coat with torn red facings, black round felt hat with the brim turned up on one side)"
SM = "Sam Freeman (a free Black soldier of about 30 from New London, Connecticut, calm lean face, short black hair, small trimmed beard, long brown linen hunting shirt with fringed cape over a wool waistcoat, black cocked hat)"

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

HUT_IN = "inside a small soldiers' log hut at Valley Forge, winter 1777-78: rough log walls chinked with clay, a dirt floor, a wooden-and-clay fireplace at the far end with a small fire, three tiers of bunks made of poles and straw along both side walls, muskets leaning on the wall, wet wool blankets and a kettle, smoky dim air"
CAMP = "Valley Forge, Pennsylvania, winter 1777-78: long straight rows of small log huts with clay-chinked walls and wooden chimneys smoking, on a rolling snowy hillside, tree stumps everywhere where the forest was cut, bare winter woods beyond, a grey sky"

scenes = [
 # ───────── İLK ~60 SN: TAMAMI KLİP ─────────
 dict(title="No shoes", mode="clip", pov=True, beat="SOĞUK AÇILIŞ (0:00) — kanca ilk 5 sn, ≤12 sn", mood="tense",
  v="December, seventeen seventy-seven. I am marching through the snow... and I have no shoes. Just rags, tied around my feet. And every step I take... leaves a red print behind me.",
  img=f"A frozen country road in Pennsylvania, December 1777, grey dusk, light snow falling: {EL} marches in a long ragged column of Continental soldiers, his feet wrapped in torn rags tied with string, a flintlock musket on his shoulder, his breath steaming",
  shots=["close on rag-wrapped feet stepping through thin snow on a frozen rutted road",
         "the young soldier's tired face under his worn cocked hat, snowflakes on his eyelashes",
         "a long column of ragged soldiers with muskets trudging up a snowy road into grey dusk"],
  sound="boots and wrapped feet crunching on frozen snow, wind, a drum tapping a slow march far ahead",
  refs=["eli"], must=["exactly one close-up soldier, the rest small in the column", "no visible blood or wounds"]),
 dict(title="Who I am", mode="clip", pov=True, mood="warm",
  v="My name is Eli Parker. I'm seventeen, a private in a Connecticut regiment of the Continental Army. Back home, I milked cows and split rails on my father's farm. I signed up to fight for liberty. Nobody told me the hardest enemy... would be the winter.",
  img=f"Late afternoon on the snowy march, December 1777: {EL} pauses at the roadside, adjusting the grey blanket on his shoulders and looking toward the viewer, other soldiers passing behind him with muskets",
  shots=["the young soldier pulls the blanket tighter around his shoulders and glances up",
         "soldiers pass behind him in a ragged column, some wrapped in blankets",
         "his breath steams as he lifts his musket back onto his shoulder and walks on"],
  sound="wind, footsteps in snow, a man coughing",
  refs=["eli"], must=["exactly one main soldier in the foreground"]),
 dict(title="Valley Forge", mode="clip", pov=True, mood="intrigue",
  v="On the nineteenth of December, we reached a bare, frozen hillside eighteen miles from Philadelphia. There was no town. No barracks. Not even a roof. Just woods and snow, and the ruins of an old iron forge the British had burned. They called the place Valley Forge.",
  img="A bare snowy hillside above a frozen creek in Pennsylvania, 19 December 1777, grey winter light: a ragged column of Continental soldiers arriving over the crest with muskets and a few ox-drawn wagons, bare woods all around, the cold, roofless, long-abandoned blackened stone ruins of a small iron forge by the creek below, burned months ago, snow inside the ruins, NO fire, NO glow, NO smoke from the ruins",
  shots=["the column of soldiers comes over the snowy crest and stops, looking at the empty hillside",
         "the blackened stone ruins of a burned forge beside a half-frozen creek",
         "wind blows snow across an empty hillside of bare trees"],
  sound="cold wind across an open hillside, a creek trickling under ice, an ox lowing",
  refs=["camp"], must=["no huts yet, only bare woods and snow", "soldiers are small in the frame"]),
 # ───────── NEDEN BURADAYIZ ─────────
 dict(title="How we got here", mode="stills", ambience_from="Who I am", pov=False, mood="intrigue",
  v="That autumn had gone badly. We lost the fight at Brandywine Creek in September. Two weeks later, the British marched into Philadelphia, our capital, without firing a shot. We struck back at Germantown in October... and lost again. Now the British were warm in the city's houses. And we were out here.",
  img="The British army in Philadelphia, 1777",
  stills=["Philadelphia, autumn 1777: a column of British redcoat soldiers with muskets marching along a cobbled street of red-brick Georgian houses, townspeople watching from doorways, autumn leaves, NO close-up faces",
          "Night in Philadelphia, winter 1777: warm candlelight glowing in the windows of red-brick houses on a snowy street, a British sentry in a red coat standing by a doorway, smoke from chimneys, NO close-up faces"],
  sound="wind, distant church bell",
  refs=[], must=["British soldiers in red coats", "18th-century brick town"], must_not=["modern objects", "street lamps of the 19th century"]),
 dict(title="Thanksgiving", mode="stills", ambience_from="No shoes", pov=True, mood="tense",
  v="The day before we reached camp, Congress declared a day of Thanksgiving. So we got a special dinner. Each man received half a gill of rice... and a tablespoon of vinegar. That was it. That was Thanksgiving. We laughed about it. What else could we do?",
  img=f"{EL} holding a tin cup with a little rice",
  stills=[f"A cold roadside camp at dusk, December 1777: {EL} sits on a log by a small fire and looks down at a few spoonfuls of plain boiled rice in a battered tin cup, a small wooden spoon in his hand, snow on the ground",
          "Close painterly still life on a frozen log: a battered tin cup with a few spoonfuls of plain rice and a small wooden spoon of vinegar beside it, firelight, snow, NO people"],
  sound="small campfire crackling, wind",
  refs=["eli"], must=["exactly one person"]),
 # ───────── KULÜBELER ─────────
 dict(title="Build or freeze", mode="clip", pov=True, beat="SORUN → ÇÖZÜM", mood="intrigue",
  v="General Washington gave us an order: build huts, or freeze. Twelve men to a hut, fourteen feet by sixteen, with a fireplace at one end. He offered twelve dollars to the first squad in each regiment to finish. So the whole hillside rang with axes, day and night.",
  img=f"Valley Forge, late December 1777: soldiers chopping down trees and notching logs on a snowy hillside, {JO} swinging an axe at a log, the half-built log walls of a small hut beside him, stumps and wood chips on the snow",
  shots=["the red-bearded soldier swings an axe into a log, chips flying into the snow",
         "two soldiers lift a notched log onto the half-built wall of a hut",
         "across the hillside, dozens of men chop trees and raise log walls, smoke from small fires"],
  sound="many axes chopping, a tree cracking and falling, men calling out",
  refs=["jonah", "camp"], must=["18th-century hand tools only: axes, saws", "huts are small, made of logs"]),
 dict(title="The general's tent", mode="stills", ambience_from="Build or freeze", pov=False, mood="warm",
  v="And here's something I never forgot. The general could have taken a warm farmhouse on the very first night. Instead, he lived in his own canvas tent in the snow, the same as us, while we started on the huts. Men noticed that. I noticed it.",
  img="General Washington's tent at Valley Forge",
  stills=["Valley Forge, December 1777: a large white canvas officers' marquee tent pitched alone on a snowy rise among bare trees, warm candlelight glowing through the canvas at dusk, a tall officer in a blue and buff coat seen only FROM BEHIND standing at the entrance, two sentries with muskets, NO faces visible",
          "Inside a canvas officers' tent at night, 1777: a small camp table with a candle, a quill, an inkwell and folded letters, a wool cloak over a chair, frost on the canvas, NO people"],
  sound="wind flapping canvas, a candle hissing",
  refs=[], must=["the officer's face is NOT visible, he is seen from behind"], must_not=["a recognizable face of a real person"]),
 dict(title="Our hut", mode="stills", ambience_from="Build or freeze", pov=True, mood="warm",
  v="Our hut took us nine days. Logs for the walls. Clay and straw packed into the cracks. Bunks of poles and straw, three high. The chimney was made of sticks and mud, and it caught fire twice. But on the first night with a roof over us... nobody said a word. We just slept.",
  img="The inside of the soldiers' hut",
  stills=[f"{EL} and {SM} pack wet clay and straw into the gaps between the logs of their unfinished hut wall, snow on the ground, their breath steaming",
          "Painterly view inside a finished soldiers' log hut at night, Valley Forge 1777: three tiers of bunks made of poles and straw along the walls, soldiers asleep under grey blankets, a small fire in the clay fireplace at the end, NO faces visible"],
  sound="fire crackling, men breathing in sleep, wind outside",
  refs=["eli", "sam", "hut_in"], must=["at most two people awake"]),
 dict(title="My hutmates", mode="stills", ambience_from="Build or freeze", pov=False, mood="warm",
  v="I shared it with eleven men. Jonah Hale, my friend since school, who could carry a log by himself. And Sam Freeman from New London. He was a free man, and he chose that name himself. Sam was the best shot in the regiment... and the only one of us who could cook.",
  img="Eli's hutmates by the fire",
  stills=[f"Inside the smoky log hut by the fireplace: {JO} laughs while sitting on a low bunk mending the torn sleeve of his coat with a needle and thread",
          f"Inside the smoky log hut: {SM} kneels by the clay fireplace and stirs a black iron kettle with a wooden spoon, firelight on his calm face"],
  sound="fire crackling, a kettle bubbling, a man laughing softly",
  refs=["jonah", "sam", "hut_in"], must=["exactly one person in each image"]),
 # ───────── AÇLIK ─────────
 dict(title="Fire cake", mode="stills", ambience_from="Build or freeze", pov=True, mood="tense",
  v="Food was the worst of it. Most days, there was no meat at all. So we made fire cake. Flour and water, mixed into a paste and baked on a hot stone in the fire. If you asked a man what he had for dinner, he'd say: fire cake and water, sir. Fire cake and water.",
  img="Fire cake baking on a stone",
  stills=["Close painterly view of a flat stone in the embers of a small fire, two thin grey-white cakes of flour and water baking on it, blackened at the edges, snow around the fire, NO people",
          f"{SM} uses his fingers to lift a thin blackened fire cake off a hot stone in the hut fireplace and breaks it in half"],
  sound="fire crackling, embers hissing",
  refs=["sam", "hut_in"], must=["exactly one person in the second image"]),
 dict(title="No meat!", mode="clip", pov=True, mood="tense",
  v="Two days after we arrived, a cry started in one hut and spread across the whole camp. No meat! No meat! Thousands of voices in the dark. A surgeon wrote that the valleys echoed it back to us. It wasn't a mutiny. It was hungry men... telling the world they were still there.",
  img="Night at Valley Forge, 21 December 1777, before any huts were built: rows of small white canvas army tents and many campfires on a snowy hillside among tree stumps under a dark sky, groups of ragged soldiers in blankets standing by their fires, shouting together with fists raised",
  shots=["soldiers by a campfire cup their hands to their mouths and shout into the night",
         "the shout spreads to the next row of tents, more men stepping out into the snow",
         "a wide view of the dark hillside dotted with campfires, smoke rising into the night"],
  sound="many men chanting 'No meat!' in the distance, echoing, fire crackling",
  refs=["camp"], must=["18th-century soldiers only", "canvas tents, NO log huts yet", "no weapons pointed at anyone"]),
 dict(title="Barefoot", mode="stills", ambience_from="No shoes", pov=True, mood="tense",
  v="Two days before Christmas, General Washington wrote to Congress. He counted two thousand, eight hundred and ninety-eight men in camp who could not do their duty, because they were barefoot, and had almost no clothes. I saw men stand guard on top of their own hats, just to keep their bare feet off the snow.",
  img="A barefoot sentry standing on his hat",
  stills=["Night at Valley Forge, December 1777: a lone ragged Continental sentry with a musket, wrapped in a blanket, standing on his upturned cocked hat in the snow to keep his bare feet off the ground, a hut row and a small fire behind, his face in shadow",
          "Close painterly view of a quill pen, an inkwell and a half-written letter in neat 18th-century handwriting on a small wooden table by candlelight, frost on the window behind, NO people, the writing is not readable"],
  sound="wind, a sentry stamping his feet",
  refs=["camp"], must=["exactly one person in the first image"], must_not=["readable text or words"]),
 dict(title="Moccasins of raw hide", mode="stills", ambience_from="Build or freeze", pov=True, mood="intrigue",
  v="So I made my own shoes. When the butchers killed a cow, I begged a piece of its raw hide and sewed it around my feet like moccasins, hair side in. They kept my feet off the frozen ground. But as they dried, they turned hard as wood, and cut my ankles to pieces.",
  img="Eli sewing rawhide moccasins",
  stills=[f"Inside the log hut by the fire: {EL} sits on a bunk and sews a rough piece of raw cowhide around his foot with a thick needle and sinew, making a crude moccasin",
          "Close painterly view of a pair of crude hand-sewn moccasins made of stiff raw cowhide with the hair still on, lying on a dirt floor by a fire, NO people"],
  sound="fire crackling, needle pulling through leather",
  refs=["eli", "hut_in"], must=["exactly one person"]),
 dict(title="The smoke", mode="stills", ambience_from="Build or freeze", pov=True, mood="tense",
  v="Inside the huts, the fire kept us alive. But the chimneys pulled badly, and the smoke had nowhere to go. Our eyes were red and running all winter. Twelve men in a room the size of a stable, with wet blankets, smoke, and no fresh air. We didn't know it yet... but that was the real danger.",
  img="Smoky hut interior",
  stills=[f"Inside the smoky log hut, thick grey smoke hanging under the low roof: {EL} rubs his red, watering eyes with the back of his hand, sitting by the fire, other soldiers as dim shapes on the bunks behind",
          "Outside a row of log huts at dawn, Valley Forge 1778: thick smoke leaking from the cracks and the crooked stick-and-clay chimneys, wet blankets hung on a line, snow and mud, NO people"],
  sound="coughing, fire crackling, wind",
  refs=["eli", "hut_in"], must=["exactly one close person"]),
 # ───────── HASTALIK ─────────
 dict(title="The real enemy", mode="stills", ambience_from="No shoes", pov=True, beat="BÜYÜK KIRILMA", mood="tense",
  v="People think the cold killed us at Valley Forge. It wasn't the cold. It was sickness. Typhus. Dysentery. Pneumonia. They moved through the crowded huts like fire. Before we left that camp, nearly two thousand men had died there. And there was never a battle at Valley Forge. Not one.",
  img="A hospital hut",
  stills=["A painterly view of a long log hospital hut at Valley Forge in winter 1778: sick soldiers lying under blankets on straw along both walls, a single surgeon in a dark coat bending over one of them by candlelight, a small fire at the end, faces in shadow, NO blood, NO corpses",
          "A quiet snowy hillside at Valley Forge at dusk, a long row of huts with thin smoke, bare trees, one lantern glowing in a doorway, a lonely mood, NO people"],
  sound="wind, a man coughing in the distance",
  refs=["camp"], must=["no blood, no wounds, no corpses"]),
 dict(title="Inoculation", mode="stills", ambience_from="Build or freeze", pov=True, mood="intrigue",
  v="The one sickness we did fight was smallpox. Washington ordered every man who'd never had it to be inoculated. A doctor cut a small scratch in my arm and put a little of the pox into it. I was sick for two weeks. But I never caught the real thing. Two years before, smallpox had wrecked a whole army of ours in Canada.",
  img="A doctor inoculating Eli",
  stills=[f"Inside a log hospital hut, winter 1778: an army surgeon in a dark coat and white neckcloth makes a tiny scratch with a small lancet on the upper arm of {EL}, who sits on a bench with his sleeve rolled up and looks away, candlelight",
          "Close painterly still life on a wooden table: a small surgeon's lancet, a folded cloth, a little glass vial and a candle, 18th century, NO people"],
  sound="candle hissing, wind outside, a bench creaking",
  refs=["eli", "hut_in"], must=["exactly two people in the first image, no blood"]),
 dict(title="Jonah", mode="stills", ambience_from="No shoes", pov=True, mood="tense",
  v="In January, Jonah got the fever. The biggest, strongest man in our hut... and he couldn't lift his own head. They took him to the hospital hut. I sat with him every night I could. So tell me in the comments: in that hut, what would you want most? Shoes, a blanket... or meat?",
  img="Eli sitting with Jonah",
  stills=[f"Inside a dim hospital hut at night, winter 1778: {EL} sits on a stool beside a straw bed where {JO} lies pale and feverish under a grey blanket, Eli holds a tin cup of water to his lips, one candle"],
  sound="candle hissing, slow breathing, wind",
  refs=["eli", "jonah", "hut_in"], must=["exactly two people", "no blood"]),
 # ───────── ŞUBAT ─────────
 dict(title="The starving time", mode="stills", ambience_from="No shoes", pov=True, mood="tense",
  v="February was the worst. A thaw turned the roads to deep mud, and the wagons couldn't get through. For days, there was nothing in camp. No meat, no bread, not even flour. Back in December, the general had warned Congress that this army might starve, dissolve, or disperse. In February... it nearly did.",
  img="Wagons stuck in mud",
  stills=["A muddy country road in Pennsylvania during a February thaw, 1778: a supply wagon pulled by thin oxen sunk to its axles in deep mud and melting snow, a teamster pushing a wheel, bare trees, grey sky, faces not visible",
          f"Inside the hut, February 1778: {EL} and {SM} sit by a weak fire looking into an empty black kettle, an empty flour sack on the floor"],
  sound="wind, mud squelching, an ox groaning",
  refs=["eli", "sam", "hut_in"], must=["at most two people in each image"]),
 dict(title="Foraging", mode="stills", ambience_from="Build or freeze", pov=True, mood="intrigue",
  v="Then the general sent foraging parties out across the country to find food, and put General Greene in charge of supplies. They came back with herds of cattle, driven through the snow. When the first cattle walked into camp, men cheered like we'd won a battle. Sam cooked a stew that night. I still remember the smell.",
  img="Cattle driven into camp",
  stills=["Late winter 1778, Valley Forge: a herd of cattle driven along a snowy road between rows of log huts by soldiers on foot with sticks, ragged men cheering and waving their hats from the hut doors",
          f"Inside the hut at night: {SM} lifts the lid of a steaming black iron kettle of meat stew over the fire, warm firelight, steam rising"],
  sound="cattle lowing, men cheering, then a kettle bubbling",
  refs=["sam", "camp", "hut_in"], must=["exactly one person in the second image"]),
 dict(title="Jonah comes back", mode="stills", ambience_from="Who I am", pov=True, mood="relief",
  v="And in March, Jonah walked back into our hut on his own two feet. Thin as a rail, but alive. He sat down by the fire, looked at the stew pot, and said: Is that meat? I haven't laughed like that before or since.",
  img="Jonah returns to the hut",
  stills=[f"Inside the log hut, March 1778: a thin, pale {JO} stands in the open doorway leaning on the frame, smiling weakly, daylight and melting snow behind him",
          f"Inside the log hut by the fire: {EL} laughs and hands a steaming tin bowl of stew to a thin {JO}, who sits on a bunk wrapped in a blanket"],
  sound="fire crackling, men laughing",
  refs=["eli", "jonah", "hut_in"], must=["at most two people"]),
 # ───────── STEUBEN ─────────
 dict(title="The Prussian", mode="clip", pov=True, beat="DÖNÜM NOKTASI", mood="intrigue",
  v="In March, a stranger began to drill us. A Prussian officer, Baron von Steuben. He barely spoke English. He shouted at us in German and French, and when he ran out of curses, he'd turn to his aide and say: come and swear at them for me in English! We laughed. But we listened.",
  img="A parade ground on the snowy fields of Valley Forge, March 1778: a company of about a hundred ragged Continental soldiers with muskets standing in straight lines, a stocky foreign officer in a blue coat with a large silver star on his chest seen FROM BEHIND, waving his arms and shouting at them, an aide beside him",
  shots=["the stocky officer seen from behind gestures sharply at the lines of soldiers",
         "soldiers in a ragged line snap their muskets to their shoulders at the same moment",
         "the company marches forward across the muddy field in neat ranks"],
  sound="a drill officer shouting commands, muskets clacking in unison, boots marching in mud",
  refs=["camp"], must=["the officer's face is NOT visible", "18th-century flintlock muskets"], must_not=["a recognizable face of a real person"]),
 dict(title="One army", mode="stills", ambience_from="The Prussian", pov=True, mood="relief",
  v="Before him, every regiment marched its own way. He gave us one way. How to load faster. How to march in a column and swing into a line. How to use the bayonet instead of running. By May, we weren't thirteen states' worth of farmers anymore. We were one army.",
  img="Soldiers drilling in neat lines",
  stills=["Spring 1778, Valley Forge: long neat lines of Continental soldiers in mixed brown and blue coats drilling on a green field with fixed bayonets, all muskets at the same angle, officers with swords, log huts on the hill behind, small figures, NO close-up faces",
          f"{EL} and {SM} stand side by side in a drill line, loading their flintlock muskets with paper cartridges at exactly the same moment, concentrated faces"],
  sound="drums, muskets clacking in unison, marching feet",
  refs=["eli", "sam", "camp"], must=["exactly two close people in the second image"]),
 # ───────── BAHAR ─────────
 dict(title="Spring", mode="stills", ambience_from="Who I am", pov=True, mood="relief",
  v="Spring came slowly. The snow melted, the mud dried, and the creek ran fast again. Wagons got through. New uniforms came in. Somebody's wife sent a whole crate of stockings. I got my first real pair of shoes since the autumn. I put them on... and walked around the hut three times, just to feel it.",
  img="Spring at Valley Forge",
  stills=["Valley Forge in spring 1778: rows of log huts on a green hillside, the last patches of snow melting, blossoming trees, a creek running fast below, soldiers airing blankets in the sun, small figures",
          f"Outside the log hut in spring sunshine: {EL} sits on a stump lacing up a new pair of black leather shoes with buckles, grinning down at his feet"],
  sound="birds singing, a fast creek, wind in new leaves",
  refs=["eli", "camp"], must=["exactly one close person in the second image"]),
 dict(title="The news from France", mode="clip", pov=True, mood="festive",
  v="On the sixth of May, the news came. France had joined the war on our side. The whole army lined up on the parade ground, and fired a running salute, one musket after another, all the way down the line and back. Thirteen cannon. An extra ration of rum. And for the first time... we cheered as winners.",
  img="Valley Forge parade ground, 6 May 1778, bright spring day: long lines of Continental soldiers firing muskets into the air one after another in a rolling salute, white powder smoke drifting along the line, cannon on a hill behind, plain silk regimental flags in single colors with a small painted emblem, cheering men throwing their hats",
  shots=["a long line of soldiers fires muskets into the air one after another, smoke rolling down the line",
         "cannon on the hill fire, white smoke billowing",
         "soldiers throw their hats in the air and cheer"],
  sound="a rolling musket salute, cannon booming, men cheering 'Huzzah!'",
  refs=["camp"], must=["muskets fired into the sky, not at people", "regimental flags, NOT the stars and stripes"]),
 # ───────── ÇIKIŞ ─────────
 dict(title="Marching out", mode="clip", pov=True, mood="relief",
  v="On the nineteenth of June, six months to the day after we arrived, we marched out of Valley Forge. Behind us, the hillside was a field of empty huts. Nine days later, at Monmouth, we met the British in the open field... and this time, they did not run us off it.",
  img="Valley Forge, 19 June 1778, summer morning: a long disciplined column of Continental soldiers in neat ranks marching out along a road, drums and fifes at the front, rows of empty log huts on the green hillside behind",
  shots=["drummers and fifers lead the column out at a steady march",
         "rows of soldiers march in step past the empty huts",
         "the column winds away down the road into green summer country"],
  sound="fifes and drums playing a march, marching feet, birds",
  refs=["camp"], must=["the soldiers march in neat ranks", "summer greenery"]),
 dict(title="The empty hut", mode="stills", ambience_from="Who I am", pov=True, mood="warm",
  v="Before we left, I went back inside our hut one last time. The fireplace was cold. Somebody had carved twelve names into the logs by the door. Jonah's was there. And Sam's. And mine.",
  img="The empty hut",
  stills=["Inside an empty soldiers' log hut in summer, Valley Forge 1778: the bunks bare, the clay fireplace cold, sunlight falling through the open door onto the dirt floor, small carved marks on the log beside the door that are NOT readable, NO people"],
  sound="birds outside, a soft breeze through the door",
  refs=["hut_in"], must_not=["readable text or words", "people"]),
 dict(title="How we survived", mode="stills", ambience_from="Who I am", pov=False, beat="ÖZET", mood="warm",
  v="So how did we survive Valley Forge? Huts we built with our own hands. Fire cake and water. Shoes made of raw hide. Friends who sat with you through the fever. And a stubborn idea: that if we just held on until spring, we could still win. And we did.",
  img="Eli, Jonah and Sam together",
  stills=[f"Summer evening, 1778, by a campfire on the march: {EL}, {JO} and {SM} sit together by the fire, Jonah laughing, Sam cleaning his musket, Eli looking into the flames with a quiet smile"],
  sound="campfire crackling, crickets",
  refs=["eli", "jonah", "sam"], must=["exactly three people"]),
 dict(title="Subscribe", mode="stills", ambience_from="Who I am", pov=False, beat="SABİT KAPANIŞ ÇAĞRISI", mood="outro", own_rules=True,
  v="If you've stayed with me this far, I think this story stayed with you too. If it did, leave a like and subscribe. That's how I know you want more stories like this one, and it helps them reach more people.",
  img="Eli looking at the viewer",
  stills=[f"A warm summer evening at an army camp, 1778: {EL} in a clean new coat sits on a log by a campfire and looks calmly toward the viewer with a small smile, tents and fires behind him"],
  sound="campfire crackling, crickets",
  refs=["eli"], must=["exactly one person"]),
 dict(title="What comes next", mode="stills", ambience_from="No shoes", pov=False, beat="SONRAKİ BÖLÜM", mood="intrigue", own_rules=True,
  v="A hundred and sixty-seven years later, in another December, another American army was trapped in the snow. Christmas, nineteen forty-four, in the frozen forests of Belgium, at a town called Bastogne. Surrounded, outnumbered, and out of almost everything. How did they hold? That story is next.",
  img="Bastogne, December 1944",
  stills=["The Ardennes forest in Belgium, December 1944: snow-covered pine trees, a foxhole dug at the edge of the woods with a few American soldiers in olive-drab overcoats and M1 helmets seen small and FROM BEHIND, mist, cold blue light, a distant small town with a church steeple, NO close-up faces"],
  sound="wind through pine trees, distant artillery rumble",
  refs=[], must=["World War II American soldiers"], must_not=["18th-century soldiers", "blood", "modern objects after 1944"]),
]

SHEET = ("Character reference sheet: on the left a full-body front view standing, "
         "on the right a chest-up portrait of the same person; identical original character in both views, single "
         "character only, no other people. ")
refs = {
 "eli": {"kind": "character", "prompt": SHEET + EL},
 "jonah": {"kind": "character", "prompt": SHEET + JO},
 "sam": {"kind": "character", "prompt": SHEET + SM},
 "hut_in": {"kind": "location", "prompt": "Location reference, single image, NO people: " + HUT_IN},
 "camp": {"kind": "location", "prompt": "Location reference, single image, NO people: " + CAMP},
}
for k, r in refs.items():
    r["n"] = k

ep = {
 "id": "ep008", "version": 1,
 "title": "Valley Forge: Why 2,000 Men Died Without a Single Battle",
 "title_alt": "You're a Soldier at Valley Forge. You Have No Shoes.",
 "title_c": "How Washington's Army Survived the Winter at Valley Forge (1777)",
 "thumbnail": "Bright painterly close-up: the young soldier's frost-bitten face under a worn cocked hat, a ragged blanket on his shoulders, his rag-wrapped feet in the snow in the foreground, log huts and smoke behind; big words 'NO SHOES' (B: '1777', C: no text)",
 "hook_description": "Winter 1777. The Continental Army marches into a frozen Pennsylvania hillside called Valley Forge, many of the men without shoes. Eli, a 17-year-old private from Connecticut, tells how they built a city of log huts, lived on fire cake and water, and held on until spring, when they marched out as a real army.",
 "character": "Eli Parker, a fictional 17-year-old Connecticut private; his hutmates Jonah Hale and Sam Freeman",
 "setting": "Valley Forge, Pennsylvania, 19 December 1777 to 19 June 1778: the Continental Army's winter encampment",
 "style": ("Hand-painted gouache and watercolor storybook illustration, visible brush texture, warm amber firelight "
           "against cold blue winter light, cinematic composition, historically accurate Pennsylvania 1777-78: "
           "ragged mismatched Continental Army clothing (brown, blue and grey wool coats, linen hunting shirts, cocked hats, "
           "round felt hats, wool blankets as cloaks, rags on bare feet), flintlock muskets, small log huts with "
           "clay-chinked walls and stick-and-clay chimneys, bare winter woods, no modern objects, soft painterly detail, "
           "no text, no letters, no watermark"),
 "ref_style": ("Hand-painted gouache and watercolor storybook character reference sheet, same painterly look as the episode, "
               "even neutral lighting, plain warm parchment background, historically accurate Continental Army soldier "
               "clothing of 1777, original person, no text, no labels, no watermark"),
 "motion_suffix": ("Natural real-time motion, no slow motion, soft cuts between shots, painterly style and characters stay "
                   "consistent across shots, no text; historically accurate Valley Forge 1777-78: Continental soldiers in "
                   "ragged 18th-century clothing, flintlock muskets, log huts, no modern objects, no metal stoves, no zippers"),
 "cast": {"Eli": EL, "Jonah": JO, "Sam": SM},
 "preview_scenes": [1, 2, 3],
 "gates": {},
 "hybrid": {"still_resolution": "2k", "still_quality": "medium", "clip_start_resolution": "1k",
            "note": "mode=clip → Seedance; mode=stills → 2K görseller + Ken Burns, ortam sesi ambience_from klibinden"},
 "must": ["historically accurate Valley Forge 1777-78 only (except the final teaser scene)",
          "the same faces, hair and clothes as in the reference images for every named character",
          "painterly gouache look in every frame"],
 "must_not": ["any text, letters, numbers, captions, logos or watermark",
              "a recognizable face of a real historical person (George Washington, Baron von Steuben): show them only from behind or far away",
              "modern objects: metal stoves, stovepipes, zippers, plastic, rubber boots, electric lights, cars, modern rifles",
              "19th- or 20th-century uniforms, Civil War kepis, Napoleonic shakos",
              "neat matching parade uniforms in the winter scenes (the winter army is ragged)",
              "gore, blood, wounds, corpses, skeletons, dead animals",
              "extra fingers, deformed hands, duplicated faces",
              "the same person appearing twice in one frame (clones, twins, duplicated characters)",
              "collage, multiple panels, split screen, several pictures in one image: it must be ONE single continuous scene"],
 "sources": [
  "Joseph Plumb Martin — A Narrative of Some of the Adventures, Dangers and Sufferings of a Revolutionary Soldier (1830)",
  "Albigence Waldo — 'Valley Forge, 1777-1778: Diary of Surgeon Albigence Waldo' (Pennsylvania Magazine of History and Biography, 1897)",
  "George Washington — letter to Henry Laurens, 23 December 1777, and General Orders of 18 December 1777 (Founders Online, National Archives)",
  "Wayne K. Bodle — The Valley Forge Winter: Civilians and Soldiers in War (Penn State University Press, 2002)",
  "Ricardo A. Herrera — Feeding Washington's Army: Surviving the Valley Forge Winter of 1778 (University of North Carolina Press, 2022)",
  "John B. B. Trussell Jr. — Birthplace of an Army: A Study of the Valley Forge Encampment (Pennsylvania Historical and Museum Commission, 1976)",
  "Valley Forge National Historical Park — National Park Service",
 ],
 "disclosure": ("Eli Parker, Jonah Hale and Sam Freeman are fictional characters, built from the diaries, letters and memoirs "
                "of the men who wintered at Valley Forge. The events, places and dates are real. Illustrations and animation "
                "were created with AI tools; narration uses a synthetic voice."),
 "refs": refs,
 "music": [  # 27 Eki müzik planı (Kevin MacLeod, CC BY 4.0)
  {"from": 1, "track": "Frozen_Star.mp3", "title": "Frozen Star", "mood": "soğuk açılış, yürüyüş"},
  {"from": 4, "track": "Lost_Frontier.mp3", "title": "Lost Frontier", "mood": "geçmiş, kulübe yapımı"},
  {"from": 10, "track": "Darkest_Child.mp3", "title": "Darkest Child", "mood": "açlık, yalınayak"},
  {"from": 15, "track": "Ossuary_6_-_Air.mp3", "title": "Ossuary 6 - Air", "mood": "hastalık, Jonah"},
  {"from": 19, "track": "Healing.mp3", "title": "Healing", "mood": "sığırlar, Jonah dönüyor"},
  {"from": 21, "track": "Crossing_the_Chasm.mp3", "title": "Crossing the Chasm", "mood": "von Steuben talimi"},
  {"from": 23, "track": "Eternal_Hope.mp3", "title": "Eternal Hope", "mood": "bahar, Fransa, çıkış"},
  {"from": 26, "track": "Winter_Reflections.mp3", "title": "Winter Reflections", "mood": "boş kulübe, özet"},
  {"from": 28, "track": "Dreams_Become_Real.mp3", "title": "Dreams Become Real", "mood": "kapanış"},
 ],
 "next_episode_tease": "Bastogne, December 1944: the 101st Airborne surrounded in the snow",
 "compact": {"style": "Hand-painted gouache and watercolor storybook illustration, visible brush texture, cold blue winter light with warm amber firelight, cinematic. Historically accurate Valley Forge, Pennsylvania 1777-78: ragged Continental soldiers in mismatched brown, blue and grey wool coats, linen hunting shirts, cocked hats, blankets as cloaks, rags on feet; flintlock muskets; small log huts with clay-chinked walls and stick-and-clay chimneys; bare winter woods. Show only what is described.",
             "avoid": "text, letters, numbers, logos, watermark; recognizable faces of real historical people; metal stoves, glass window panes, stovepipes, zippers, plastic, electric lights, modern rifles; 19th/20th-century uniforms; gore, blood, wounds, corpses; extra fingers, deformed hands, duplicated people; collage or split panels"},
 "voice_engine": None,
 "scenes": [],
}
titles = [s["title"] for s in scenes]
for s in scenes:
    if "eli" in s["refs"] or s["mode"] == "clip": s["pov"] = False  # anlatıcı görünüyorsa / geniş klip karesinde POV eli çelişir
for i, s in enumerate(scenes, 1):
    sc = {"n": i, "title": s["title"], "mode": s["mode"], "pov": s["pov"], "narration": plain(s["v"]),
          "narration_voiced": s["v"], "image_prompt": s["img"], "sound": s["sound"], "refs": s["refs"],
          "voice_mood": s["mood"]}
    if s["mode"] == "clip":
        sc["shots"] = s["shots"]
    else:
        sc["still_prompts"] = s["stills"]
        src = scenes[titles.index(s["ambience_from"])]
        assert src["mode"] == "clip", (s["title"], s["ambience_from"])
        sc["ambience_from"] = titles.index(s["ambience_from"]) + 1
    for k in ("beat", "must", "must_not", "own_rules"):
        if s.get(k):
            sc[k] = s[k]
    sc["pad"] = 2.2 if i in (3, 9, 14, 18, 20, 22, 25, 27) else 0.8  # müzik değişiminden önce nefes
    ep["scenes"].append(sc)
ep006 = S.load_episode("ep006")
ep["voice_engine"] = ep006["voice_engine"]
ep["max_credits"] = 360
if __name__ == "__main__" and "--force" in sys.argv:
    S.save_episode(ep)  # DİKKAT: kapıları ve üretilen varlıkları sıfırlar

clips = [s for s in ep["scenes"] if s["mode"] == "clip"]
stills = sum(len(s["still_prompts"]) for s in ep["scenes"] if s["mode"] == "stills")
cost = len(clips) * (15 + 2.75) + stills * 2.75 + len(refs) * 2.75  # GPT Image 2.5 high 2K + Seedance 720p
w = [len(s["narration"].split()) for s in ep["scenes"]]
print(len(w), "sahne", sum(w), "kelime", min(w), max(w), "≈", round(sum(w)/2.81/1.06/60 + len(w)*0.6/60, 1), "dk")
print("ilk sahne:", w[0], "kelime ≈", round(w[0]/2.81/1.06, 1), "sn")
print("klip:", [s["n"] for s in clips], "| still görsel:", stills, "| tahmini maliyet:", cost, "kredi")
