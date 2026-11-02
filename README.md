# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders (Spotify, YouTube, etc.) generally blend two signals: **content similarity** (how alike two items are based on their own attributes, like audio features or genre tags) and **collaborative signals** (what similar users listened to or liked). They also layer on business logic — freshness, diversity, popularity boosts — and constantly re-rank based on live engagement data. That full pipeline needs huge catalogs and user-behavior history, neither of which this project has.

This version is a **pure content-based recommender**: it has no user listening history to learn from, so it prioritizes a small set of numeric audio features (`energy`, `valence`, `danceability`, `acousticness`) that can be compared directly using distance math, plus a `mood` label as a categorical signal layered on top. This is a deliberate tradeoff — we give up the personalization power of collaborative filtering (which needs many users and interactions) in exchange for a system that is transparent, explainable, and works from day one with just 10 songs and no prior user data.

- **`Song` features:** `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`. Of these, `energy`, `valence`, `danceability`, and `acousticness` are used as the numeric similarity vector because they're already normalized to a 0–1 scale; `mood` and `genre` are used as categorical bonuses; `tempo_bpm` is available but not weighted in the default scoring (different scale, and correlated with energy).
- **`UserProfile` stores:** a target feature vector (the same four numeric dimensions), a preferred `mood`, and preferred `genre`(s), representing what the listener wants right now rather than a history of past plays.
- **`Recommender` scoring:** for each candidate song, it computes a Euclidean distance between the song's numeric vector and the user's target vector, converts that into a similarity score in [0, 1], and adds two small flat bonuses: a larger one (e.g. +0.15) if the song's `mood` matches the user's preferred mood, and a smaller one (e.g. +0.05) if the song's `genre` is in the user's preferred genres. This keeps numeric audio similarity as the dominant signal while letting mood and genre nudge the ranking, with mood weighted higher since it's the more direct signal of listening intent.
- **Choosing recommendations:** songs are sorted by final score (similarity + mood bonus + genre bonus) in descending order, and the top N are returned. This keeps the logic simple and explainable — every recommendation can be traced back to "closest audio match, plus whether the mood and/or genre matched."

The key tradeoff throughout: we favor **simplicity and explainability** over the accuracy a larger, behavior-driven system could achieve. A production recommender would weight collaborative signals, freshness, and diversity far more heavily; this one intentionally stays small and transparent so each scoring decision is easy to inspect and reason about.

### Data Flow

```
[1] INPUT — User Prefs
--------------------------------
  UserProfile
    target_energy          (0-1)
    target_valence         (0-1)
    target_danceability    (0-1)
    target_acousticness    (0-1)
    target_mood             (e.g. "chill")
    preferred_genres        (e.g. ["pop", "indie pop"])

        |
        v

[2] PROCESS — The Loop (score every song in songs.csv)
--------------------------------------------------------
  for each Song S in songs.csv:

      1. Build numeric vectors
            T = (target_energy, target_valence,
                 target_danceability, target_acousticness)
            V = (S.energy, S.valence,
                 S.danceability, S.acousticness)

      2. distance = euclidean(T, V)
         similarity = 1 - (distance / 2)        -> [0, 1]

      3. mood_bonus  = 0.15 if S.mood  == target_mood         else 0
         genre_bonus = 0.05 if S.genre in preferred_genres    else 0

      4. final_score = similarity + mood_bonus + genre_bonus

      store (S, final_score)

        |
        v

[3] OUTPUT — The Ranking (Top K)
--------------------------------------------------------
  sort all (S, final_score) pairs by final_score, descending
  break ties by higher danceability (or catalog order)
  return first K results

  Recommendations:
    1. Song A  (score 1.10)  <- closest audio match + mood + genre match
    2. Song B  (score 1.00)  <- strong audio match + mood match
    3. Song C  (score 0.93)  <- strong audio match + genre match only
    ...
```

### Features Used

The catalog has grown to span 13 genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, house, metal, classical, latin, r&b, gospel, punk, reggae, folk, electronic, blues, k-pop) and 16 moods (happy, chill, intense, relaxed, moody, focused, nostalgic, energetic, angry, peaceful, romantic, sad, hopeful, playful, melancholic, dreamy, triumphant). With that much more variety, matching on `mood` alone is too narrow — most songs in the catalog won't share the user's exact mood label, so the bonus rarely fires and recommendations would fall back almost entirely on the numeric vector. To keep categorical matching meaningful at this size, the `UserProfile` now also tracks a preferred `genre` (or a short list of acceptable genres) as a second, smaller bonus layered on top of the mood bonus, so a user can be rewarded for a genre fit even when an exact mood match isn't available.

