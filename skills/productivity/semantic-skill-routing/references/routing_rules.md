# Manual Override Rules for Skill Routing

These rules override the TF-IDF scoring when specific task patterns are detected.

## Known Task Type → Skill Mapping

| Task Pattern | Target Skill | Override Reason |
|--------------|--------------|-----------------|
| "code review", "review code", "review my code" | github-code-review | Precise match for code review workflow |
| "pull request", "create pr", "open PR" | github-pr-workflow | PR creation is a specific workflow |
| "git commit", "commit changes" | github-pr-workflow | Related to git workflow |
| "schedule meeting", "add event", "calendar" | google-workspace | Google Calendar specific |
| "send email", "compose email" | agentmail | Email composition |
| "docker", "container", "dockerfile" | docker-management | Container management |
| "deploy", "deployment", "kubernetes" | docker-management | Deployment involves containers |
| "cron", "cronjob", "scheduled task" | cron-job-recovery | Cron job management |
| "backup", "restore" | hermes-vps-migration | Backup/restore workflow |
| "jupyter", "notebook", "data analysis" | jupyter-live-kernel | Interactive data analysis |
| "model", "llm", "fine-tune" | huggingface-hub | ML model management |
| "blender", "3d render" | blender-mcp | 3D rendering |
| "discord", "telegram", "messaging" | hermes-discord-bot-orchestration | Messaging platforms |
| "weather" | weather-plugin | Weather information |
| "password", "secret", "api key" | github-credential-cleanup | Security sensitive |
| "code review", "security scan" | code-review | Security focused review |
| "test", "unit test", "pytest" | test-driven-development | Testing workflow |

## Model-Specific Hints

For these task types, prefer stronger models:

| Task Type | Recommended Model | Reason |
|-----------|------------------|--------|
| "architectural decision", "system design", "high level design" | claude-sonnet-4, gpt-4.1 | Complex reasoning needed |
| "refactor large codebase", "major rewrite" | claude-sonnet-4, gpt-4.1 | Heavy code manipulation |
| "deep research", "comprehensive analysis" | perplexity-sonar-pro | Research-focused |
| "quick question", "simple fix" | haiku, gpt-4o-mini | Lightweight model sufficient |
| "code generation", "boilerplate" | haiku, gpt-4o-mini | Fast generation ok |
| "creative writing", "story", "content" | sonnet-4, gpt-4o | Creative reasoning |
| "math", "proof", "formal logic" | claude-opus-4, gpt-4.1 | Mathematical reasoning |

## Negative Rules (Never Suggest)

These skills should NEVER be auto-suggested regardless of score:

| Skill | Reason |
|-------|--------|
| hermes-gateway-restart-notification | Internal system maintenance |
| security-health-check | Sensitive - only run explicitly |
| hermes-auto-update-cron | System maintenance |

## Category Boosting

When query contains category names, boost skills in that category:

| Query Contains | Boost Category |
|----------------|----------------|
| "productivity", "productivity tool" | +0.2 to all productivity/* skills |
| "devops", "infrastructure" | +0.2 to all devops/* skills |
| "creative", "design", "art" | +0.2 to all creative/* skills |
| "AI", "agent", "automation" | +0.2 to all autonomous-ai-agents/* skills |
| "data science", "ML", "machine learning" | +0.2 to all data-science/* skills |
| "security", "hardening" | +0.2 to all security/* skills |

## Priority Rules

1. **Explicit user request wins**: If user says "use X skill", always obey
2. **Manual overrides apply first**: These rules trigger before TF-IDF scoring
3. **Category boosts apply after scoring**: Add boost to TF-IDF scores
4. **Never suggest negative rule skills**: Filter them out completely
