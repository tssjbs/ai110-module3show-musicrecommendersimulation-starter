"""Scoring strategies for VibeFinder (Strategy pattern)."""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

# Default balanced weights (Phase 3 baseline)
GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_SIMILARITY_SCALE = 1.5

MODE_ALIASES = {
    "balanced": "balanced",
    "default": "balanced",
    "genre-first": "genre_first",
    "genre_first": "genre_first",
    "mood-first": "mood_first",
    "mood_first": "mood_first",
    "energy-focused": "energy_focused",
    "energy_focused": "energy_focused",
}


def normalize_mode(mode: str) -> str:
    key = (mode or "balanced").strip().lower()
    return MODE_ALIASES.get(key, "balanced")


def _pref(user_prefs: Dict, *keys: str):
    for key in keys:
        if key in user_prefs and user_prefs[key] is not None:
            return user_prefs[key]
    raise KeyError(f"Expected one of {keys} in user preferences")


def _score_advanced_features(user_prefs: Dict, song: Dict, reasons: List[str]) -> float:
    """Bonus points for extended catalog columns (Challenge 1)."""
    bonus = 0.0

    target_detail = user_prefs.get("mood_detail")
    if target_detail and song.get("mood_detail") == target_detail:
        bonus += 1.0
        reasons.append("mood_detail match (+1.0)")

    target_decade = user_prefs.get("release_decade")
    if target_decade and song.get("release_decade") == target_decade:
        bonus += 0.5
        reasons.append("release_decade match (+0.5)")

    theme = user_prefs.get("lyrical_theme")
    if theme and song.get("lyrical_theme") == theme:
        bonus += 0.5
        reasons.append("lyrical_theme match (+0.5)")

    if user_prefs.get("prefer_instrumental") and song.get("vocal_style") == "instrumental":
        bonus += 0.5
        reasons.append("instrumental preference (+0.5)")

    if user_prefs.get("avoid_explicit") and int(song.get("is_explicit", 0)) == 1:
        bonus -= 1.0
        reasons.append("explicit content penalty (-1.0)")

    min_pop = user_prefs.get("min_popularity")
    if min_pop is not None:
        pop = int(song.get("popularity", 0))
        if pop >= int(min_pop):
            pop_pts = 0.01 * min(pop, 100)
            bonus += pop_pts
            reasons.append(f"popularity threshold (+{pop_pts:.2f})")

    return bonus


class ScoringStrategy(ABC):
    """Strategy interface: score one song for a user profile."""

    @abstractmethod
    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        pass


class _WeightedStrategy(ScoringStrategy):
    def __init__(
        self,
        genre_weight: float,
        mood_weight: float,
        energy_scale: float,
        name: str,
    ):
        self.genre_weight = genre_weight
        self.mood_weight = mood_weight
        self.energy_scale = energy_scale
        self.name = name

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        genre = _pref(user_prefs, "genre", "favorite_genre")
        mood = _pref(user_prefs, "mood", "favorite_mood")
        target_energy = float(_pref(user_prefs, "energy", "target_energy"))
        likes_acoustic = bool(user_prefs.get("likes_acoustic", False))

        score = 0.0
        reasons: List[str] = [f"mode={self.name}"]

        if song["genre"] == genre:
            score += self.genre_weight
            reasons.append(f"genre match (+{self.genre_weight:.1f})")

        if song["mood"] == mood:
            score += self.mood_weight
            reasons.append(f"mood match (+{self.mood_weight:.1f})")

        energy_delta = abs(float(song["energy"]) - target_energy)
        energy_points = self.energy_scale * (1.0 - energy_delta)
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

        score += _score_advanced_features(user_prefs, song, reasons)
        return score, reasons


class BalancedScoringStrategy(_WeightedStrategy):
    def __init__(self) -> None:
        super().__init__(GENRE_MATCH_POINTS, MOOD_MATCH_POINTS, ENERGY_SIMILARITY_SCALE, "balanced")


class GenreFirstScoringStrategy(_WeightedStrategy):
    def __init__(self) -> None:
        super().__init__(3.0, 0.75, 1.0, "genre_first")


class MoodFirstScoringStrategy(_WeightedStrategy):
    def __init__(self) -> None:
        super().__init__(1.0, 2.5, 1.25, "mood_first")


class EnergyFocusedScoringStrategy(_WeightedStrategy):
    def __init__(self) -> None:
        super().__init__(1.0, 1.0, 3.0, "energy_focused")


def get_scoring_strategy(mode: str) -> ScoringStrategy:
    normalized = normalize_mode(mode)
    strategies = {
        "balanced": BalancedScoringStrategy,
        "genre_first": GenreFirstScoringStrategy,
        "mood_first": MoodFirstScoringStrategy,
        "energy_focused": EnergyFocusedScoringStrategy,
    }
    return strategies[normalized]()
