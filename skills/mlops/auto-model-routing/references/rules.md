# Auto Model Routing Rules

## Routing Table: Keywords → Model Mappings

### Category: reasoning/heavy
**Model:** claude-sonnet-4-20250514
**Provider:** anthropic
**Confidence:** 0.85

| Keywords | Description |
|---------|-------------|
| debug | Debugging complex issues, error analysis |
| architect | System design, architecture planning |
| design | UI/UX design, system design |
| analyze | Deep analysis, data analysis |
| complex | Complex multi-step problems |
| system | System-level thinking |

### Category: fast/light
**Model:** MiniMax-M2.7-highspeed
**Provider:** minimax
**Confidence:** 0.9

| Keywords | Description |
|---------|-------------|
| quick | Fast response needed |
| simple | Simple, straightforward tasks |
| one-liner | Single line answers |
| small | Small changes, minor fixes |
| easy | Easy tasks, low complexity |
| fix typo | Typo corrections |

### Category: creative
**Model:** MiniMax-M2.7-highspeed
**Provider:** minimax
**Confidence:** 0.8

| Keywords | Description |
|---------|-------------|
| write | General writing tasks |
| story | Story writing, fiction |
| creative | Creative tasks |
| song | Songwriting, lyrics |
| poem | Poetry writing |
| narrative | Narrative writing |

### Category: research
**Model:** deep-research-iterative
**Provider:** perplexity
**Confidence:** 0.85

| Keywords | Description |
|---------|-------------|
| research | Research tasks |
| find | Finding information |
| investigate | Investigation, fact-finding |
| explore | Exploration, discovery |
| search | Searching for answers |

### Category: coding
**Model:** claude-sonnet-4-20250514
**Provider:** anthropic
**Confidence:** 0.85

| Keywords | Description |
|---------|-------------|
| code | Writing code |
| implement | Implementing features |
| refactor | Code refactoring |
| program | Programming tasks |
| build | Building applications |
| function | Writing functions |

## Model Cost Hints

| Model | Relative Cost | Best For |
|-------|--------------|----------|
| MiniMax-M2.7-highspeed | $ | Quick, simple, creative tasks |
| claude-sonnet-4-20250514 | $$$ | Complex reasoning, coding, architecture |
| deep-research-iterative | $$$ | In-depth research tasks |

**Rule:** Don't route cheap/simple tasks to expensive models.

## Confidence Level Guidelines

### High Confidence (0.8-1.0)
- Explicit keyword match in task text
- Strong signal words present
- Clear task category

### Medium Confidence (0.5-0.79)
- Partial keyword match
- Context inference required
- Multiple possible categories

### Low Confidence (0.3-0.49)
- No keyword match
- Ambiguous task
- Uses fallback model

## Routing Algorithm

1. **Lowercase** task text
2. **Tokenize** into words
3. **Match** against keyword lists
4. **Score** each category by matches
5. **Select** highest-scoring category
6. **Return** model + provider + confidence

### Tie-Breaking Rules
1. Prefer higher base confidence category
2. If still tied, use last matching category
3. If no matches, use fallback

## Fallback Configuration

**Default Model:** MiniMax-M2.7-highspeed
**Default Provider:** minimax
**Fallback Confidence:** 0.3
**Reason:** "No matching keywords, using fallback model"
