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

This simulation uses **content-based filtering**: each song is scored from its attributes, then the highest-scoring songs are recommended. It does not use other users’ listening history (no collaborative filtering).

### Song features (`Song` / `data/songs.csv`)

Each row in the catalog (18 songs after expansion) includes:

| Feature | Role |
|---------|------|
| `genre` | Category label (pop, lofi, rock, hip-hop, classical, …) |
| `mood` | Subjective vibe (chill, intense, happy, relaxed, …) |
| `energy` | 0.0–1.0 intensity |
| `tempo_bpm` | Beats per minute (reserved for future weighting) |
| `valence` | 0.0–1.0 emotional positivity |
| `danceability` | 0.0–1.0 how suitable for dancing |
| `acousticness` | 0.0–1.0 acoustic vs electronic production |

### User profile (`UserProfile`)

Example taste profile for testing (**“Maya — late-night focus listener”**):

```python
UserProfile(
    favorite_genre="lofi",
    favorite_mood="chill",
    target_energy=0.38,
    likes_acoustic=True,
)
```

**Why this profile works:** It separates **chill lofi** (e.g. *Midnight Coding*, *Library Rain*) from **intense rock/metal** (*Storm Runner*, *Iron Horizon*): genre and mood mismatches cost points, and high-energy tracks score poorly when `target_energy` is low. It is **not** too narrow for a demo—still allows cross-genre mood matches (e.g. ambient *Spacewalk Thoughts*) if energy and mood align.

A **narrow** profile (e.g. `pop` + `happy` + energy 0.9) would mostly surface pop workout tracks and ignore great mood matches in other genres.

### Algorithm recipe (scoring rule — one song)

For each song, start at **0** and add:

| Rule | Points |
|------|--------|
| Genre equals `favorite_genre` | **+2.0** |
| Mood equals `favorite_mood` | **+1.0** |
| Energy similarity | **+1.5 × (1 − \|song.energy − target_energy\|)** (closer = more points, max 1.5) |
| Acoustic bonus (if `likes_acoustic` and `song.acousticness ≥ 0.65`) | **+0.5** |
| Valence similarity (optional stretch) | **+0.5 × (1 − \|song.valence − 0.6\|)** when mood is chill/relaxed |

**Ranking rule (list of songs):** Compute the score for **every** song in the CSV, sort by score **descending**, return the top **k** (default 5). Ties break by lower `id` for stability.

### Data flow (planning sketch)

```
Input: UserProfile (genre, mood, target_energy, likes_acoustic)
   ↓
Process: For each song in songs.csv → apply scoring recipe → (score, reasons)
   ↓
Output: Sort all scores → Top K recommendations + short explanation per song
```

### Expected bias / limitations (design note)

- **Genre overweight:** A +2.0 genre match can hide a better mood/energy fit in another genre (“filter bubble” by genre).
- **Small catalog:** 18 songs cannot represent real-world diversity; one genre may dominate top‑k.
- **No lyrics, language, or popularity:** Two songs with similar tags but different quality rank the same.
- **Static profile:** Real apps update taste from skips and replays; this profile is fixed per run.

Implementation of this recipe lives in `score_song()` and `Recommender.recommend()` in Phase 3.

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

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
Loaded songs: 18

User profile: genre=pop, mood=happy, energy=0.8

Top recommendations:

1. Sunrise City — Neon Echo
   Score: 4.47
   Because: genre match (+2.0); mood match (+1.0); energy similarity (+1.47)

2. Gym Hero — Max Pulse
   Score: 3.30
   Because: genre match (+2.0); energy similarity (+1.30)

3. Rooftop Lights — Indigo Parade
   Score: 2.44
   Because: mood match (+1.0); energy similarity (+1.44)

4. Island Morning — Kingston Tide
   Score: 2.26
   Because: mood match (+1.0); energy similarity (+1.26)

5. Night Drive Loop — Neon Echo
   Score: 1.42
   Because: energy similarity (+1.42)
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

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



