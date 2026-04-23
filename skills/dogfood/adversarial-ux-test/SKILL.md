---
name: dogfood
description: Systematic exploratory QA testing of web applications — find bugs, capture evidence, and generate structured reports.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [qa, testing, dogfood, exploratory, web, bugs]
    related_skills: [adversarial-ux-test]
---

# Dogfood — Systematic Exploratory QA Testing

Systematic exploratory QA testing for web applications. Find bugs, capture evidence, and generate structured reports.

## When to Use

- "Test this app for bugs"
- "Run QA on my web app"
- "Exploratory test of [URL]"
- "Find all the things that are broken"
- Dogfood a new feature before release

## Philosophy

Exploratory testing is about **simultaneous learning and testing**. Unlike scripted testing (checklist → pass/fail), exploratory testing:
- Discovers bugs that scripted tests miss
- Tests the app the way a real user would
- Finds context-specific bugs (state, timing, data)
- Covers edge cases and error states

## Setup

```bash
# Required tools (built into Hermes)
# - browser tool (headless Chrome)
# - screenshot capability
# - console log capture

# No additional installation needed
```

## Testing Strategy

### The Bug Hunting Flow

```
1. Map the app's core workflows
2. Explore off-the-beaten-path routes
3. Test error states and edge cases
4. Probe with unexpected inputs
5. Check race conditions and timing
6. Verify state persists correctly
7. Capture evidence for each bug
```

### Core Workflows (First Pass)

Test the happy path for main user journeys:
- Sign up / log in
- Create/read/update/delete primary objects
- Navigation between major sections
- Search and filtering
- Forms and validation

### Exploratory Routes (Second Pass)

Go where users shouldn't/wouldn't:
- Rapid multi-clicking
- Back button during submissions
- Refresh at every step
- Partial form submissions
- Invalid characters and overflow
- Concurrent sessions
- Session timeout mid-action

## Evidence Collection

For each bug found, capture:

```
BUG #[N]
═══════════════════════════════════════
URL: https://app.com/buggy-page
Steps to reproduce:
  1. Navigate to /settings
  2. Click "Edit Profile"
  3. Clear the "Name" field
  4. Click "Save"

Expected: Validation error shown
Actual: Page crashes, console error:
  TypeError: Cannot read property 'name' of null

Severity: HIGH (data loss)
Evidence: [screenshot.png]
Console: [error log]
```

## Bug Severity Ratings

| Severity | Definition | Example |
|----------|-----------|---------|
| CRITICAL | Data loss, security breach | Cart items disappear on refresh |
| HIGH | Core feature broken | Can't complete checkout |
| MEDIUM | Feature broken but workaround exists | Filter resets on page change |
| LOW | Minor UX issue | Button misaligned on mobile |
| COSMETIC | Text/style only | Typo, color wrong |

## Report Format

```
═══════════════════════════════════════
DOGFOOD QA REPORT — [App Name]
Date: [YYYY-MM-DD]
Tester: Hermes Agent
URL: [Test URL]
═══════════════════════════════════════

SUMMARY
  Total bugs found: [N]
  Critical: [N]  High: [N]  Med: [N]  Low: [N]

BUGS BY SEVERITY
─────────────────

🔴 CRITICAL (2)
  #1: Cart data loss on session timeout
  #2: SQL injection in search field

🟠 HIGH (3)
  #3: Checkout fails with 3+ items
  ...

🟡 MEDIUM (5)
  ...

🟢 LOW (8)
  ...

RECOMMENDATIONS
─────────────────
1. Fix all CRITICAL before next release
2. HIGH bugs block the 2.0 launch
3. Consider fixing LOW if sprint allows
```

## Tips

- **Screenshot everything** — not just bugs, also working features
- **Reproduce each bug 2x** before reporting
- **Check mobile view** — resize browser to 375px width
- **Test on multiple browsers** if targeting all users
- **API errors** are often more serious than UI errors
- **Empty states** and **loading states** often have bugs
- **Admin/backend routes** often have fewer tests = more bugs
