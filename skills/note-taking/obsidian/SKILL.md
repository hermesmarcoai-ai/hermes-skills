---
name: obsidian
description: Read, search, and create notes in the Obsidian vault.
---

# Obsidian Vault

Two modes are supported:

## Mode 1: Remote vault via GitHub + MCP (Hermes on VPS, Obsidian on user's Mac)

When the vault lives on the user's local machine and Hermes runs on a remote VPS, sync via GitHub.

### Setup
1. Create a private GitHub repo for the vault
2. User installs "Obsidian Git" plugin on Mac and pushes vault (or does it via terminal: `git init -b main && git add -A && git commit -m "Initial" && git remote add origin <URL> && git push -u origin main`)
3. Clone the repo on the VPS: `git clone https://<GHP_TOKEN>@github.com/<user>/<repo>.git /home/Obsidian-Vault`
4. Add MCP filesystem server in `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  obsidian:
    command: npx
    args: [-y, "@modelcontextprotocol/server-filesystem", "/home/Obsidian-Vault"]
    timeout: 120
```
5. Restart Hermes — tools like `mcp_obsidian_read_file`, `mcp_obsidian_write_file`, `mcp_obsidian_search_files`, etc. become available
6. Set up auto-sync: user configures Obsidian Git plugin for auto-push/pull every 5 min, or runs manual push/pull after edits

### Working with notes
Use the `mcp_obsidian_*` tools (discovered at startup). Common tools:
- `mcp_obsidian_read_file` — read a note
- `mcp_obsidian_write_file` — create/overwrite a note
- `mcp_obsidian_search_files` — find notes by pattern
- `mcp_obsidian_list_directory` — browse vault structure
- `mcp_obsidian_edit_file` — line-level edits

### PITFALLS
- GitHub credential helper may not work in non-interactive shells — embed token in clone URL: `https://<token>@github.com/user/repo.git`
- The vault repo may be empty initially — wait for user to push first commit
- MCP filesystem tools use forward slashes relative to the vault root path
- Auto-sync delay: changes made by Hermes won't appear in Obsidian until user does a git pull (auto-pull every 5 min recommended)

## Mode 2: Local vault (Hermes and Obsidian on same machine)

**Location:** Set via `OBSIDIAN_VAULT_PATH` environment variable (e.g. in `~/.hermes/.env`).
If unset, defaults to `~/Documents/Obsidian Vault`.
Note: Vault paths may contain spaces - always quote them.

## Read a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat "$VAULT/Note Name.md"
```

## List notes

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# All notes
find "$VAULT" -name "*.md" -type f

# In a specific folder
ls "$VAULT/Subfolder/"
```

## Search

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# By filename
find "$VAULT" -name "*.md" -iname "*keyword*"

# By content
grep -rli "keyword" "$VAULT" --include="*.md"
```

## Create a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat > "$VAULT/New Note.md" << 'ENDNOTE'
# Title

Content here.
ENDNOTE
```

## Append to a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
echo "
New content here." >> "$VAULT/Existing Note.md"
```

## Building a Memory Graph Knowledge Base

The [obsidian-openclaw-memory](https://github.com/Samin12/obsidian-openclaw-memory) pattern provides a proven structure for AI-persistent memory via Obsidian. Adapt it by pre-populating with real user data from Hermes memory.

### Core File Structure
```
vault/
├── USER.md              # Who the human is (name, goals, constraints, tech stack)
├── AGENTS.md            # How the AI operates (memory protocol, tool rules, safety)
├── SOUL.md              # AI persona & tone guidelines
├── MEMORY.md            # ★ Distilled long-term memory (short, high-signal entries)
├── HEARTBEAT.md         # Proactive maintenance checklist
├── memory/
│   └── YYYY-MM-DD.md    # Raw daily session logs
├── second-brain/
│   ├── README.md        # Index & navigation
│   ├── concepts/        # Deep dives on important ideas/frameworks
│   ├── documents/       # Working docs & strategies
│   └── journal/         # Daily structured summaries
├── directives/          # SOPs & repeatable workflows
├── execution/           # Reusable Python scripts
├── projects/            # One folder per active project
└── skills/              # Custom skill definitions
```

### Population Strategy (from Hermes memory)
1. **USER.md** — Pull from memory "user" store (identity, goals, constraints, tech stack)
2. **AGENTS.md** — Pull from memory "memory" store (infrastructure, tool configs, known fixes)
3. **MEMORY.md** — Distill all current memory entries into curated long-term format
4. **SOUL.md** — Derive from communication patterns in past sessions
5. **second-brain/concepts/** — Create starter notes for user's focus areas (from memory goals/focus)
6. **Add `[[wiki-links]]`** in every file footer to build the knowledge graph edges

### Key Principles
- **Pre-populate with real data** — users value seeing their actual context, not empty templates
- **Use wiki-links everywhere** — `[[USER]]`, `[[MEMORY]]`, etc. so Graph View shows connections
- **Tags in frontmatter** — `tags: [memory, identity, business]` for Dataview queries
- **Create a daily log entry** for the setup session itself (`memory/YYYY-MM-DD.md`)

### Git Push Pitfall: `gh repo create --push` fails on VPS
The `gh repo create --push` command fails because:
1. Git user identity is not configured (`user.name` / `user.email`)
2. The remote URL requires authentication but git can't prompt interactively

**Proven fix:**
```bash
# Set local git identity (don't use --global, keep it vault-specific)
git config user.name "Hermes Agent"
git config user.email "hermes@example.com"

# Commit first
git add -A && git commit -m "Initial vault setup"

# Create repo
gh repo create <org>/<repo-name> --public --source=. --remote=origin

# Set authenticated remote URL and push
GH_TOKEN=$(gh auth token)
git remote set-url origin "https://x-access-token:${GH_TOKEN}@github.com/<org>/<repo-name>.git"
git push -u origin main
```

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
