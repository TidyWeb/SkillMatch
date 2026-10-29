# SkillMatch Evidence & Matching Framework

Version: 1.0

Author: SK Mizanur Rahman

---

# 1. Purpose

The SkillMatch Evidence & Matching Framework defines how user experience, work history, and achievements are transformed into evidence that can be matched against employer requirements.

The objective is to produce tailored CVs that:

- Reflect genuine experience
- Maintain user authenticity
- Avoid AI hallucination
- Provide transparent evidence mapping
- Identify genuine capability gaps

This framework supports the Tailor My CV workflow and acts as the link between:

- Job advertisements
- Competencies
- CV content
- Biography content
- Tailored CV generation

---

# 2. Design Principles

## 2.1 Evidence First

Every statement used in a tailored CV must be supported by evidence.

Evidence may originate from:

- CV content
- Biography stories
- Biography examples
- User clarification

If evidence cannot be found, the requirement remains a gap.

---

## 2.2 No Hallucination

The system must never:

- Invent skills
- Invent achievements
- Invent metrics
- Invent project experience
- Invent software knowledge

Where no evidence exists, a gap must be recorded.

---

## 2.3 Evidence Traceability

Every tailored statement should be traceable back to its source.

Example:

Stakeholder Management
    ↓
Story S12
    ↓
Project Coordinator Role
    ↓
Biography.md

This enables transparency and validation.

---

# 3. Core Entities

## 3.1 Job Requirement

A capability, skill, qualification or experience requested by an employer.

Examples:

- Stakeholder Management
- SQL
- Attention to Detail
- Process Improvement

Attributes:

- Requirement ID
- Requirement Text
- Requirement Type
- Priority

Priority Values:

- Essential
- Desirable

---

## 3.2 Competency

A normalised skill definition used throughout SkillMatch.

Examples:

- stakeholder_management
- analytical_thinking
- customer_insight
- process_improvement
- project_management

Competencies provide a common language between:

- Job advertisements
- User experience
- Matching logic

---

## 3.3 Evidence

Evidence is a verified statement supporting a competency.

Types:

### CV Evidence

Origin:

skillmatch_cv_copy.md

Example:

"Co-ordinated multiple project stakeholders."

Strength:

Moderate

---

### Story Evidence

Origin:

biography.md

Example:

Complete STAR story.

Strength:

Strong

---

### Example Evidence

Origin:

biography.md

Example:

Single confirmed example.

Strength:

Moderate

---

### User Confirmation

Origin:

Current conversation.

Example:

"Yes, I used Power BI for monthly reporting."

Strength:

Conditional

Requires validation.

---

# 4. Evidence Hierarchy

Evidence is not equal.

SkillMatch applies a hierarchy.

Level 1

Story Evidence

Highest confidence.

Contains:

- Situation
- Task
- Action
- Result

Level 2

CV Evidence

Documented experience.

Level 3

Example Evidence

Single confirmed example.

Level 4

User Confirmation

Requires interpretation.

---

# 5. Matching Model

Matching occurs at requirement level.

Requirement
    ↓
Competency
    ↓
Evidence Search
    ↓
Evidence Evaluation
    ↓
Match Status

---

# 6. Match Status

## Match

Strong evidence exists.

Criteria:

- Story Evidence available

or

- Multiple supporting sources

Result:

Requirement supported.

---

## Partial Match

Related evidence exists.

Criteria:

- Indirect evidence
- Transferable experience
- Single supporting source

Result:

Requirement partially supported.

---

## Gap

No evidence exists.

Criteria:

- No matching evidence found

Result:

Requirement remains a gap.

No content may be created to fill the gap.

---

# 7. Evidence Evaluation Matrix

| Evidence Source | Confidence |
|---------------|------------|
| STAR Story | High |
| CV Statement | Medium |
| Example | Medium |
| User Confirmation | Low |

---

# 8. Requirement Mapping Workflow

Step 1

Read job brief.

Step 2

Extract requirements.

Step 3

Map each requirement to competencies.

Step 4

Search available evidence.

Step 5

Evaluate evidence strength.

Step 6

Assign match status.

Step 7

Generate evidence map.

Step 8

Present evidence map to user.

Step 9

User confirms or adjusts.

Step 10

Generate tailored CV.

---

# 9. Gap Management

Gaps are valuable information.

A gap indicates:

- Missing experience
- Missing evidence
- Missing qualification

Gaps must:

- Be reported
- Be explained
- Never be hidden

Gaps must not be rewritten as strengths.

---

# 10. Tailored CV Generation Rules

The tailoring process may:

- Reorder evidence
- Emphasise relevant experience
- Rewrite wording for clarity
- Build stronger profile statements

The tailoring process may not:

- Invent evidence
- Invent metrics
- Invent certifications
- Invent software skills
- Invent project work

---

# 11. Future Enhancements

Potential future developments:

- Evidence scoring
- Confidence scoring
- Competency weighting
- Automated gap analysis
- Match percentage calculations
