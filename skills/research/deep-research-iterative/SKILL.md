---
name: deep-research-iterative
description: Iterative deep research loop using Perplexity Sonar Deep Research — research → synthesize → gap_analysis → research. Use when user wants thorough, multi-pass research on a complex topic.
triggers:
  - iterative deep research
  - deep research loop
  - research synthesis gap analysis
  - thorough research
  - comprehensive research
---

# Deep Research Iterative

## Overview

Iterative deep research workflow that cycles through **research → synthesize → gap_analysis → research** until knowledge gaps are saturated. Uses Perplexity Sonar Deep Research model for comprehensive coverage.

## When to Use

- Complex topics requiring multiple passes
- User says "iterative deep research", "thorough research", or "comprehensive research"
- Topics where initial findings reveal gaps needing deeper investigation
- Multi-faceted questions that benefit from progressive refinement

## Workflow Loop

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ┌──────────┐    ┌────────────┐    ┌──────────────────┐   │
│   │ RESEARCH │───▶│ SYNTHESIZE │───▶│ GAP_ANALYSIS     │   │
│   └──────────┘    └────────────┘    └────────┬─────────┘   │
│                                                │             │
│                        ┌───────────────────────┘             │
│                        ▼                                     │
│                   ┌──────────┐                               │
│                   │ RESEARCH │ (refined)                      │
│                   │ (pass N) │                               │
│                   └────┬─────┘                               │
│                        │                                      │
│         ┌──────────────┴──────────────┐                     │
│         ▼                              ▼                     │
│   ┌───────────┐              ┌─────────────┐                 │
│   │ Continue? │              │   DONE ✓   │                 │
│   └─────┬─────┘              └─────────────┘                 │
└─────────┼─────────────────────────────────────────────────────┘
          │ No
          ▼
    [gap_threshold]
```

## Implementation

### Phase 1: RESEARCH

**Purpose:** Gather comprehensive information on the topic.

```python
import os

def set_deep_research_model():
    """Configure Perplexity Sonar Deep Research model."""
    os.environ["AUXILIARY_WEB_EXTRACT_MODEL"] = "perplexity/sonar-deep-research"
    os.environ["AUXILIARY_WEB_EXTRACT_PROVIDER"] = "openrouter"
    os.environ["AUXILIARY_WEB_EXTRACT_BASE_URL"] = "https://openrouter.ai/api/v1"
```

**Research prompt template:**
```
Research topic: {topic}

Provide a comprehensive overview covering:
1. Core concepts and definitions
2. Current state of knowledge
3. Key players, developments, or perspectives
4. Recent innovations or findings (last 1-2 years)
5. Controversies or debates
6. Practical applications or implications

Search multiple sources and synthesize findings.
```

### Phase 2: SYNTHESIZE

**Purpose:** Organize findings into a coherent structure.

**Synthesis prompt template:**
```
Synthesize the following research findings into a structured summary:

{research_findings}

Organize into:
- Key findings (top 5-7)
- Supporting evidence
- Conflicting viewpoints or gaps in evidence
- Emerging trends or developments

Format as a clear, hierarchical document.
```

### Phase 3: GAP_ANALYSIS

**Purpose:** Identify what is NOT yet known or needs deeper investigation.

**Gap analysis prompt template:**
```
Analyze the synthesized research and identify knowledge gaps:

{synthesized_content}

For each gap, rate:
- **Severity**: Critical / Important / Minor
- **Type**: Factual unknown, contradictory evidence, outdated info, or missing perspective
- **Researchable**: Yes (online sources exist) / No (requires expert consultation) / Partial

Output a ranked list of gaps by severity, with specific questions to answer in next pass.
```

### Phase 4: REFINED RESEARCH

**Purpose:** Address identified gaps in the next iteration.

**Refined research prompt:**
```
Follow-up research to address specific gaps:

Previous topic: {original_topic}
Identified gaps:
{gap_list}

For each gap:
1. What specific question needs answering?
2. What sources might contain this information?
3. What new search terms or angles should be explored?

Conduct targeted searches to fill these gaps.
```

## Iteration Control

### Stop Conditions

Stop iterating when ANY of:
1. **Gap saturation**: No critical gaps remain (all rated Important/Critical are "Researchable: Yes/Partial" and answered)
2. **Diminishing returns**: New findings repeat existing knowledge (set `min_novel_findings = 2` threshold)
3. **Max iterations**: Hard cap of 5 passes (prevents infinite loops)
4. **User override**: User says "stop" or "that's enough"

### Iteration State

Track between passes:
```python
state = {
    "pass": 1,
    "topic": str,
    "research_findings": [],
    "syntheses": [],
    "gaps": [],
    "answered_gaps": [],
    "stop_reason": None
}
```

## Example Workflow

```
User: "Do iterative deep research on the current state of solid-state batteries"

Pass 1:
  - Research: Gather overview of solid-state battery tech, players, timeline
  - Synthesize: Key players (Toyota, QuantumScape, Samsung), challenges, timelines
  - Gaps: Energy density compared to液态, cost projections, manufacturing challenges
  - Decision: Continue (critical gaps remain)

Pass 2:
  - Research: Targeted searches on energy density comparisons, cost analysis
  - Synthesize: Updated findings with specific data points
  - Gaps: Supply chain specifics, recycling challenges
  - Decision: Continue

Pass 3:
  - Research: Supply chain and recycling landscape
  - Synthesize: Full picture emerging
  - Gaps: Minor items only
  - Decision: Stop (gap saturation reached)

Output: Comprehensive research brief covering all critical gaps
```

## Output Format

Final deliverable should include:
1. **Executive Summary** (3-5 bullet points)
2. **Key Findings** (detailed, sourced)
3. **Gap Analysis Results** (what was investigated, what remains unknown)
4. **Iteration Log** (optional, for transparency)

## Pitfalls

- **Don't skip synthesis**: Jumping from research to gap analysis loses context
- **Don't over-iterate**: 5 passes max, or stop when gaps are satisfied
- **Reset model after completion**: Return to normal model to avoid token waste
- **Track answered vs unanswered gaps**: Don't re-research already-answered gaps

## Environment Setup

See `scripts/deep_research_trigger.py` in the parent `deep-research` skill for the model configuration helper.
