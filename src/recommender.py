import csv
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

NUMERIC_FEATURES = ["energy", "valence", "danceability", "acousticness"]
MOOD_BONUS = 0.15
GENRE_BONUS = 0.05

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Reads songs.csv into a list of song dicts with properly typed fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a song's audio similarity plus mood/genre bonuses against user preferences."""
    # 1. Numeric similarity: Euclidean distance over the shared audio features,
    #    normalized into a [0, 1] similarity score.
    used_features = [f for f in NUMERIC_FEATURES if f in user_prefs and f in song]
    if used_features:
        squared_diffs = [(user_prefs[f] - song[f]) ** 2 for f in used_features]
        distance = math.sqrt(sum(squared_diffs))
        max_distance = math.sqrt(len(used_features))
        similarity = 1 - (distance / max_distance)
    else:
        similarity = 0.0

    score = similarity
    reasons = [f"its audio profile is a {similarity:.0%} match to what you're looking for"]

    # 2. Mood bonus: larger bonus, since mood is the stronger signal of intent.
    target_mood = user_prefs.get("mood")
    if target_mood and song.get("mood") == target_mood:
        score += MOOD_BONUS
        reasons.append(f"it matches your '{target_mood}' mood")

    # 3. Genre bonus: smaller bonus, since genre is a weaker/secondary signal.
    preferred_genres = user_prefs.get("preferred_genres")
    if preferred_genres is None and "genre" in user_prefs:
        preferred_genres = [user_prefs["genre"]]
    if preferred_genres and song.get("genre") in preferred_genres:
        score += GENRE_BONUS
        reasons.append(f"it's in the '{song.get('genre')}' genre you prefer")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song against user preferences and returns the top k, highest score first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        if len(reasons) > 1:
            explanation = ", and ".join([", ".join(reasons[:-1]), reasons[-1]])
        else:
            explanation = reasons[0]
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)

    return scored[:k]
