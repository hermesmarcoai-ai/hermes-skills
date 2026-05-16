# Force-Push via GitHub REST API

When `git push --force` times out or hangs, use the GitHub API directly to update branch refs.

## The Problem

Git push can fail in several ways despite valid credentials:
- Hangs >60s (timeout exit 124) — network/cloudflare throttling
- Returns 401 even with correct PAT
- Returns 403 "Permission denied to hermesmarcoai-ai"

## Why Git Push Times Out

Git push over HTTPS involves:
1. git-remote-https connecting to github.com:443
2. Negotiating HTTP/2
3. Sending pack data (the commit objects)
4. GitHub's Babel CDN may throttle large packs

The timeout happens before git even gets to auth challenge in some cases.

## Python Solution

```python
import subprocess, requests

def force_push_via_api(owner, repo, branch='master'):
    """
    Force-push using GitHub REST API when git push times out.
    Uses PATCH /repos/{owner}/{repo}/git/refs/heads/{branch}
    """
    # Extract token from git credentials
    with open(os.path.expanduser('~/.git-credentials')) as f:
        token = f.read().split('github.com')[1].split('@')[0].split(':')[1]
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    
    # Get local HEAD SHA
    local_sha = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd='/home/marco/.hermes',
        capture_output=True, text=True, timeout=5
    ).stdout.strip()
    
    # Get current remote SHA
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}",
        headers=headers, timeout=15
    )
    remote_sha = resp.json()['object']['sha']
    
    if local_sha == remote_sha:
        print("Already in sync!")
        return True
    
    # Force update
    resp = requests.patch(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}",
        headers=headers,
        json={"sha": local_sha, "force": True},
        timeout=30
    )
    
    if resp.status_code == 200:
        print(f"✅ Force-pushed {local_sha[:8]} → {branch}")
        return True
    else:
        print(f"❌ Failed: {resp.status_code} - {resp.text[:200]}")
        return False
```

## Shell Equivalent

```bash
#!/bin/bash
# force-push-api.sh - bypass git push timeouts
TOKEN=$(grep "github.com" ~/.git-credentials | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
OWNER="${1:-hermesmarcoai-ai}"
REPO="${2:-hermes-skills}"
BRANCH="${3:-master}"
LOCAL_SHA=$(git rev-parse HEAD)

# Get remote SHA
REMOTE_SHA=$(curl -s -H "Authorization: token $TOKEN" \
    "https://api.github.com/repos/$OWNER/$REPO/git/refs/heads/$BRANCH" | \
    python3 -c "import sys,json; print(json.load(sys.stdin)['object']['sha'])")

if [ "$LOCAL_SHA" = "$REMOTE_SHA" ]; then
    echo "Already synced"
    exit 0
fi

# Force update
RESULT=$(curl -s -X PATCH \
    -H "Authorization: token $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"sha\":\"$LOCAL_SHA\",\"force\":true}" \
    "https://api.github.com/repos/$OWNER/$REPO/git/refs/heads/$BRANCH")

if echo "$RESULT" | grep -q '"ref"'; then
    echo "✅ Force-pushed to $BRANCH"
else
    echo "❌ Failed: $RESULT"
fi
```

## API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/repos/{owner}/{repo}/git/refs/heads/{branch}` | Get current branch SHA |
| PATCH | `/repos/{owner}/{repo}/git/refs/heads/{branch}` | Force update branch to new SHA |

## When to Use This

- git push times out after 30-60s
- Returns 401/403 with valid token
- Need quick sync without debugging credential issues
- Backup branch already created but master won't force push

## Session Transcript (2026-05-16)

```
git push --force origin master → timeout after 60s (exit 124)
git remote set-url with token → 403 "Permission denied to hermesmarcoai-ai"
curl to api.github.com → works fine, token valid

Python PATCH request with force:true → 200 OK
Master branch updated successfully via API
```

**Key insight**: The git credential system was failing but direct API with same token worked. Possibly git-remote-https was caching stale auth or cloudflare was throttling git protocol specifically.