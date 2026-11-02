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

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



