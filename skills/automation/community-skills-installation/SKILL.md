---
name: community-skills-installation
title: Install Community Skills & Plugins
category: automation
description: Install and verify community skills from GitHub repositories safely
version: 1.0
author: hermes-agent
tags:
  - skills
  - plugins
  - installation
  - security
---

# Install Community Skills & Plugins

Safely install and verify community skills/plugins from GitHub repositories for Hermes Agent.

## ⚠️ Security Checklist

Before installing ANY community skill:

1. **Verify GitHub repo legitimacy**
   - Check owner/organization (Nous Research, known contributors)
   - Star count (889+ is good)
   - Recent activity (updated recently)
   - README quality

2. **Inspect repository contents**
   - No suspicious files (.sh scripts, binary executables)
   - Proper licensing (MIT, Apache 2.0)
   - Clear documentation

3. **Identify skill type**
   - **Hermes plugins**: Have `plugin.yaml` → use `hermes plugins install`
   - **Claude Code plugins**: Use `/plugin` commands
   - **Skill directories**: Auto-loaded from `~/.hermes/skills/`

## Installation Process

### Step 1: Fetch Repository Info

```python
import requests

# Get repo contents
url = "https://api.github.com/repos/OWNER/REPO/contents/"
response = requests.get(url)
data = response.json()

# Get repo description
repo_url = "https://api.github.com/repos/OWNER/REPO"
repo_response = requests.get(repo_url)
repo_data = repo_response.json()

# Verify: stars, created_at, updated_at, description
```

### Step 2: Read README for Installation Instructions

```python
# Read README
url = "https://raw.githubusercontent.com/OWNER/REPO/branch/README.md"
response = requests.get(url)
readme = response.text

# Extract skill list and installation requirements
```

### Step 3: Verify Plugin Structure

```python
import os
import subprocess

skill_path = "~/.hermes/skills/NAME"

# Check for plugin.yaml (Hermes plugin)
plugin_yaml = os.path.join(skill_path, "plugin.yaml")
if os.path.exists(plugin_yaml):
    print("✅ Hermes Plugin Detected")
    
# Check for skill.md
skill_md = os.path.join(skill_path, "skill.md")
if os.path.exists(skill_md):
    print("✅ Skill documentation found")
```

### Step 4: Install via Hermes CLI (Preferred)

```bash
# Install Hermes plugin
hermes plugins install OWNER/REPO

# Verify installation
hermes plugins list

# Restart gateway for plugin to take effect
hermes gateway restart
```

### Step 5: Verify Skills Loaded

```bash
# List all available skills
hermes skills list

# Filter by category
hermes skills list | grep -i CATEGORY
```

## Common Pitfalls

❌ **Don't use pip install** - Most Hermes plugins are NOT Python packages
❌ **Don't assume all repos are safe** - Always inspect first
❌ **Don't skip verification** - Check `plugin.yaml` structure

✅ **Use `hermes plugins install`** for plugin repos
✅ **Clone manually** with `git clone` if needed
✅ **Verify with `hermes skills list`** after installation

## Example: Installing from awesome-hermes-agent

```bash
# 1. Clone to inspect
git clone https://github.com/0xNyk/awesome-hermes-agent.git

# 2. Read README to identify skills
cat awesome-hermes-agent/README.md

# 3. Install individual plugins
hermes plugins install robbyczgw-cla/hermes-web-search-plus
hermes plugins install FahrenheitResearch/hermes-weather-plugin

# 4. Verify
hermes plugins list
hermes skills list

# 5. Restart gateway
hermes gateway restart
```

## Verification Commands

```bash
# Check plugin status
hermes plugins list

# Check skill availability
hermes skills list

# Test plugin functionality
hermes chat

# Check gateway logs
hermes gateway logs
```

## When to Reject

- ❌ Experimental/Beta with no production track record
- ❌ Requires suspicious API keys or permissions
- ❌ Poor documentation or no README
- ❌ Owner is unknown/anonymous with low stars
- ❌ Contains `.sh` scripts or suspicious executables

## Integration with Morning Briefs

For weather plugins specifically (useful for Aosta forecasts):
- `wx_conditions` - Current weather
- `wx_forecast` - 7-day forecast  
- `wx_alerts` - Severe weather warnings
- `wx_radar` - Radar imagery
- `wx_model_imagery` - Model visualizations

These work automatically once the plugin is installed and the gateway is restarted.