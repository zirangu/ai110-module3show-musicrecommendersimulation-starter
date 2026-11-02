# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

**MoodMatch CLI 1.0**

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

**Goal / task:** Given a small target "vibe" (how energetic, how happy-sounding, how danceable, how acoustic a song should be, plus an optional mood and genre), the system predicts which songs in a small catalog are the closest match and returns the top 5, each with a plain-English reason. It's trying to answer: "out of the songs I know about, which ones sound and feel most like what this person is asking for right now?"

**Assumptions:** It assumes the user can describe their mood as a short list of numbers and labels rather than giving feedback on actual songs, and it assumes there's no listening history to learn from — every recommendation starts from zero.

**Intended use:** This is a **classroom exploration tool**, built to learn and demonstrate how content-based recommenders work, not a production app. It's meant to be run from the command line against the tiny `data/songs.csv` catalog (currently 28 songs) to see how scoring and ranking logic behaves, including its weaknesses.

**Non-intended use:** This should **not** be used to make real recommendations for real listeners, relied on for an actual music streaming product, or treated as a fair/accurate measure of listener taste — the catalog is far too small and the scoring weights (0.15 mood bonus, 0.05 genre bonus) are hand-picked design choices, not validated against real user behavior. It also should not be used to draw conclusions about which genres or moods are objectively "better" matches for any audience — the catalog imbalance (e.g. more pop/lofi songs than metal/gospel) would bias any such conclusion.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

**Plain-language explanation:**

Think of each song as a point with four "audio dials" turned somewhere between 0 and 1: how energetic it is, how positive/upbeat it sounds, how danceable it is, and how acoustic (unplugged) it feels. When you tell the system what you're in the mood for, it sets those same four dials to your target, then checks every song in the catalog and measures how close its dials are to yours — the closer the dials line up, the higher the "audio match" score it gets.

On top of that base match, the system gives two small bonuses: a bigger one if the song's mood label (like "chill" or "happy") matches what you asked for, since mood is the clearest hint of what you want to hear right now, and a smaller one if the song's genre is one you said you like, since genre is more about general taste than the specific moment. A song still needs a genuinely close audio match to rank near the top — the bonuses only help break ties or nudge close calls, they can't rescue a song whose overall vibe is far off from what you asked for. Finally, the system sorts every song by its total score and hands back the highest-scoring ones, along with a plain-English reason for each (e.g., "it's a 95% audio match, and it matches your happy mood").

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

**Dataset:** `data/songs.csv` has **28 songs**, each with `title`, `artist`, `genre`, `mood`, and four numeric audio features (`energy`, `valence`, `danceability`, `acousticness`, all 0-1) plus `tempo_bpm`. The starter file had 10 songs across 7 genres and 6 moods; we added 18 more songs to bring it to 13 genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, house, metal, classical, latin, r&b, gospel, punk, reggae, folk, electronic, blues, k-pop) and 16 moods (happy, chill, intense, relaxed, moody, focused, nostalgic, energetic, angry, peaceful, romantic, sad, hopeful, playful, melancholic, dreamy, triumphant). Even with the additions, genre/mood representation is uneven — most genres have only 1-2 songs, while a few artists (LoRoom, Reverie Sol, Neon Echo) appear more than once. The dataset has no lyrics, no listening/skip history, no release date, and no indication of cultural/regional origin — so the system has no way to reason about anything beyond these numeric and label fields.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

**Where it works well:** When a user's target profile closely resembles an actual song that exists in the catalog (e.g. "High-Energy Pop" matching "Sunrise City," or "Chill Lofi" matching "Library Rain"), the top result is intuitive and the explanation is easy to trust. The numeric similarity score correctly separates opposite-feeling profiles — a high-energy/low-acoustic target and a low-energy/high-acoustic target produce almost entirely non-overlapping top-5 lists, which matches what you'd expect from real music. The mood and genre bonuses also work as intended for tie-breaking: when two songs have a near-identical audio match, the one that also carries the right mood or genre label consistently wins.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

**Discovered weakness (feature removal experiment):** Running the same "High-Energy Pop" profile (`energy=0.9, valence=0.85, mood=happy, genre=pop`) with the mood check disabled flipped the #1 and #2 results: "Gym Hero" (mood=`intense`) overtook "Sunrise City" (mood=`happy`), even though the user explicitly wanted a happy song. This happens because `energy`, `danceability`, and `acousticness` alone can't reliably distinguish "happy and energetic" from "intense and energetic" — both moods produce a similar numeric profile, and `valence` alone isn't a strong enough signal to separate them without the categorical mood label. This is a real filter-bubble risk: any user who leans on high energy without specifying mood could get systematically pushed toward whichever of "happy"/"intense"/"triumphant" happens to have the closest acousticness/danceability profile, regardless of the emotional tone they actually want. By contrast, doubling the weight on `energy` relative to `genre` barely changed the top-5 at all in the same test — suggesting the system is far more sensitive to losing a categorical signal like mood than to re-weighting the numeric features, and that the four numeric features are somewhat redundant with each other for distinguishing emotional tone.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

