import csv
from pathlib import Path
from typing import List, Dict, Tuple

from dataclasses import dataclass, asdict

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
        """Return the top k Song objects for the given user profile."""
        prefs = _user_profile_to_prefs(user)
        song_dicts = [_song_to_dict(s) for s in self.songs]
        ranked = recommend_songs(prefs, song_dicts, k=k)
        id_order = [item[0]["id"] for item in ranked]
        by_id = {s.id: s for s in self.songs}
        return [by_id[sid] for sid in id_order]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Build a human-readable explanation for why a song fits the profile."""
        prefs = _user_profile_to_prefs(user)
        _, reasons = score_song(prefs, _song_to_dict(song))
        if not reasons:
            return "No strong matches to your stated preferences."
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load the song catalog from CSV into a list of dictionaries with typed numbers."""
    path = Path(csv_path)
    songs: List[Dict] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            songs.append(
                {
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
                }
            )
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against preferences; returns total score and reason strings."""
    genre = _pref(user_prefs, "genre", "favorite_genre")
    mood = _pref(user_prefs, "mood", "favorite_mood")
    target_energy = float(_pref(user_prefs, "energy", "target_energy"))
    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))

    score = 0.0
    reasons: List[str] = []

    if song["genre"] == genre:
        score += 2.0
        reasons.append("genre match (+2.0)")

    if song["mood"] == mood:
        score += 1.0
        reasons.append("mood match (+1.0)")

    energy_delta = abs(float(song["energy"]) - target_energy)
    energy_points = 1.5 * (1.0 - energy_delta)
    score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.2f})")

    if likes_acoustic and float(song["acousticness"]) >= 0.65:
        score += 0.5
        reasons.append("acoustic bonus (+0.5)")

    if mood in ("chill", "relaxed"):
        valence_delta = abs(float(song["valence"]) - 0.6)
        valence_points = 0.5 * (1.0 - valence_delta)
        score += valence_points
        reasons.append(f"valence similarity (+{valence_points:.2f})")

    return score, reasons

def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort by score descending, and return the top k with explanations."""
    scored: List[Tuple[Dict, float, List[str]]] = []
    for song in songs:
        total, reasons = score_song(user_prefs, song)
        scored.append((song, total, reasons))

    # sorted() returns a new list; .sort() would mutate scored in place — both work here.
    ranked = sorted(
        scored,
        key=lambda item: (-item[1], item[0]["id"]),
    )

    top: List[Tuple[Dict, float, str]] = []
    for song, total, reasons in ranked[:k]:
        explanation = "; ".join(reasons) if reasons else "No strong matches."
        top.append((song, total, explanation))
    return top

def _pref(user_prefs: Dict, *keys: str) -> str:
    for key in keys:
        if key in user_prefs and user_prefs[key] is not None:
            return user_prefs[key]
    raise KeyError(f"Expected one of {keys} in user preferences")

def _user_profile_to_prefs(user: UserProfile) -> Dict:
    return {
        "favorite_genre": user.favorite_genre,
        "favorite_mood": user.favorite_mood,
        "target_energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }

def _song_to_dict(song: Song) -> Dict:
    return asdict(song)
