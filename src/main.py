"""
Command line runner for the Music Recommender Simulation.

Optional extensions: scoring modes, diversity penalty, tabulated output.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

from src.display import format_recommendations_table
from src.recommender import load_songs, recommend_songs

# Challenge 2: switch mode via env or edit here — balanced | genre-first | mood-first | energy-focused
SCORING_MODE = os.environ.get("VIBEFINDER_MODE", "balanced")
APPLY_DIVERSITY = os.environ.get("VIBEFINDER_DIVERSITY", "1") != "0"
DEMO_ALL_MODES = os.environ.get("VIBEFINDER_DEMO_MODES", "0") == "1"

SCORING_MODES = ["balanced", "genre-first", "mood-first", "energy-focused"]

PROFILES: List[Dict[str, Any]] = [
    {
        "label": "High-Energy Pop",
        "prefs": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.85,
            "likes_acoustic": False,
            "mood_detail": "euphoric",
            "release_decade": "2010s",
            "min_popularity": 60,
        },
    },
    {
        "label": "Chill Lofi",
        "prefs": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.38,
            "likes_acoustic": True,
            "mood_detail": "nostalgic",
            "prefer_instrumental": True,
            "release_decade": "2020s",
        },
    },
    {
        "label": "Deep Intense Rock",
        "prefs": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.92,
            "likes_acoustic": False,
            "mood_detail": "aggressive",
            "avoid_explicit": True,
        },
    },
]


def print_recommendations(
    label: str,
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    scoring_mode: str = SCORING_MODE,
    apply_diversity: bool = APPLY_DIVERSITY,
) -> None:
    p = user_prefs
    print(f"=== {label} ===")
    print(
        f"Profile: genre={p['genre']}, mood={p['mood']}, energy={p['energy']}, "
        f"mode={scoring_mode}, diversity={'on' if apply_diversity else 'off'}\n"
    )
    recommendations = recommend_songs(
        user_prefs,
        songs,
        k=k,
        scoring_mode=scoring_mode,
        apply_diversity=apply_diversity,
    )
    print(format_recommendations_table(recommendations))
    print()


def main() -> None:
    csv_path = Path(__file__).resolve().parent.parent / "data" / "songs.csv"
    songs = load_songs(str(csv_path))
    print(f"Loaded songs: {len(songs)}\n")

    if DEMO_ALL_MODES:
        demo = PROFILES[1]
        for mode in SCORING_MODES:
            print_recommendations(
                f"{demo['label']} [{mode}]",
                demo["prefs"],
                songs,
                scoring_mode=mode,
            )
        return

    for entry in PROFILES:
        print_recommendations(entry["label"], entry["prefs"], songs, scoring_mode=SCORING_MODE)


if __name__ == "__main__":
    main()
