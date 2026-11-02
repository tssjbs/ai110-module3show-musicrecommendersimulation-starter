# AI Interactions Log

> Stretch features for VibeFinder optional extensions.

---

## Agentic Workflow (SF8)

**What task did you give the agent?**

Implement all four optional challenges in one pass: extend `songs.csv` with five new attributes, wire them into scoring, add Strategy-based scoring modes, greedy diversity penalties for duplicate artists/genres, and tabulated CLI output with reasons.

**Prompts used:**

1. *"Add popularity (0–100), release_decade, mood_detail, lyrical_theme, is_explicit, and vocal_style to songs.csv; update load_songs and scoring to use mood_detail, decade, theme, instrumental preference, explicit penalty, and min_popularity."*

2. *"Refactor scoring into a Strategy pattern with balanced, genre-first, mood-first, and energy-focused modes; select mode from main.py or VIBEFINDER_MODE env var."*

3. *"When building top-k, apply a diversity penalty if the artist or genre is already in the result list; document the rule."*

4. *"Use tabulate to print a table with rank, title, artist, genre, score, and the full reasons string."*

**What did the agent generate or change?**

- `data/songs.csv` — six new columns on all 18 rows  
- `src/scoring_strategies.py` — `ScoringStrategy` ABC and four concrete strategies  
- `src/recommender.py` — extended loader, diversity-aware `recommend_songs`, optional `apply_diversity`  
- `src/display.py` — `format_recommendations_table()`  
- `src/main.py` — mode env vars, extended profile prefs, table output  
- `requirements.txt` — added `tabulate`

**What did you verify or fix manually?**

- Ran `pytest` — starter tests still pass (`apply_diversity=False` on `Recommender.recommend`).  
- Ran `python -m src.main` — Chill Lofi diversity swaps second *LoRoom* track for a different artist when penalties apply.  
- Checked CSV integers parse as `int`/`float` and missing optional keys in old rows would default (handled in loader).  
- Fixed greedy tie-break when `best_idx` is still `-1` on the first pick.

---

## Design Pattern (SF10)

**Which design pattern did you use?**

**Strategy** — interchangeable scoring algorithms selected at runtime.

**How did AI help you brainstorm or implement it?**

The assistant suggested keeping Phase 3 weights in a `BalancedScoringStrategy` and cloning the same loop with different constants for genre-first / mood-first / energy-focused instead of copying four full functions. That kept `recommend_songs()` and diversity logic in one place while only the “how to score one song” step varies.

**How does the pattern appear in your final code?**

- `src/scoring_strategies.py`: abstract `ScoringStrategy.score()`, concrete classes, and `get_scoring_strategy(mode)`.  
- `src/recommender.py`: `score_song(..., scoring_mode=...)` delegates to `get_scoring_strategy(mode).score(...)`.  
- `src/main.py`: `SCORING_MODE` / `VIBEFINDER_MODE` picks the strategy for CLI runs.

**Branch note (Challenge 2):** You can prototype a new mode on `git checkout -b experiment/mood-first`, tweak weights in `MoodFirstScoringStrategy`, and merge when satisfied—`main` stays on `balanced` by default.
