# 🎧 Model Card: VibeFinder 1.0

A short document explaining what this music recommender does, how it was tested, and where it falls short.

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder **suggests up to five songs** from a small catalog. It does not predict chart success or play counts. It picks songs that **match tags and numbers** the user gives: favorite genre, mood, target energy, and whether they like acoustic tracks.

---

## 3. Intended Use and Non-Intended Use

**Intended use**

- Learning how content-based recommenders work in a **classroom or demo** setting.
- Comparing taste profiles in the terminal and reading **why** each song scored well.

**Non-intended use**

- Do **not** use this as a real streaming product. The catalog is 18 songs.
- Do **not** treat results as fair or complete for any culture, language, or artist community—the labels are hand-made and uneven.
- Do **not** assume songs are ranked by quality or popularity. Only rule matches matter.

---

## 4. Data Used

- **Size:** 18 songs in `data/songs.csv` (meets 15–20 requirement).
- **Core features:** genre, mood, energy (0–1), tempo_bpm, valence, danceability, acousticness.
- **Stretch features:** popularity (0–100), release_decade, mood_detail (e.g. euphoric, nostalgic), lyrical_theme, is_explicit, vocal_style.
- **Limits:** One rock track, two pop tracks, no lyrics text, no real listener history. Genre imbalance means “rock radio” often becomes “intense mood + high energy” from other genres.

---

## 5. Algorithm Summary

This is **not machine learning**. It is a **points game**:

1. Start each song at 0.
2. Add **+2** if genre matches the user.
3. Add **+1** if mood matches.
4. Add up to **+1.5** for how close the song’s energy is to the user’s target energy.
5. Optional: **+0.5** acoustic bonus; extra valence points for chill/relaxed moods.
6. Stretch: bonuses for mood_detail, release_decade, lyrical_theme, instrumental preference, popularity threshold; penalty for explicit content when `avoid_explicit` is set.
7. Sort by score; build top **k** with optional **diversity penalties** (see below).

Every song gets an energy score even when genre and mood fail—that is important for bias (see below).

**Modes (stretch):** `balanced`, `genre-first`, `mood-first`, `energy-focused` via Strategy classes in `src/scoring_strategies.py` and `VIBEFINDER_MODE` in the CLI.

---

## 6. Observed Behavior / Biases

- **Genre filter bubble:** Wrong mood is never punished. “Pop + sad + high energy” still recommends upbeat *Gym Hero* because pop (+2) and energy beat a missing melancholy match.
- ***Gym Hero* effect:** One pop/intense/high-energy track shows up on many lists. It feels like a recommender “favorite” even though the code has no memory—just strong tags.
- **Rock fans see “intense” more than “rock”:** With only one rock row, second place is often other intense genres (hip-hop, metal, pop).
- **Weight experiment:** Halving genre weight and doubling energy made lists more “workout energy” and less genre-loyal. Same order at the top for pop, but funk/electronic crept into slots.

### Diversity and fairness (stretch)

Without diversity, **Neon Echo** and **LoRoom** could occupy multiple top slots because they have several catalog rows. The greedy **artist penalty (−1.0)** and **genre penalty (−0.5)** push the list toward different artists/genres after the first pick. That reduces repetition and mild “filter bubbles” where one label dominates the playlist. It does not fix cultural bias in the tags themselves—it only spreads results within our tiny CSV.

---

## 7. Evaluation Process

**How we tested**

- Six profiles in `src/main.py`: three normal (High-Energy Pop, Chill Lofi, Deep Intense Rock) and three edge cases (conflicting mood/energy, impossible lofi energy, acoustic + metal).
- Compared top-5 lists and checked if they **felt** right for each persona.
- Ran a **weight shift** (genre 2→1, energy scale 1.5→3), noted changes, restored baseline for tests.
- Used `pytest` on the `Recommender` class (pop/happy profile should rank pop first).

**What we looked for**

- Do chill and intense profiles separate by energy?
- Do adversarial profiles expose bad behavior?
- Do “Because:” reasons match the math in `score_song`?

**Pair comparisons (short)**

