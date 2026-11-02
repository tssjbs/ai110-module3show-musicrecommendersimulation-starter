# 🎵 Music Recommender Simulation

## Project Summary

**VibeFinder 1.0** loads 18 tagged songs from CSV, scores each row against a taste profile (genre, mood, energy, acoustic preference, and optional stretch fields), and prints a ranked top-5 with plain-English reasons in the terminal. It is a content-based simulation for learning—not a production recommender. Full documentation lives in the [**Model Card**](model_card.md).

---

## How Real-World Music Recommenders Work

Apps like **Spotify**, **YouTube Music**, and **Apple Music** combine **song data**, **user data**, and a **ranking step** to decide what to show next.

**Input data (about each track)**  
Platforms store features such as **genre**, **mood/valence**, **tempo (BPM)**, **energy**, **popularity**, and sometimes audio embeddings from machine learning. These describe the song itself, not the listener.

**User preferences (about the listener)**  
The system builds a taste profile from **explicit choices** (likes, saves, genre picks) and **implicit history** (skips, replays, time of day, device). Collaborative filtering also uses patterns from *other* users with similar behavior (“people like you also played …”).

**Ranking / selection**  
Candidate songs are **scored or ranked**, then the app shows the top items (often mixing in exploration and diversity rules). The user never sees raw numbers—only the ordered playlist.

**How VibeFinder maps to this**  
Our simulation uses only **content-based** ranking: we match your stated genre, mood, and energy to each CSV row. We do **not** use listening history or other users (no collaborative filtering). That keeps the loop visible: **preferences → score every song → sort → explain top-k**.

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
| `popularity`, `release_decade`, `mood_detail`, … | Stretch attributes (see model card) |

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

### Optional extensions

- **Advanced CSV columns:** popularity, release_decade, mood_detail, lyrical_theme, is_explicit, vocal_style (see scoring bonuses in `src/scoring_strategies.py`).
- **Scoring modes:** `VIBEFINDER_MODE=genre-first` | `mood-first` | `energy-focused` | `balanced` (default).
- **Diversity:** `VIBEFINDER_DIVERSITY=0` to disable artist/genre penalties in top-k.
- **Compare modes:** `VIBEFINDER_DEMO_MODES=1 python -m src.main` (Chill Lofi profile, all modes).
- **Stretch log:** [`ai_interactions.md`](ai_interactions.md).

---

## Sample Recommendation Output

Run: `python -m src.main` (table includes scores and reasons).

### Example explanations (tied to `score_song`)

1. **Sunrise City** for *High-Energy Pop*: `genre match (+2.0); mood match (+1.0); energy similarity (+1.46)` — only track with both **pop** and **happy**, plus energy near 0.85.  
2. **Library Rain** for *Chill Lofi*: genre + mood + energy + `acoustic bonus (+0.5)` + `mood_detail match (+1.0)` — matches low-energy, nostalgic, instrumental-friendly tags.  
3. **Storm Runner** for *Deep Intense Rock*: `genre match (+2.0); mood match (+1.0); energy similarity (+1.48)` — the sole **rock** row that also matches **intense** and high target energy.

### Three user profiles (top 3 each)

**High-Energy Pop** (`genre=pop`, `mood=happy`, `energy=0.85`)

```
1. Sunrise City — Score 6.74 — genre match (+2.0); mood match (+1.0); energy similarity (+1.46); …
2. Rooftop Lights — Score 4.53 — mood match (+1.0); energy similarity (+1.36); …
3. Gym Hero — Score 4.23 — genre match (+2.0); energy similarity (+1.38); diversity: duplicate genre (-0.5)
```

**Chill Lofi** (`genre=lofi`, `mood=chill`, `energy=0.38`, acoustic + nostalgic)

```
1. Library Rain — Score 7.46 — genre + mood + energy + acoustic bonus + mood_detail match
2. Midnight Coding — Score 6.92 — same pattern; diversity: duplicate genre (-0.5)
3. Spacewalk Thoughts — Score 4.33 — mood/energy/acoustic fit without lofi genre tag
```

**Deep Intense Rock** (`genre=rock`, `mood=intense`, `energy=0.92`)

```
1. Storm Runner — Score 4.48 — genre + mood + energy + mood_detail match
2. Gym Hero — Score 3.48 — mood + energy (pop, not rock)
3. Block Cipher — Score 2.44 — intense hip-hop; mood match without genre match
```

**What differs between profiles:** Pop vs lofi vs rock profiles pull from different CSV corners—high energy (~0.8+) vs low (~0.38) vs intense (~0.9). The **EDM/electronic** listener would see *Afterhours Pulse* rise under `energy-focused` mode; the **acoustic low-energy** listener sees lofi/jazz/ambient rows; an **intense** profile surfaces *Gym Hero* and *Block Cipher* even when genre does not match, because mood and energy still add points.

---

## Experiments You Tried

Phase 4 **weight shift**: halved genre points (2.0 → 1.0) and doubled energy scale (1.5 → 3.0). Top-5 **order** stayed similar for pop and rock profiles, but high-energy non-matches (e.g. funk/electronic) moved up—recommendations became more “energy-first,” not necessarily better for genre purists. Full stress-test outputs and profile comparisons are in [**model_card.md → Evaluation**](model_card.md).

---

## Limitations and Risks

- Tiny catalog (18 songs); genre match often means one fixed track.
- No lyrics, language, popularity, or listening history.
- Genre weight (+2) can overpower mood when user tags conflict.
- See [**model_card.md §6**](model_card.md) for bias notes from stress tests.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Recommenders turn **labeled data plus rules** into a ordered list—they do not have to be neural nets to feel “smart.” VibeFinder showed me that every weight is a product choice: rewarding genre without punishing wrong mood created a filter bubble in edge-case profiles. Bias showed up as *Gym Hero* and other intense tracks surfacing whenever energy and one tag aligned, even when the mood tag said something else.

Using AI coding help was fastest for boilerplate and formatting, but **profiles and weights had to be validated by running** `python -m src.main` and reading the reasons line. The full reflection (learning moment, surprises, next steps) is in [**model_card.md §10**](model_card.md).



