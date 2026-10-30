# Reviewing the taxonomy: a guide for the team

SkillMatch's judgements come from four plain-text files in `data/taxonomy/`. You don't need to know any programming to review them. This guide covers the two that matter most for career-changers:

- **`role_archetypes.yaml`**: kinds of previous job (nurse, store manager, head chef…) and the competencies each one usually shows.
- **`competencies.yaml`**: the transferable competencies adverts ask for, and the advert wording that signals each one.

Each file starts with the line `# DRAFT: for team review`. Leave that line in place.

## How the files are used

1. When someone picks "Kitchen manager or head chef" on their profile, SkillMatch **suggests** the competencies listed for that archetype. The person ticks the ones that are true and can add a line of evidence.
2. When SkillMatch reads an advert, it looks for each competency's **phrases** in every requirement. "Experience managing stock levels and suppliers" contains `stock levels` and `supplier*`, so it is tagged *stock, inventory and supply*.
3. If the person ticked that competency with evidence, the requirement is **met**, and the app writes: *"Requirement: stock, inventory and supply. Your evidence: as a kitchen manager, you ran weekly stock and margin reports…"*

Get the phrases wrong and real requirements are missed, or the wrong ones are matched. Get the archetypes wrong and people aren't prompted for strengths they have.

## Reading an entry

### A competency (`competencies.yaml`)

```yaml
  - id: stock_inventory_supply
    label: stock, inventory and supply
    category: core
    description: Managing stock levels, orders and suppliers so the right things are in the right place at the right time.
    phrases: [stock control, stock levels, stock management, inventory, supply chain, demand planning, purchasing, procurement, supplier*, ordering, replenishment, wastage, materials planning]
```

| Field | What it means | Can I change it? |
|---|---|---|
| `id` | The computer's name for it | **No.** Other files refer to it. |
| `label` | What users see after "Requirement:" | Yes. Keep it lower case and short. |
| `category` | `core`, or `sector` for industry knowledge | Rarely |
| `description` | One plain sentence shown on the profile form | Yes |
| `phrases` | Advert wording that signals it | Yes: this is the main thing to review |
| `not_phrases` | Optional wording that cancels a match | Yes |

**Phrase rules:**

- Capital letters don't matter, and phrases match whole words only, so `stock` won't match "stocking".
- A `*` lets a word continue: `supplier*` matches *supplier*, *suppliers* and *supplier's*.
- `...` allows up to four words in between: `present* ... findings` matches "presenting your key findings".
- Prefer two- or three-word phrases. A single common word causes false matches. `lead` alone would match "a leading organisation", and `hospital*` once matched "hospitality".
- When a phrase keeps matching the wrong thing, add the wrong wording to `not_phrases`. Example: `not_phrases: [data warehous*]` stops "data warehousing" counting as warehouse experience.

### An archetype (`role_archetypes.yaml`)

```yaml
  - id: kitchen_manager
    label: Kitchen manager or head chef
    aliases: [head chef, sous chef, kitchen manager, chef de cuisine, catering manager, executive chef]
    competencies: [stock_inventory_supply, budget_cost_control, scheduling_rota_planning, team_leadership, regulatory_compliance, problem_solving_pressure, kpi_monitoring, training_others, sector_retail_hospitality, attention_to_detail, clear_communication, stakeholder_management, organisation_prioritising]
    example_evidence: Ran weekly stock and margin reports for a 40-cover restaurant and cut food waste by 15%.
```

| Field | What it means |
|---|---|
| `label` | What users pick from the list |
| `aliases` | Other job titles people type. A typed title like "Sous Chef" is matched to the closest archetype. |
| `competencies` | The competencies to **suggest**, most typical first. Each must be an `id` from `competencies.yaml`. |
| `example_evidence` | A realistic evidence line, written as the person would ("Ran…", "Led…", "Kept…") |

## A worked review

**Scenario:** you're reviewing *Retail store manager* and you know store managers deal with shrinkage and loss prevention, but nothing mentions it.

1. **Is there a competency for it?** Search `competencies.yaml` for "loss" or "shrink". `stock_inventory_supply` is close, and `regulatory_compliance` covers audits.
2. **Do adverts use that wording?** Looking at real adverts (see `docs/advert_patterns.md`), "stock loss", "shrinkage" and "loss prevention" appear in retail data roles. Add them to `stock_inventory_supply`:
   ```yaml
       phrases: [stock control, stock levels, …, wastage, materials planning, shrinkage, stock loss, loss prevention]
   ```
3. **Should the archetype suggest it?** `retail_store_manager` already lists `stock_inventory_supply`, so nothing to add.
4. **Is the example evidence realistic?** "Ran a store with 35 staff and £4m turnover, reviewing weekly sales, margin and shrinkage KPIs with the area manager" mentions shrinkage. Good.
5. **Check the files.** Ask whoever runs the app to run:
   ```
   uv run python -m skillmatch.taxonomy validate
   ```
   It prints `OK: …` or a list of problems in plain English, naming the file and entry. For example: *"role_archetypes.yaml, entry 'kitchen_manager': competency 'stock_control' does not exist in competencies.yaml"*.
6. **Check the effect.** Run `make test`, then `uv run python scripts/calibrate.py`, and look at whether results for the demo personas changed as you expected.

## What to look for

- **Missing strengths.** For each archetype, ask someone who did that job: "Which of these would you tick? What's missing?"
- **Phrases that over-match.** Short or common words (`calm`, `targets`, `procedures`). Check them against real adverts.
- **Phrases that under-match.** Common advert wording with no competency. The calibration report lists the most common **unclassified** requirements; each one is a candidate phrase.
- **Sector knowledge.** The `sector_*` competencies let a nurse's NHS experience count when an advert says "healthcare experience essential". Are the right sectors there for your users?
- **Labels and descriptions.** Would someone who has never worked in data understand them?

## The ten entries to review first

The calibration on live adverts (see `DECISIONS.md` and `FINAL_REPORT.md`) suggests starting here:

1. `competencies.yaml` → `analytical_thinking`: the single word "analytical" is a phrase and appears in many adverts. Check it isn't too generous.
2. `competencies.yaml` → `stakeholder_management`: the most-requested competency. Check `influenc*` and `partnering with`.
3. `competencies.yaml` → `regulatory_compliance`: broad words (`complian*`, `governance`, `regulation*`) also catch data-governance requirements.
4. `competencies.yaml` → `problem_solving_pressure`: `fast-paced` makes every "fast-paced environment" a problem-solving requirement.
5. `competencies.yaml` → `sector_manufacturing_logistics`: `production`, `transport` and `warehouse` wording; check the `not_phrases`.
6. `competencies.yaml` → `sector_public_policing`: council, police and civil-service wording, important for public-sector roles.
7. `technical_skills.yaml` → `data_analysis`: "datasets" and a broad "analysing … data" rule make it common. Is that right?
8. `technical_skills.yaml` → `dashboards_reporting`: overlaps with Power BI and Tableau; "management information" sits here.
9. `role_archetypes.yaml` → `nurse` and `care_worker`: check the suggested competencies with someone from health and care.
10. `role_archetypes.yaml` → `company_director` and `senior_manager`: leadership-level evidence meets "senior stakeholders" requirements automatically. Check the suggestions are fair.
