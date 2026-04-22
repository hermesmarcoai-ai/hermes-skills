---
name: agentmail
description: Manage emails via AgentMail API — list, read, send, reply, forward, and search emails from hermes.nakamoto@agentmail.to inbox using the AgentMail Python SDK.
version: 1.0.0
author: hermes
metadata:
  tags: [Email, API, AgentMail, Communication]
  homepage: https://docs.agentmail.to
---

# AgentMail Email Management

AgentMail provides programmatic email inboxes for AI agents. The current inbox is **hermes.nakamoto@agentmail.to**.

## Configuration

- **Email:** hermes.nakamoto@agentmail.to
- **Inbox ID:** hermes.nakamoto@agentmail.to
- **API Key:** Stored in env var `AGENTMAIL_API_KEY` or use inline
- **SDK:** `agentmail` Python package (`pip install agentmail`)
- **API Base:** https://api.agentmail.to/v0/

**Note:** IMAP is still under development per AgentMail docs. All operations go through the SDK/API.

## Quick Reference

```python
from agentmail import AgentMail

client = AgentMail(api_key='am_us_inbox_...')
inbox = 'hermes.nakamoto@agentmail.to'
```

### List Messages
```python
msgs = client.inboxes.messages.list(inbox_id=inbox)
print(f"Count: {msgs.count}")
for m in msgs.messages:
    print(f"Subject: {m.subject} | From: {m.from_} | Labels: {m.labels}")
```

### Read a Message
```python
msg = client.inboxes.messages.get(inbox_id=inbox, message_id=m.message_id)
print(msg.text)  # plain text body
print(msg.html)  # HTML body if available
```

### Send a Message
```python
response = client.inboxes.messages.send(
    inbox_id=inbox,
    to='recipient@example.com',
    subject='Subject',
    text='Body text',
    # html='<p>HTML body</p>',  # optional
)
```

### Reply to a Message
```python
response = client.inboxes.messages.reply(
    inbox_id=inbox,
    message_id=msg.message_id,
    text='Reply text',
)
```

### Reply All
```python
response = client.inboxes.messages.reply_all(
    inbox_id=inbox,
    message_id=msg.message_id,
    text='Reply all text',
)
```

### Forward a Message
```python
response = client.inboxes.messages.forward(
    inbox_id=inbox,
    message_id=msg.message_id,
    to='forward@example.com',
    text='Forward note',
)
```

### Update Message (mark read, add labels)
```python
response = client.inboxes.messages.update(
    inbox_id=inbox,
    message_id=msg.message_id,
    labels=['read', 'archived'],
)
```

### List Threads
```python
# First list messages to get thread_id
msgs = client.inboxes.messages.list(inbox_id=inbox)
thread_id = msgs.messages[0].thread_id
thread = client.threads.get(inbox_id=inbox, thread_id=thread_id)
```

### Raw Message (MIME)
```python
raw = client.inboxes.messages.get_raw(inbox_id=inbox, message_id=msg.message_id)
```

### Attachments
```python
# Download attachment
attachment = client.inboxes.messages.get_attachment(
    inbox_id=inbox,
    message_id=msg.message_id,
    attachment_id='attachment_id'
)
```

## Common Patterns

### Check for unread messages
```python
msgs = client.inboxes.messages.list(inbox_id=inbox)
unread = [m for m in msgs.messages if 'unread' in m.labels]
```

### List with filters
```python
client.inboxes.messages.list(inbox_id=inbox, limit=20)  # pagination
```

## Important Notes

- `message_id` on list responses is the **email Message-ID** (e.g., `<...@email.amazonses.com>`)
- `thread_id` is a UUID
- Labels include: `sent`, `received`, `unread`, `spam`, `trash`, `blocked`
- IMAP is under development — use SDK for all operations currently