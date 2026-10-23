"""Fill the sentence templates in data/taxonomy/phrasing.yaml. No AI: plain string templates."""

from __future__ import annotations

import re

from skillmatch.taxonomy import Taxonomy, get_taxonomy

IRREGULAR_PAST = {
    "ran", "led", "kept", "sat", "built", "wrote", "taught", "held", "made", "set", "cut", "won",
    "drove", "oversaw", "grew", "put", "did", "chose", "gave", "took", "saw", "met", "brought",
    "bought", "sold", "spent", "found", "began", "spoke", "dealt", "paid", "read", "sent",
    "thought", "told", "understood", "went", "got", "had", "knew", "rose", "fed", "hit",
    "split", "spread", "lent", "sought", "shut", "upheld", "withheld", "overcame",
}  # fmt: skip
PRESENT_VERBS = {
    "run", "lead", "manage", "keep", "produce", "track", "plan", "report", "analyse", "analyze",
    "monitor", "train", "write", "build", "design", "deliver", "coordinate", "handle", "maintain",
    "present", "prepare", "check", "audit", "supervise", "teach", "oversee", "negotiate", "use",
    "create", "develop", "organise", "organize", "record", "review", "schedule", "support",
}  # fmt: skip
SENIORITY_WORDS = {
    "individual": "individual",
    "supervisor": "supervisor",
    "manager": "manager",
    "senior_manager": "senior manager",
    "director": "director",
}


def with_article(phrase: str) -> str:
    phrase = phrase.strip()
    if not phrase:
        return ""
    first = phrase.split()[0]
    if first.isupper() and len(first) > 1:  # acronyms: "an NHS…", "a PA"
        an = first[0] in "AEFHILMNORSX"
    else:
        an = phrase[0].lower() in "aeiou"
    return f"{'an' if an else 'a'} {phrase}"


def role_phrase(title: str) -> str:
    """'Head Chef' -> 'a head chef'; 'NHS Administrator' -> 'an NHS administrator'; keeps 'PhD'."""
    words = title.strip().split()
    out = [w if any(c.isupper() for c in w[1:]) or w.startswith("(") else w.lower() for w in words]
    return with_article(" ".join(out))


def evidence_clause(evidence: str) -> str | None:
    """'Ran weekly stock reports.' -> 'you ran weekly stock reports'. None if it isn't a verb phrase."""
    text = " ".join((evidence or "").split()).rstrip(" .;")
    if not text:
        return None
    if re.match(r"^i\s", text, re.I):
        text = text[2:]
    elif re.match(r"^i've\s", text, re.I):
        return "you've " + text[5:]
    first, _, rest = text.partition(" ")
    word = first.lower()
    if word in IRREGULAR_PAST or word in PRESENT_VERBS or (word.endswith("ed") and len(word) > 3):
        lead = first if first.isupper() and len(first) > 1 else word
        return f"you {lead} {rest}".strip()
    return None


class Phraser:
    def __init__(self, tax: Taxonomy | None = None):
        self.tax = tax or get_taxonomy()
        self.t = self.tax.phrasing

    def fill(self, section: str, key: str, **values) -> str:
        return self.t[section][key].format(**values)

    def tier_label(self, tier: str) -> str:
        return self.t["tiers"][tier]

    # Answers
    def competency(self, requirement: str, role_title: str, evidence: str) -> str:
        clause = evidence_clause(evidence)
        if clause:
            return self.fill(
                "answers",
                "competency_with_evidence",
                requirement=requirement,
                role=role_phrase(role_title),
                evidence=clause,
            )
        return self.fill(
            "answers",
            "competency_with_quote",
            requirement=requirement,
            role=role_phrase(role_title),
            quote=evidence.strip().rstrip("."),
        )

    def leadership(
        self, requirement: str, role_title: str, seniority: str, evidence: str | None
    ) -> str:
        clause = evidence_clause(evidence or "")
        sen = SENIORITY_WORDS.get(seniority, seniority)
        if clause:
            return self.fill(
                "answers",
                "leadership_with_evidence",
                requirement=requirement,
                role=role_phrase(role_title),
                seniority=sen,
                evidence=clause,
            )
        return self.fill(
            "answers",
            "leadership_without_evidence",
            requirement=requirement,
            role=role_phrase(role_title),
            seniority=sen,
        )


def years_text(n: float | None) -> str:
    if not n:
        return "no years"
    if n < 1:
        months = round(n * 12)
        return f"{months} month{'s' if months != 1 else ''}"
    n = int(n) if float(n).is_integer() else n
    return f"{n} year{'s' if n != 1 else ''}"


def join_items(items: list[str], limit: int = 4) -> str:
    items = list(dict.fromkeys(items))
    if len(items) > limit:
        return ", ".join(items[:limit]) + f" and {len(items) - limit} more"
    if len(items) > 1:
        return ", ".join(items[:-1]) + " and " + items[-1]
    return items[0] if items else ""
