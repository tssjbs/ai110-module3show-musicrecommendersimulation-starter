"""Terminal formatting helpers (Challenge 4)."""

from typing import Dict, List, Tuple

from tabulate import tabulate


def format_recommendations_table(
    recommendations: List[Tuple[Dict, float, str]],
) -> str:
    """Render top-k recommendations as a table including score reasons."""
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append(
            [
                rank,
                song["title"],
                song["artist"],
                song["genre"],
                f"{score:.2f}",
                explanation,
            ]
        )
    headers = ["#", "Title", "Artist", "Genre", "Score", "Reasons"]
    return tabulate(rows, headers=headers, tablefmt="simple")
