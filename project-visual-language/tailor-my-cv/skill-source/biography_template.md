# biography.md skeleton (agreed 27 Oct 2026)

Plain Markdown with fixed labels. Read by the user's AI. The user can skim it to check nothing was invented.

```
# Biography
updated: 2026-10-28
built_with: SkillMatch Biographer v1

## Progress
Biography: ██████░░░░ 60%
done: J2, J4, E1 | next: J1 (kitchen porter) | outside work: not started

## Profile
target: entry-level data analyst / business insight
summary: (2-3 lines in the user's words)

## Timeline
- J1 | Kitchen porter | The Swan, Lichfield | 2004-2006
- J2 | Head chef | ... | 2010-2018
- E1 | PhD, History | University of ... | 2019-2023
- O1 | Volunteer treasurer | Running club | 2020-now

## Skills
### process_improvement
- S03 | J2 | lens: fixing
  S: Food waste was high on Mondays.
  T: Cut waste without running out.
  A: Tracked covers by day for 8 weeks, changed the order pattern.
  R: Waste down about 15%. Measured before and after.
  learned: Small daily records show patterns.
  in_their_words: "Mondays we were binning half the fridge"
  also_shows: kpi_monitoring, stock_inventory_supply

### problem_solving_pressure
- X05 | J1 | lens: pressure
  example: Kept the pot wash clear through Saturday rushes, 300 covers, two porters.
  in_their_words: "you just never stopped"

## Unconfirmed
(skills the AI suggested but the user couldn't back up. Never used.)
```

- IDs: J = job, E = education, O = outside work, S = story (full STAR), X = example (one confirmed line).
- `in_their_words` is required on every story and example: the user's exact phrasing. It is a core feature, not decoration. STAR gives the bones; the quote gives the character, so tailored text doesn't read as mechanical.
- Each story sits once, under its strongest skill. `also_shows` links it to the others.
- Skill headings use ids from `skillmatch-app/data/taxonomy/competencies.yaml`.
