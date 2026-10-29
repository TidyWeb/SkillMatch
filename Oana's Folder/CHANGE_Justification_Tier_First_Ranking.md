# Change Justification: Tier-First Vacancy Ranking

**Component:** `skillmatch/results.py`
**Change type:** Ordering behaviour (display layer only)
**Status:** Staged, pending approval

---

## 1. Summary of the Change

The vacancy ordering logic is changed from **distance-first** to **match-tier-first**, with distance retained as a secondary sort key and title as a final deterministic tie-breaker.

**Previous behaviour:**

```python
def sort_key(m: MatchResult):
    return (m.distance_miles is None, m.distance_miles or 0, m.vacancy["title"])
```

**New behaviour:**

```python
TIER_RANK = {tier: rank for rank, tier in enumerate(TIER_ORDER)}

def _sort_key(m: MatchResult):
    """Experimental ranking: match tier first, then distance, then title."""
    return (
        TIER_RANK[m.tier],
        m.distance_miles is None,
        m.distance_miles or 0,
        m.vacancy["title"],
    )
```

The change is confined to the presentation layer. The tiering logic in `match.py` and the thresholds in `config.py` are untouched.

## 2. Problem Being Addressed

Under distance-first ordering, the quality of the skill match is not a factor in result position. A consequence is that a proximate vacancy of lower relevance ("Good fit" or "Stretch") can appear above a remote or further-afield vacancy that matches the candidate's evidenced skills more closely ("Strong fit").

For an early-career tool whose primary function is to identify where a candidate's skills are genuinely competitive, ordering by proximity ahead of match quality misaligns the output with the user's objective. The defect is one of ordering, not of matching.

## 3. Justification for Tier-First Ordering

- **Alignment with user intent.** The product's stated purpose is to match skills to roles, not to rank by commute. Tier-first ordering ensures the strongest matches are surfaced first regardless of geography, which is consistent with that purpose.
- **Preservation of distance as a relevant signal.** Distance is demoted, not removed. Within any given tier, the nearest vacancies still appear first. Commute preferences continue to influence ordering, but no longer override match quality.
- **Deterministic and stable output.** Including the vacancy title as a final key guarantees a stable order when tier and distance are equal, preventing non-deterministic ordering across runs.
- **Correct handling of missing distance.** The tuple element `m.distance_miles is None` sorts known distances ahead of unknown ones within a tier, avoiding comparison errors between `None` and numeric values.
- **Low risk, bounded scope.** The change affects only the sort key applied to already-computed results. It introduces no new dependency on the matching engine and cannot alter tier assignment.

## 4. Behavioural Specification

| Case | Expected order |
|---|---|
| Different tiers, different distances | Higher tier first, regardless of distance |
| Same tier, different known distances | Nearest first |
| Same tier, one known and one unknown distance | Known distance first |
| Same tier, same distance | Alphabetical by title |

## 5. Test Coverage

A new test module, `tests/test_ranking.py`, verifies each case in the specification above:

- `test_match_tier_takes_priority_over_distance` — a 20-mile Strong fit ranks above a 2-mile Good fit.
- `test_distance_breaks_ties_within_the_same_tier` — among Strong fits, the nearer vacancy ranks first.
- `test_known_distances_rank_before_unknown_distances_within_a_tier` — known distances precede unknown within a tier.
- `test_title_breaks_ties_when_tier_and_distance_match` — alphabetical fallback is deterministic.

## 6. Risks and Mitigations

| Risk | Assessment | Mitigation |
|---|---|---|
| Users expecting nearest-first results may be surprised | Low–moderate; behaviour change is visible | Surface the sort rule in the UI ("sorted by match, then distance") |
| Tier definition drift could alter ordering | None; tier logic unchanged | No action required |
| Future tier additions not reflected in `TIER_RANK` | Low | `TIER_RANK` is derived from `TIER_ORDER`; adding a tier to the canonical list propagates automatically |

## 7. Alternatives Considered and Rejected

- **Weighted percentage score:** Rejected for this change. A single score can obscure a missed essential requirement and introduces false precision. The existing categorical tiers plus explicit reasons are more defensible and easier to explain.
- **Hybrid proximity weighting (e.g., tier × distance penalty):** Rejected as unnecessarily complex. It would make ordering harder to explain and to test without a demonstrated user need.
- **Removing distance entirely:** Rejected. Commute remains a legitimate constraint for the target cohort; demotion rather than removal preserves that signal.

## 8. Recommendation

Approve the change. It corrects a demonstrable ordering defect with bounded scope, complete test coverage, and no impact on matching logic or configuration. The accompanying tests should be merged with the patch so the ordering contract is enforced going forward.