| Profiles | What changed | Why it makes sense |
|----------|--------------|-------------------|
| High-Energy Pop vs Chill Lofi | No overlap in top-3 | Genre + mood tags point at different corners of the CSV. |
| Chill Lofi vs Deep Intense Rock | Energy ~0.4 vs ~0.9 | Energy similarity rewards different rows even when moods differ. |
| Deep Intense Rock vs sad pop edge case | *Storm Runner* vs *Gym Hero* #1 | Full rock match beats pop without mood match. |

### Full stress-test log (baseline)

```
Loaded songs: 18

=== High-Energy Pop ===
Profile: genre=pop, mood=happy, energy=0.85, likes_acoustic=False

1. Sunrise City — Neon Echo
   Score: 4.46
   Because: genre match (+2.0); mood match (+1.0); energy similarity (+1.46)
2. Gym Hero — Max Pulse
   Score: 3.38
   Because: genre match (+2.0); energy similarity (+1.38)
3. Rooftop Lights — Indigo Parade
   Score: 2.37
   Because: mood match (+1.0); energy similarity (+1.36)
4. Island Morning — Kingston Tide
   Score: 2.19
   Because: mood match (+1.0); energy similarity (+1.19)
5. Neon Pocket — Funk Atlas
   Score: 1.48
   Because: energy similarity (+1.48)

=== Chill Lofi ===
Profile: genre=lofi, mood=chill, energy=0.38, likes_acoustic=True

1. Library Rain — Paper Lanterns
   Score: 5.46
2. Midnight Coding — LoRoom
   Score: 5.42
3. Focus Flow — LoRoom
   Score: 4.46
4. Spacewalk Thoughts — Orbit Bloom
   Score: 3.33
5. Coffee Shop Stories — Slow Stereo
   Score: 2.43

=== Deep Intense Rock ===
Profile: genre=rock, mood=intense, energy=0.92, likes_acoustic=False

1. Storm Runner — Voltline
   Score: 4.48
2. Gym Hero — Max Pulse
   Score: 2.48
3. Block Cipher — Cipher K
   Score: 2.44
4. Iron Horizon — Black Anvil
   Score: 2.42
5. Afterhours Pulse — Club Meridian
   Score: 1.46

=== Edge: High energy + sad mood (conflict) ===
1. Gym Hero — Max Pulse (3.46)
2. Sunrise City — Neon Echo (3.38)
3. Old Pines — Willow & Ash (1.87)

=== Edge: Lofi genre but wants max energy ===
1. Midnight Coding — LoRoom (4.69)
2. Library Rain — Paper Lanterns (4.60)
3. Focus Flow — LoRoom (3.67)

=== Edge: Acoustic lover in metal genre ===
1. Iron Horizon — Black Anvil (4.39)
2. Storm Runner — Voltline (2.48)
3. Block Cipher — Cipher K (2.47)
```

*(Chill Lofi and other blocks above omit repeated “Because” lines in this summary copy; run `python -m src.main` for full reasons.)*

---

## 8. Strengths

- Clear **CLI output** with scores and reasons.
- **Chill Lofi** and **High-Energy Pop** lists matched expectations when tags aligned.
- Easy to **debug**: change a weight, re-run, see the list move.

---

## 9. Ideas for Improvement

1. **Subtract points** for wrong mood or genre, not only add for matches.
2. **Tune diversity penalties** by user (some want deep dives on one artist).
3. **Bigger, balanced catalog** and Streamlit UI for sliders and live re-ranking.

---

## 10. Personal Reflection

**Biggest learning moment:** Seeing the **adversarial profile** (“pop + melancholy + high energy”) recommend *Gym Hero* clicked for me. The code was doing exactly what we wrote—reward genre and energy—but the result felt wrong emotionally. That is when I understood that **fairness and “feels right” depend on the rules**, not on the word “AI.”

**AI tools:** They sped up boring parts (CSV loading, sorting, formatting the CLI) and helped phrase the scoring recipe. I still had to **run the profiles myself**, check that *Sunrise City* beat *Gym Hero* for happy pop, and revert the weight experiment so tests passed. The assistant does not replace reading the terminal output.

**Why simple rules still feel like recommendations:** A ranked top-5 with “Because: genre match (+2.0)” mimics Spotify’s explainable moments. Your brain fills in intent even though there is no neural network—just addition.

**What I would try next:** Mood **penalties**, a larger CSV with balanced genres, and a small web form so friends could pick moods and compare lists without editing Python.
