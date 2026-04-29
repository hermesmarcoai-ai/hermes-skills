---
name: content-factory
description: Design spec for a fully automated Content Factory inside Discord - multi-agent architecture for trending topics, scripts, visuals, and organized output.
trigger: content-factory
category: creative
---

# Content Factory — Discord Multi-Agent Architecture

## 1. System Overview

```
[Trend Scanner] → [Topic Selector] → [Script Writer] → [Visual Generator]
      ↓                  ↓                 ↓                ↓
[Database] ←─────────────────────────────────────────────────
      ↓
[Discord Output Channels]
```

## 2. Discord Server Structure

### Category: CONTENT PIPELINE
| Channel | Purpose |
|---------|---------|
| #trending-topics | Auto-posted trending subjects |
| #approved-topics | Manually approved topics for production |
| #scripts-drafts | Generated scripts for review |
| #scripts-final | Approved scripts ready for production |
| #thumbnails | Generated visual assets |
| #content-queue | Final content ready to publish |

### Category: INTELLIGENCE
| Channel | Purpose |
|---------|---------|
| #topic-intel | Trending data, analytics |
| #performance-metrics | Content performance tracking |
| #feedback-loop | Human corrections fed back |

### Category: AGENTS
| Channel | Purpose |
|---------|---------|
| #agent-log | Agent activity logs |
| #agent-errors | Errors requiring attention |

### Category: OPERATIONS
| Channel | Purpose |
|---------|---------|
| #commands | Bot command input |
| #daily-brief | Daily content brief from Hermes |
| #alerts | System notifications |

## 3. Multi-Agent System

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| Trend Scanner | Monitor trends | Twitter/X API, Google Trends, Reddit | List of trending topics |
| Topic Selector | Filter & rank | Trending topics list + criteria | 3-5 approved topics |
| Script Writer | Write scripts | Approved topic | Video script (hook + body + CTA) |
| Visual Generator | Create assets | Final script | Thumbnail + post images |
| Quality Controller | Validate output | Script + visuals | PASS/FAIL + feedback |
| Publisher | Format & post | Final content | Discord message + metadata |

## 4. Workflow Pipeline

```
1. TREND SCAN (every 6h)
   → Fetch: Twitter API, Google Trends, Reddit
   → Filter: relevance score > threshold
   → Output: trending-topics channel

2. TOPIC APPROVAL (automatic + manual)
   → Hermes reviews and ranks
   → User approves or rejects
   → Output: approved-topics channel

3. SCRIPT GENERATION (triggered on approval)
   → Script Writer agent picks topic
   → Generates: hook, main content, CTA
   → Output: scripts-drafts channel

4. QUALITY CHECK (automatic)
   → Quality Controller reviews
   → PASS → scripts-final
   → FAIL → feedback-loop + retry

5. VISUAL GENERATION (triggered on script approval)
   → Visual Generator creates thumbnail
   → Creates social media assets
   → Output: thumbnails channel

6. PUBLISH READY (automatic)
   → Publisher formats for each platform
   → Output: content-queue channel
```

## 5. Automation Stack

| Tool | Purpose |
|------|---------|
| Hermes Agent | Orchestrator, runs all agents |
| Discord Bot | Channel management, posting |
| Twitter/X API | Trend monitoring |
| Google Trends API | Trend data |
| DALL-E / Flux | Thumbnail generation |
| Claude/GPT | Script writing |
| n8n / Make | Workflow automation glue |
| Redis | Queue management |

## 6. Leverage & Scalability

- Agents run in parallel — multiple scripts simultaneously
- Queue-based processing — no blocking
- Templates — script structure reused, only content changes
- Modular agents — add new formats without rebuilding
- Human-in-the-loop only at approval gates

## 7. Quality Control

- Automatic scoring: engagement prediction, completeness check
- Human review: scripts and thumbnails must be approved
- Feedback loop: corrections improve next outputs
- Performance tracking: metrics per topic, per format, per agent

## 8. Common Mistakes to Avoid

1. Skipping the approval gate — fully automated content loses quality
2. Too many agents — start with 3, add only when necessary
3. No feedback loop — agents repeat mistakes without corrections
4. Monolithic design — keep agents small and replaceable
5. Ignoring metrics — track what works, kill what doesn't