**Profiles tested:** "High-Energy Pop" (`energy=0.9, valence=0.85, danceability=0.85, acousticness=0.1, mood=happy, genre=pop`), "Chill Lofi" (`energy=0.35, valence=0.55, danceability=0.55, acousticness=0.8, mood=chill, genre=lofi`), "Deep Intense Rock" (`energy=0.9, valence=0.45, danceability=0.6, acousticness=0.1, mood=intense, genre=rock`), plus three adversarial profiles (a high-energy "sad" profile, a profile asking for a genre/mood that doesn't exist in the catalog, and a self-contradictory "happy metal" profile), and 100 randomized profiles used to check for repeat-offender songs. See the README's "Experiments You Tried" section for full output.

**What I looked for:** whether the top result's genre and mood actually matched the request, whether the numeric audio features of the recommendations made intuitive sense next to the target, and whether the system broke (crashed, returned nothing, or silently misbehaved) on inputs that don't fit the catalog.

**What surprised me:** the system never crashes or returns nothing, even on nonsense input like `genre=opera, mood=euphoric` — it just quietly falls back to pure numeric similarity, which feels "safe" but can also hide the fact that the user's actual request was never matched at all. I was also surprised how much a single small bonus (+0.05 for genre) could reorder two songs with very close scores, and how little doubling the energy weight changed anything, while removing the mood check entirely changed the #1 result.

**Pairwise comparisons:**

- **High-Energy Pop vs. Chill Lofi** — Nearly the opposite recommendation list. The pop profile's high `energy`/`danceability`/`valence` and low `acousticness` target pulls up upbeat, electronic-leaning songs ("Sunrise City," "Gym Hero"), while the lofi profile's low energy and high acousticness target pulls up quiet, unplugged-sounding songs ("Library Rain," "Midnight Coding"). This makes sense — the two profiles ask for audio features that are nearly inverses of each other, so the systems' two top-5 lists barely overlap.
- **Deep Intense Rock vs. High-Energy Pop** — Both ask for high `energy` (0.9), so some loud/fast songs show up in both lists ("Gym Hero" appears near the top of both). But Rock's lower `valence` (0.45, less "happy-sounding") and lower `acousticness` target pulls in angrier, grittier songs ("Riot Gear," "Broken Window"), while Pop's high `valence` (0.85) keeps the list skewed toward upbeat, cheerful-sounding tracks. This confirms `valence` is doing real work separating "angry-energetic" from "happy-energetic" even when `energy` itself is identical.
- **High-Energy Pop vs. the "High-Energy Sad" adversarial profile** — Same high-energy target, opposite `valence` and `mood`. The Pop profile keeps "Sunrise City"/"Gym Hero" at the top; the "sad" profile instead surfaces angry/intense songs ("Riot Gear," "Broken Window") because no "sad" song in the catalog is also high-energy — so the mood bonus for "sad" never fires for anyone, and the ranking falls back to whichever high-energy songs are numerically closest. This is a valid, explainable outcome, but it also reveals that the system has no way to tell the user "no song really matches what you asked for" — it just gives its best (numeric) guess.

**Why "Gym Hero" keeps showing up for "Happy Pop" users (plain language):** Think of each song as having a few dials — not just mood, but things a computer can measure directly, like how loud/fast it is (energy) and how danceable it is. "Gym Hero" is tagged with the mood "intense," not "happy," but on those measurable dials it's turned up almost exactly where a "happy, energetic pop" fan would want (very high energy, very danceable, upbeat-sounding). Our system mostly judges songs by those dials, with the mood label as a smaller "bonus" on top rather than a strict requirement. So even though "Gym Hero" doesn't carry the "happy" label, its sound is close enough to what a happy-pop fan asked for that it earns a high score anyway — it's basically a workout anthem that sounds similar to a happy pop song, even if the artist intended it to feel more intense than cheerful. This is a reasonable design choice (it keeps recommendations from being too strict about labels), but it's also exactly the kind of mismatch worth watching for: the system can mistake "sounds similar" for "is what you actually wanted."

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

1. **Add an artist/result diversity cap** so one or two artists with multiple catalog entries (LoRoom, Reverie Sol) can't crowd out everyone else's top-5, since our 100-random-profile test showed they appear disproportionately often.
2. **Let the system say "no good match"** instead of always returning 5 songs — right now, a contradictory or out-of-catalog request (e.g. "sad" + high-energy) silently falls back to its best numeric guess, which can quietly mislead a user into thinking a real match was found.
3. **Tune the bonus weights against real feedback** instead of hand-picked constants (0.15 mood, 0.05 genre) — e.g. by asking a few test users which of two ranked lists feels more "right," rather than guessing.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

Building even this small recommender made clear how much a "recommendation" is really just a distance calculation wearing a friendly explanation. Nothing in the system actually understands music — it just measures how close a handful of numbers are and reports back a percentage. The most interesting discovery was how easily the numeric features alone can produce a technically-correct-but-wrong result, like recommending "Gym Hero" (intense) to someone who wanted "happy" pop, simply because its energy and danceability happened to line up. That reshaped how I think about real apps like Spotify: a feature like "energy" or "danceability" is a useful proxy, but proxies can quietly stand in for things they don't actually measure (like emotional tone), and the only way to catch that is to test with real, sometimes contradictory, user intent — not just the "clean" cases.
