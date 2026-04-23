---
name: cos-executive-assistant
description: Executive assistant skill for the Chief of Staff suite — handles email triage, calendar management, meeting prep, and scheduling coordination.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [executive-assistant, email, calendar, scheduling, cos]
    category: productivity
---

# COS Executive Assistant

Handles email triage, calendar management, meeting preparation, and scheduling for the Chief of Staff operating loop.

## When to Use

- User asks to "check my email", " triage inbox", or "draft a reply"
- Scheduling a meeting or finding available time
- Meeting prep: "What do I need to know for my 3pm?"
- Drafting communications (emails, messages, briefs)

## Setup

```bash
# Email via AgentMail
export AGENTMAIL_API_KEY=your_key

# Or via himalaya (IMAP/SMTP)
# Config: ~/.config/himalaya/config.toml

# Calendar via Google Workspace
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Usage

### Triage email

```
User: "Triage my inbox"
→ Fetch last 20 emails, classify:
  - Action needed (respond)
  - Delegate (forward to someone)
  - Reference (read later)
  - Archive (delete)
→ Summarize action items
```

### Schedule a meeting

```
User: "Find time to meet with Sarah next week"
→ Check both calendars for overlap
→ Propose 3 time slots
→ On confirmation, create calendar event
```

### Meeting prep

```
User: "Prep for 3pm with Marco"
→ Pull relevant context:
  - Last conversation topic
  - Outstanding action items
  - Related documents in Obsidian
→ Generate briefing doc
```

## Email Triage Format

```
📧 INBOX (12 new)
━━━━━━━━━━━━━━━━━
🔥 ACTION (3)
  • Sarah re: Q2 budget — reply needed
  • Hostinger re: VPS renewal — decide by Fri
  • GitHub re: PR review — 2 PRs need review

📋 DELEGATE (1)
  • Team re: deploy doc → forward to Marco

📚 REFERENCE (5)
  • Newsletter: AI weekly
  • Discord: 3 new messages in #general
  • ...

🗑️  ARCHIVE (3)
  (auto-archived: newsletters, auto-replies)
```
