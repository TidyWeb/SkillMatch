"""Tests for the experimental match-tier-first vacancy ranking."""

from types import SimpleNamespace

from skillmatch.results import _sort_key


def vacancy(tier, distance, title):
    """Build the small part of a match result that the sort key needs."""
    return SimpleNamespace(
        tier=tier,
        distance_miles=distance,
        vacancy={"title": title},
    )


def test_match_tier_takes_priority_over_distance():
    # A more distant Strong fit should rank above a nearby Good fit.
    matches = [
        vacancy("good", 2, "Nearby role"),
        vacancy("strong", 20, "Further role"),
    ]

    ordered = sorted(matches, key=_sort_key)

    assert [m.vacancy["title"] for m in ordered] == [
        "Further role",
        "Nearby role",
    ]


def test_distance_breaks_ties_within_the_same_tier():
    matches = [
        vacancy("strong", 12, "Further role"),
        vacancy("strong", 3, "Nearby role"),
    ]

    ordered = sorted(matches, key=_sort_key)

    assert [m.vacancy["title"] for m in ordered] == [
        "Nearby role",
        "Further role",
    ]


def test_known_distances_rank_before_unknown_distances_within_a_tier():
    matches = [
        vacancy("good", None, "Unknown distance"),
        vacancy("good", 5, "Known distance"),
    ]

    ordered = sorted(matches, key=_sort_key)

    assert [m.vacancy["title"] for m in ordered] == [
        "Known distance",
        "Unknown distance",
    ]


def test_title_breaks_ties_when_tier_and_distance_match():
    matches = [
        vacancy("strong", 5, "Zebra role"),
        vacancy("strong", 5, "Analyst role"),
    ]

    ordered = sorted(matches, key=_sort_key)

    assert [m.vacancy["title"] for m in ordered] == [
        "Analyst role",
        "Zebra role",
    ]
