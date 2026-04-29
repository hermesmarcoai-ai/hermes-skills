---
name: decision-log
description: Prompt to save strategic decisions with reasoning, alternatives considered, confidence level, and review date. Before closing strategic threads, trigger this skill to capture the decision-making process for future reference and accountability.
version: 1.0.0
author: Marco
license: MIT
metadata:
  hermes:
    tags: [decision-making, strategic, reasoning, accountability, logging]
    related_skills: [cos-chief-of-staff, cos-proactive-reporting]
    category: productivity
---

# Decision Log — Capture Strategic Reasoning Before Closing Threads

This skill ensures strategic decisions are logged with full context before closing threads. It captures the decision made, alternatives considered, reasoning, confidence level, and a review date for accountability and future reference.

## When to Trigger

**Trigger automatically when:**
- Closing a strategic planning thread
- Making a business or technical decision with long-term impact
- Resolving a debate or choosing between multiple options
- Setting priorities, budgets, or resource allocations
- Any decision that affects future work or direction

**Do not trigger for:**
- Minor operational decisions (what to name a variable, trivial tool choices)
- Routine confirmations without deliberation
- Decisions that can be easily reversed

## Decision Log Template

Before summarizing or closing a strategic thread, output the following prompt:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 DECISION LOG — Save Before Closing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Decision Made:**
[What was decided]

**Alternatives Considered:**
1. [Option A] — briefly why not
2. [Option B] — briefly why not
3. [Option C] — briefly why not

**Reasoning:**
[Key factors that led to this decision]

**Confidence Level:**
- [ ] Low (reversible, low stakes)
- [x] Medium (significant but adjustable)
- [ ] High (strategic, hard to reverse)

**Review Date:**
[YYYY-MM-DD — when to revisit this decision]

**Notes:**
[Any additional context]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Workflow

1. **Detect** strategic thread reaching conclusion
2. **Prompt** the user with the template above
3. **Collect** responses for each field
4. **Save** to decision log file
5. **Confirm** saved and provide log location

## Storage

Decisions are saved to:
```
~/.hermes/decisions/[YYYY-MM-DD]-[short-title].md
```

Format each entry as a dated markdown file for easy searching and review.

## Example Decision Entry

```markdown
# Decision: Adopt microservices architecture for Platform v2

**Date:** 2026-04-25
**Thread:** Platform Architecture Review

**Decision Made:**
Migrate to microservices with Kubernetes orchestration for Platform v2.

**Alternatives Considered:**
1. Monolithic modular — Rejected: team lacks experience with distributed systems patterns needed for scale
2. Serverless (AWS Lambda) — Rejected: cold start latency unacceptable for real-time features
3. Containerized monolith — Rejected: limits independent scaling of ML inference component

**Reasoning:**
- ML inference needs independent scaling (CPU/GPU)
- Team already has Kubernetes experience from other projects
- Real-time requirements demand low-latency internal communication
- Future ML model deployments require isolated resource management

**Confidence Level:** High

**Review Date:** 2026-07-25

**Notes:**
Re-evaluate if team grows beyond 10 engineers or ML workloads change significantly.
```

## Confidence Level Guidelines

| Level | Criteria | Revisit Frequency |
|-------|----------|-------------------|
| Low | Reversible, low stakes, easily testable | 1-2 weeks |
| Medium | Significant but adjustable | 1-3 months |
| High | Strategic, hard to reverse, expensive to change | 3-6 months |

## Pitfalls

- **Forgetting to prompt** — make this a habit before any strategic conclusion
- **Skipping alternatives** — documenting why options were rejected is as important as the decision itself
- **Setting review dates too far** — high-confidence decisions still need checkpoints
- **Vague reasoning** — "because it seemed best" is not sufficient; capture specific factors

## Verification

After saving a decision, confirm:
1. File exists at `~/.hermes/decisions/[date]-[title].md`
2. All template fields are filled
3. Review date is set appropriately
4. User confirmed the log was saved