**`Song` object:**
- `genre` — categorical, now also used as a (smaller) bonus signal in scoring, not just metadata
- `mood` — categorical, used as the primary bonus signal in scoring
- `energy` — numeric (0–1), part of the similarity vector
- `valence` — numeric (0–1), part of the similarity vector
- `danceability` — numeric (0–1), part of the similarity vector
- `acousticness` — numeric (0–1), part of the similarity vector
- `tempo_bpm` — numeric (60–170ish), stored but not weighted in default scoring (different scale, correlated with energy)

**`UserProfile` object:**
- `target_mood` — the mood the user wants to match (categorical, drives the larger mood bonus)
- `preferred_genres` — one genre, or a short list of acceptable genres (categorical, drives the smaller genre bonus)
- `target_energy` — numeric (0–1), target value for the energy dimension
- `target_valence` — numeric (0–1), target value for the valence dimension
- `target_danceability` — numeric (0–1), target value for the danceability dimension
- `target_acousticness` — numeric (0–1), target value for the acousticness dimension

Together, `UserProfile`'s four numeric targets and `Song`'s four numeric features form the two vectors compared in the similarity score, while `target_mood` vs. `Song.mood` and `preferred_genres` vs. `Song.genre` form two independent categorical bonuses (mood weighted higher than genre, since mood is the more direct signal of what the user wants to hear right now).

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output from running `python src/main.py` with the starter profile `{"genre": "pop", "mood": "happy", "energy": 0.8}`:

