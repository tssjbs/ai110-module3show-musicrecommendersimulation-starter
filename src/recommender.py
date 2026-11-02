import csv
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from dataclasses import dataclass, asdict

from src.scoring_strategies import get_scoring_strategy, normalize_mode

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
    popularity: int = 50
    release_decade: str = "2010s"
    mood_detail: str = "neutral"
    lyrical_theme: str = "general"
    is_explicit: int = 0
    vocal_style: str = "mixed"

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
    def __init__(self, songs: List[Song], scoring_mode: str = "balanced"):
        self.songs = songs
        self.scoring_mode = scoring_mode

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for the given user profile."""
        prefs = _user_profile_to_prefs(user)
        song_dicts = [_song_to_dict(s) for s in self.songs]
        ranked = recommend_songs(
            prefs,
            song_dicts,
            k=k,
            scoring_mode=self.scoring_mode,
            apply_diversity=False,
        )
        id_order = [item[0]["id"] for item in ranked]
        by_id = {s.id: s for s in self.songs}
        return [by_id[sid] for sid in id_order]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Build a human-readable explanation for why a song fits the profile."""
        prefs = _user_profile_to_prefs(user)
        _, reasons = score_song(prefs, _song_to_dict(song), scoring_mode=self.scoring_mode)
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
                    "popularity": int(row.get("popularity", 50)),
                    "release_decade": row.get("release_decade", "2010s"),
                    "mood_detail": row.get("mood_detail", "neutral"),
                    "lyrical_theme": row.get("lyrical_theme", "general"),
                    "is_explicit": int(row.get("is_explicit", 0)),
                    "vocal_style": row.get("vocal_style", "mixed"),
                }
            )
    return songs

def score_song(
    user_prefs: Dict,
    song: Dict,
    scoring_mode: str = "balanced",
) -> Tuple[float, List[str]]:
    """Score one song against preferences; returns total score and reason strings."""
    strategy = get_scoring_strategy(scoring_mode)
    return strategy.score(user_prefs, song)

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    scoring_mode: str = "balanced",
    apply_diversity: bool = True,
    artist_penalty: float = 1.0,
    genre_penalty: float = 0.5,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, rank with optional diversity penalties, return top k."""
    mode = normalize_mode(scoring_mode)
    scored: List[Tuple[Dict, float, List[str]]] = []
    for song in songs:
        total, reasons = score_song(user_prefs, song, scoring_mode=mode)
        scored.append((song, total, reasons))

    if not apply_diversity or k <= 0:
        ranked = sorted(scored, key=lambda item: (-item[1], item[0]["id"]))
        return _pack_top_k(ranked, k)

    return _recommend_with_diversity(
        scored,
        k,
        artist_penalty=artist_penalty,
        genre_penalty=genre_penalty,
    )

def _recommend_with_diversity(
    scored: List[Tuple[Dict, float, List[str]]],
    k: int,
    artist_penalty: float,
    genre_penalty: float,
) -> List[Tuple[Dict, float, str]]:
    """Greedy top-k: penalize artists/genres already chosen (Challenge 3)."""
    remaining = list(scored)
    chosen: List[Tuple[Dict, float, List[str]]] = []
    used_artists: set = set()
    used_genres: set = set()

    while remaining and len(chosen) < k:
        best_idx = -1
        best_effective = float("-inf")
        best_adjusted_reasons: List[str] = []

        for idx, (song, base_score, reasons) in enumerate(remaining):
            effective = base_score
            extra: List[str] = []
            if song["artist"] in used_artists:
                effective -= artist_penalty
                extra.append(f"diversity: duplicate artist (-{artist_penalty:.1f})")
            if song["genre"] in used_genres:
                effective -= genre_penalty
                extra.append(f"diversity: duplicate genre (-{genre_penalty:.1f})")

            if effective > best_effective or (
                effective == best_effective
                and (best_idx < 0 or song["id"] < remaining[best_idx][0]["id"])
            ):
                best_effective = effective
                best_idx = idx
                best_adjusted_reasons = reasons + extra

        song, base_score, _ = remaining.pop(best_idx)
        chosen.append((song, best_effective, best_adjusted_reasons))
        used_artists.add(song["artist"])
        used_genres.add(song["genre"])

    return _pack_top_k(chosen, k)

def _pack_top_k(
    ranked: List[Tuple[Dict, float, List[str]]],
    k: int,
) -> List[Tuple[Dict, float, str]]:
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
