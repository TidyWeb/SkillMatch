# SkillMatch Prototype: State Assessment and Readiness Review

**Scope:** An objective evaluation of the `prototype/app` codebase against the standard of a fully developed, production-ready application.
**Components reviewed:** README, architecture, `wsgi.py`, `app.js`, `match.py`, `config.py`, taxonomy, and test suite.
**Date of review:** October 2026

---

## 1. Executive Summary

SkillMatch is functionally coherent and demonstrates deliberate engineering choices in several areas: stateless session handling, a test suite with meaningful coverage, centralised configuration, and a rule-based matching model that prioritises explainability over scoring.

However, measured against a fully developed application, the prototype sits at an **early-to-mid maturity stage**. It is well-structured but not complete. The gaps are less about code correctness and more about operational robustness, maintainability of rule-based logic at scale, and unresolved product decisions. This review separates what is demonstrably sound from what remains open.

---

## 2. Assessment Against a Mature Application Standard

| Dimension | Mature Application Expectation | Current Prototype State | Verdict |
|---|---|---|---|
| **Configuration** | Centralised, environment-aware, no hard-coded secrets | `config.py` centralises thresholds and paths; `.env` used correctly | Meets standard |
| **Session & Privacy** | Server-side session or signed tokens; no PII leakage | Profile held in `sessionStorage` only; nothing persisted server-side | Meets standard (design choice) |
| **Testing** | Unit + integration + regression coverage of core logic | ~22 test modules including match cases, ETL, filters, routes | Meets standard for prototype; integration depth unverified |
| **Matching Explainability** | Every result traceable to a reason | Returns `top_answers`, `gap_advice`, `reasons` | Meets standard |
| **Rule Maintenance** | Rules externalised and reviewable by non-engineers | YAML taxonomy separated from Python logic | Meets standard |
| **Data Pipeline** | Scheduled, monitored, idempotent ETL with failure alerts | Nightly GitHub Action → Cloud Run; monitoring/alerting not evidenced | Partially meets |
| **Deployment** | Reproducible, containerised, rollback-capable | Dockerfile, Cloud Run, Workload Identity Federation | Meets standard |
| **Error Handling** | Graceful degradation and observable failures | Fallback to fixtures exists; logging/observability not evidenced | Partially meets |
| **Accessibility & UX** | Documented WCAG posture, responsive design | Phone-width screenshot referenced; no accessibility audit evidenced | Unverified |
| **Documentation** | Architecture, decisions, changelog, runbook | `DECISIONS.md`, `CHANGELOG.md`, `docs/` present and substantive | Meets standard |

---

## 3. Strengths (Factual, Not Evaluative)

- **Stateless request model.** The profile is transmitted per-request from browser `sessionStorage`; the server holds no user state. This removes a class of privacy and scaling concerns that a mature application would otherwise need to address.
- **Rule-based matching with explicit outputs.** The algorithm returns categorical tiers (`Strong`, `Good`, `Stretch`, `Not yet`) and justification strings. It deliberately avoids percentage scores, which prevents false precision.
- **Centralised tunables.** All thresholds (`STRONG_MAX_PARTLY`, `STRETCH_MIN_GAPS`, etc.) reside in `config.py`, making behaviour auditable and adjustable without touching logic.
- **Contextual rule handling.** The code distinguishes disjunctive requirements (`or`), hands-on experience phrasing, interest-only statements, and leadership competencies mapped from prior roles. This is a level of linguistic nuance beyond naive keyword matching.
- **Substantive test surface.** Test modules target specific failure modes (missing text, duplicate missingness, outcome retention, Reed budget), indicating edge-case awareness rather than happy-path-only testing.

---

## 4. Gaps and Risks

### 4.1 Rule-Based Logic Does Not Scale Without Governance

The regex patterns (`HANDS_ON`, `LEADERSHIP_REQ`, `DISJUNCTIVE`) are effective but brittle. A mature application would either (a) maintain an explicit, versioned rule catalogue with regression fixtures per rule, or (b) migrate to a probabilistic extraction layer (e.g., spaCy) with human-in-the-loop review. Currently, adding a rule requires engineering involvement and carries unquantified regression risk.

### 4.2 Observability and Failure Handling Are Not Evidenced

The nightly ETL and Cloud Run deployment are automated, but there is no visible evidence of structured logging, metrics, alerting, or runbook procedures for pipeline failure. A mature application would surface ETL failures, request errors, and match-anomaly rates to operators.

### 4.3 The "Small Gap" Penalty Is Undocumented in Effect

`data_gate` returns `"small"` when a candidate is one year short and the advert lacks entry signals; this increments `n_gaps` and can push a vacancy toward `Stretch` or `Not yet`. The policy is defensible, but its aggregate effect on real candidate outcomes is not measured. A mature system would track tier distribution and gate-trigger rates.

### 4.4 Coverage of the Taxonomy Is Unquantified

The README notes that roughly 17% of requirement statements cannot be linked to a skill or competency. A mature application would treat this as a tracked metric with a defined acceptable threshold and a feedback loop into taxonomy curation.

### 4.5 Unresolved Product Decisions

Salary policy and travel-routing provider remain open. These are not engineering defects, but they block the transition from prototype to shippable product and should be tracked as explicit decision records.

### 4.6 Accessibility and UX Verification Absent

Responsive design is referenced, but there is no evidence of accessibility testing (keyboard navigation, screen-reader semantics, colour contrast) or usability validation with the target cohort.

---

## 5. Readiness Verdict

| Category | Status |
|---|---|
| Core matching logic | Functionally sound; maintainability risk as rules grow |
| Data pipeline | Automated; lacks observability and failure alerting |
| Security & privacy | Strong by design (stateless, no PII persisted) |
| Testing | Good unit coverage; integration and regression depth unverified |
| Documentation | Above standard for a prototype |
| Product completeness | Blocked by unresolved salary and travel decisions |

**Overall:** The prototype is a credible, well-documented foundation. It is not yet a fully developed application. The highest-value next investments are (1) observability and failure alerting around the ETL and deployment, (2) a governed rule-catalogue process or a documented migration path to NLP extraction, (3) instrumentation of tier distribution and taxonomy coverage as tracked metrics, and (4) closure of the open salary and travel decisions.

---

## 6. Recommended Priority Actions

1. Add structured logging and alerting to the nightly ETL and Cloud Run service.
2. Define and track two metrics: taxonomy coverage rate (currently ~83%) and tier distribution per demo persona.
3. Formalise the rule catalogue: one regression fixture per regex rule in `match.py`.
4. Record salary and travel-routing decisions in `DECISIONS.md` with owners and dates.
5. Conduct a lightweight accessibility and usability pass against the target graduate cohort.