```
Loaded songs: 28

Based on your preferences ({'genre': 'pop', 'mood': 'happy', 'energy': 0.8}), here are your top 5 recommendations:

1. Sunrise City by Neon Echo (pop, happy) — Score: 1.18
   Why: Recommended because its audio profile is a 98% match to what you're looking for, it matches your 'happy' mood, and it's in the 'pop' genre you prefer.

2. Rooftop Lights by Indigo Parade (indie pop, happy) — Score: 1.11
   Why: Recommended because its audio profile is a 96% match to what you're looking for, and it matches your 'happy' mood.

3. Dancehall Riot by Mellow Tide (reggae, energetic) — Score: 0.98
   Why: Recommended because its audio profile is a 98% match to what you're looking for.

4. Paper Crown by Yuki Starling (k-pop, triumphant) — Score: 0.95
   Why: Recommended because its audio profile is a 95% match to what you're looking for.

5. Night Drive Loop by Neon Echo (synthwave, moody) — Score: 0.95
   Why: Recommended because its audio profile is a 95% match to what you're looking for.
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

### Standard User Profiles

**High-Energy Pop** — `{'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'valence': 0.85, 'danceability': 0.85, 'acousticness': 0.1}`

```
1. Sunrise City by Neon Echo (pop, happy) — Score: 1.14
   Why: Recommended because its audio profile is a 94% match to what you're looking for, it matches your 'happy' mood, and it's in the 'pop' genre you prefer.
2. Rooftop Lights by Indigo Parade (indie pop, happy) — Score: 1.00
   Why: Recommended because its audio profile is a 85% match to what you're looking for, and it matches your 'happy' mood.
3. Gym Hero by Max Pulse (pop, intense) — Score: 1.00
   Why: Recommended because its audio profile is a 95% match to what you're looking for, and it's in the 'pop' genre you prefer.
4. Paper Crown by Yuki Starling (k-pop, triumphant) — Score: 0.96
   Why: Recommended because its audio profile is a 96% match to what you're looking for.
5. Velvet Static by DJ Kessler (house, energetic) — Score: 0.93
   Why: Recommended because its audio profile is a 93% match to what you're looking for.
```

**Chill Lofi** — `{'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'valence': 0.55, 'danceability': 0.55, 'acousticness': 0.8}`

```
1. Library Rain by Paper Lanterns (lofi, chill) — Score: 1.16
   Why: Recommended because its audio profile is a 96% match to what you're looking for, it matches your 'chill' mood, and it's in the 'lofi' genre you prefer.
2. Midnight Coding by LoRoom (lofi, chill) — Score: 1.13
   Why: Recommended because its audio profile is a 93% match to what you're looking for, it matches your 'chill' mood, and it's in the 'lofi' genre you prefer.
3. Spacewalk Thoughts by Orbit Bloom (ambient, chill) — Score: 1.04
   Why: Recommended because its audio profile is a 89% match to what you're looking for, and it matches your 'chill' mood.
4. Focus Flow by LoRoom (lofi, focused) — Score: 1.01
   Why: Recommended because its audio profile is a 96% match to what you're looking for, and it's in the 'lofi' genre you prefer.
5. Coffee Shop Stories by Slow Stereo (jazz, relaxed) — Score: 0.91
   Why: Recommended because its audio profile is a 91% match to what you're looking for.
```

**Deep Intense Rock** — `{'genre': 'rock', 'mood': 'intense', 'energy': 0.9, 'valence': 0.45, 'danceability': 0.6, 'acousticness': 0.1}`

```
1. Storm Runner by Voltline (rock, intense) — Score: 1.17
   Why: Recommended because its audio profile is a 97% match to what you're looking for, it matches your 'intense' mood, and it's in the 'rock' genre you prefer.
2. Riot Gear by Static Fang (punk, angry) — Score: 0.94
   Why: Recommended because its audio profile is a 94% match to what you're looking for.
3. Gym Hero by Max Pulse (pop, intense) — Score: 0.94
   Why: Recommended because its audio profile is a 79% match to what you're looking for, and it matches your 'intense' mood.
4. Thunderclap Tuesday by Voltline (rock, triumphant) — Score: 0.90
   Why: Recommended because its audio profile is a 85% match to what you're looking for, and it's in the 'rock' genre you prefer.
5. Night Drive Loop by Neon Echo (synthwave, moody) — Score: 0.88
   Why: Recommended because its audio profile is a 88% match to what you're looking for.
```

### Adversarial / Edge Case Profiles

These profiles were designed to see if the scoring logic could be "tricked" or produce unexpected results.

**High-Energy "Sad" (conflicting signals)** — `{'mood': 'sad', 'energy': 0.9, 'valence': 0.1, 'danceability': 0.9, 'acousticness': 0.0}`
A user who wants a `sad` mood but a high-energy, highly danceable, zero-acoustic sound — a combination that doesn't really exist in real music (sad songs are rarely high-energy dance tracks).

```
1. Riot Gear by Static Fang (punk, angry) — Score: 0.80
   Why: Recommended because its audio profile is a 80% match to what you're looking for.
2. Broken Window by Grayscale Hymn (metal, angry) — Score: 0.78
   Why: Recommended because its audio profile is a 78% match to what you're looking for.
3. Storm Runner by Voltline (rock, intense) — Score: 0.77
   Why: Recommended because its audio profile is a 77% match to what you're looking for.
4. Night Drive Loop by Neon Echo (synthwave, moody) — Score: 0.75
   Why: Recommended because its audio profile is a 75% match to what you're looking for.
5. Velvet Static by DJ Kessler (house, energetic) — Score: 0.69
   Why: Recommended because its audio profile is a 69% match to what you're looking for.
```
**Result:** No song in the catalog has `mood == "sad"` *and* matches this audio profile, so the mood bonus never fires for anyone. The system silently falls back to pure numeric similarity and hands back angry/intense songs — technically the closest audio matches, but completely missing the "sad" intent. This is the expected, honest behavior of a content-based system with no fallback/override logic: it doesn't flag the contradiction, it just quietly ignores the mood bonus.

**Nonexistent genre and mood** — `{'genre': 'opera', 'mood': 'euphoric', 'energy': 0.5, 'valence': 0.5, 'danceability': 0.5, 'acousticness': 0.5}`
Neither `opera` nor `euphoric` exist anywhere in `songs.csv`.

```
1. Clay Pigeons by Dust Devil Trio (blues, moody) — Score: 0.93
   Why: Recommended because its audio profile is a 92% match to what you're looking for.
2. Backroad Sunset by Clay & Wren (country, nostalgic) — Score: 0.91
   Why: Recommended because its audio profile is a 91% match to what you're looking for.
3. Slow Burn by Reverie Sol (r&b, romantic) — Score: 0.89
   Why: Recommended because its audio profile is a 89% match to what you're looking for.
4. Midnight Coding by LoRoom (lofi, chill) — Score: 0.87
   Why: Recommended because its audio profile is a 87% match to what you're looking for.
5. City Lullaby by Reverie Sol (r&b, sad) — Score: 0.85
   Why: Recommended because its audio profile is a 85% match to what you're looking for.
```
**Result:** No crash, no error — the system doesn't validate that `genre`/`mood` exist in the catalog, it just never finds a match, so neither bonus ever applies and results fall back entirely to audio similarity. This confirms the scoring logic degrades gracefully rather than breaking on unrecognized categorical input.

**Happy Metal (contradictory genre + mood + audio target)** — `{'genre': 'metal', 'mood': 'happy', 'energy': 1.0, 'valence': 0.0, 'danceability': 1.0, 'acousticness': 0.0}`
Asks for the `metal` genre and a `happy` mood simultaneously, with a `valence` target of 0.0 (maximally sad-sounding) — an internally contradictory profile.

```
1. Broken Window by Grayscale Hymn (metal, angry) — Score: 0.77
   Why: Recommended because its audio profile is a 72% match to what you're looking for, and it's in the 'metal' genre you prefer.
2. Riot Gear by Static Fang (punk, angry) — Score: 0.73
   Why: Recommended because its audio profile is a 73% match to what you're looking for.
3. Sunrise City by Neon Echo (pop, happy) — Score: 0.70
   Why: Recommended because its audio profile is a 55% match to what you're looking for, and it matches your 'happy' mood.
4. Storm Runner by Voltline (rock, intense) — Score: 0.70
   Why: Recommended because its audio profile is a 70% match to what you're looking for.
5. Rooftop Lights by Indigo Parade (indie pop, happy) — Score: 0.68
   Why: Recommended because its audio profile is a 53% match to what you're looking for, and it matches your 'happy' mood.
```
**Result:** This is where the scoring logic gets genuinely "tricked." `Broken Window` has a weaker raw audio match (72%) than several other songs, but the genre bonus (+0.05) is enough to push it to #1 over `Riot Gear`, which has a *higher* raw similarity (73%) but no genre match. It also surfaces both the only `metal` song (matching the stated genre, despite sounding nothing like "happy") and genuinely happy pop songs (matching the stated mood, despite not being metal) side by side — a direct symptom of feeding the system a self-contradictory profile. This confirms the small bonuses can occasionally reorder close results in ways a listener might find surprising.

### Weight Shift Experiment: Swapping Mood and Genre Bonuses

To see how sensitive the ranking is to the bonus weights, we temporarily swapped `MOOD_BONUS` and `GENRE_BONUS` (baseline: mood=0.15, genre=0.05 → shifted: mood=0.05, genre=0.15) and re-ran two profiles.

**Deep Intense Rock** — `{'genre': 'rock', 'mood': 'intense', ...}`

```
BASELINE (mood=0.15, genre=0.05)              SHIFTED (mood=0.05, genre=0.15)
1. Storm Runner       (rock, intense) 1.17     1. Storm Runner       (rock, intense) 1.17
2. Riot Gear          (punk, angry)   0.94     2. Thunderclap Tuesday(rock, triumph) 1.00
3. Gym Hero           (pop, intense)  0.94     3. Riot Gear          (punk, angry)   0.94
4. Thunderclap Tuesday(rock, triumph) 0.90     4. Night Drive Loop   (synthwave)     0.88
5. Night Drive Loop   (synthwave)     0.88     5. Broken Window      (metal, angry)  0.86
```

**Adversarial: Happy Metal** — `{'genre': 'metal', 'mood': 'happy', 'valence': 0.0, ...}`

```
BASELINE (mood=0.15, genre=0.05)              SHIFTED (mood=0.05, genre=0.15)
1. Broken Window   (metal, angry)  0.77        1. Broken Window   (metal, angry)  0.87
2. Riot Gear       (punk, angry)   0.73        2. Riot Gear       (punk, angry)   0.73
3. Sunrise City     (pop, happy)   0.70        3. Storm Runner    (rock, intense) 0.70
4. Storm Runner    (rock, intense) 0.70        4. Night Drive Loop(synthwave)     0.67
5. Rooftop Lights   (indie pop, happy) 0.68     5. Velvet Static  (house, energetic)0.63
```

**Observations:**
- **Rankings did change**, but not wildly — in "Deep Intense Rock," `Thunderclap Tuesday` (rock, genre match but no mood match) jumped from #4 to #2 once the genre bonus outweighed the mood bonus, pushing out `Gym Hero` (mood match, no genre match) entirely from the top 5.
- In the "Happy Metal" profile, giving genre more weight made `Broken Window`'s lead even bigger (0.77 → 0.87), and it also bumped `Storm Runner` above `Sunrise City`/`Rooftop Lights` — the two songs whose *only* edge was a mood match lost ground once mood was worth less, dropping entirely out of the top 5.
- This confirms the bonuses are doing real, measurable work: they're small enough that they rarely overturn a strong audio-similarity lead (`Storm Runner` stayed #1 in both runs), but large enough to flip the order of songs that are otherwise close — meaning the 0.15/0.05 split is a real design decision with real consequences, not just cosmetic.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

### Potential Biases

- **Catalog imbalance / popularity skew** — genres and moods aren't evenly represented in `songs.csv` (e.g. more pop/lofi songs than metal or gospel), so the recommender is statistically more likely to surface those genres regardless of fit, simply because they have more entries competing for high scores.
- **Artist repetition** — some artists (e.g. Neon Echo, LoRoom, Reverie Sol) appear multiple times across different songs. A good numeric/mood match can cause the same artist to dominate a user's top-K list, narrowing exposure rather than diversifying it.
- **Mood label subjectivity** — moods like "chill," "relaxed," and "dreamy" overlap conceptually but are treated as strictly equal/unequal in the mood bonus. This binary treatment can arbitrarily reward or withhold the bonus for songs that are actually close in feel, baking in whoever's subjective labeling choices went into the CSV.
- **Feature weighting bias** — the 0.15/0.05 mood-vs-genre split and the choice to exclude `tempo_bpm` from scoring are arbitrary design decisions, not derived from user feedback or behavior data. They encode the designer's assumptions about what matters, which may not reflect real listener preferences.
- **Cold-start / majority-fit bias** — because there's no listening history, every user with a similar `target_*` vector gets nearly identical recommendations. This flattens individuality and can systematically underserve users whose taste falls in sparsely populated regions of the feature space (e.g. high-energy + high-acousticness, which barely exists in the catalog).
- **Audio-feature proxy bias** — numeric features like `energy` and `valence` are stand-ins for subjective qualities and may have been tagged inconsistently or with cultural/genre bias (e.g. genres with quieter production, like folk or classical, may be systematically scored as low-energy even when emotionally intense).

### Measured: Does the Same Song Keep Winning?

To check whether a handful of songs quietly dominate every recommendation list, we ran 100 randomized user profiles (random `energy`/`valence`/`danceability`/`acousticness` targets, random `mood`, random `genre`) through `recommend_songs` and tallied how often each song and artist showed up.

```
Ran 100 random profiles, looked at top-5 each time (500 total slots)

Top-1 (rank #1) frequency across all runs:
  Clay Pigeons: 10/100 times (10%)
  City Lullaby: 9/100 times (9%)
  Slow Burn: 9/100 times (9%)
  Tidepool Static: 6/100 times (6%)
  Lantern Hollow: 6/100 times (6%)
  Rust Belt Ballad: 6/100 times (6%)
  Coffee Shop Stories: 5/100 times (5%)
  Midnight Coding: 5/100 times (5%)
  Library Rain: 4/100 times (4%)
  Focus Flow: 4/100 times (4%)

Overall appearances in top-5 (by song title):
  Clay Pigeons: 39 times
  Focus Flow: 35 times
  Midnight Coding: 34 times
  City Lullaby: 31 times
  Rust Belt Ballad: 31 times
  Slow Burn: 30 times
  Library Rain: 28 times
  Tidepool Static: 26 times
  Backroad Sunset: 24 times
  Spacewalk Thoughts: 24 times

Overall appearances in top-5 (by artist):
  LoRoom: 69 times
  Reverie Sol: 61 times
  Orbit Bloom: 50 times
  Dust Devil Trio: 39 times
  Harlan Creek: 31 times
  Wen Liu: 30 times
  Paper Lanterns: 28 times
  Clay & Wren: 24 times
  Voltline: 22 times
  Slow Stereo: 22 times

Total unique songs in catalog: 28
Unique songs that ever appeared in a top-5: 28
```

**Findings:**
- No single song wins every list — all 28 songs in the catalog appeared in a top-5 at least once across the 100 runs, so the system isn't fully degenerate.
- There *is* a clear **"center of the catalog" bias**: songs with mid-range, unremarkable audio features (e.g. "Clay Pigeons," "City Lullaby," "Slow Burn" — all around energy 0.3–0.5, valence 0.3–0.7) end up close to almost *any* random target vector by Euclidean distance, so they rack up disproportionate top-5 appearances (30–39 out of 500 slots) regardless of what the user actually asked for.
- **Artist repetition compounds this** — artists with more than one song in the catalog (LoRoom, Reverie Sol, Orbit Bloom) appear in the top-5 far more often (50–69 times) than artists with only one song, purely because they have more entries competing for the same slots, not because of any genuine taste match. This is a direct, measured confirmation of the catalog-imbalance and artist-repetition biases noted above.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



