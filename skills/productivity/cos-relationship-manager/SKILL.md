---
name: cos-relationship-manager
description: Relationship manager for the Chief of Staff suite — tracks contacts, follows up on outstanding conversations, and maintains relationship context.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [relationships, contacts, follow-up, crm, cos]
    category: productivity
---

# COS Relationship Manager

Tracks contacts, follows up on outstanding conversations, and maintains relationship context. Part of the Chief of Staff operating loop.

## When to Use

- "Did I follow up with X about Y?"
- "Who should I catch up with this week?"
- "Update contact info for someone"
- "What was the last conversation with X?"

## Storage

Contacts stored in Obsidian with this structure:
```
contacts/
  ├── john-doe.md
  ├── sarah-smith.md
  └── ...
```

Each contact note contains:
- Basic info (name, role, company, channels)
- Last contacted date
- Outstanding items
- Relationship context (important facts)

## Usage

### Add/update contact

```
User: "I met someone new — Alex from Vercel, they work on AI infra"
→ Create contacts/alex-vercel.md
→ Fields: name, company, role, channel, met_via, interests
```

### Follow-up check

```
User: "Any follow-ups due this week?"
→ Query contacts with follow_up_date ≤ today
→ Generate reminder list
```

### Relationship context

```
User: "What do I know about Marco?"
→ Return contacts/marco.md
→ Last conversation: Apr 20 about VPS migration
→ Outstanding: needs to review PR #47
→ Notes: prefers concise responses
```

## Weekly Relationship Check

Every Friday:
- Pull contacts with `follow_up_date ≤ today`
- Generate personalized catch-up suggestions
- Flag any stale relationships (>30 days no contact)

## Integration

- Works with Obsidian (contact notes)
- Telegram/Discord handles for quick reach-outs
- Meeting notes linked from calendar events
