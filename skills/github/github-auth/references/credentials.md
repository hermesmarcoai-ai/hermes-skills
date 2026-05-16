# GitHub Credentials — Extraction & Storage Reference

## Extract token from `~/.git-credentials`

```bash
# Pattern: https://<token>@github.com
TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
echo "${TOKEN}"
```

## Store token from Bitwarden into `~/.git-credentials`

Use when Bitwarden vault is **unlocked** and you have the GitHub item:

```bash
SESS=$(BW_MASTER_PASSWORD='...' bw unlock --passwordenv BW_MASTER_PASSWORD 2>/dev/null | grep -o "export BW_SESSION=[^']*" | cut -d= -f2 | tr -d "'")
# If above returns empty, try session from ~/.bashrc:
SESS="<BW_SESSION_from_bashrc>"
TOKEN=$(bw get password "GitHub" --session "$SESS" --raw 2>/dev/null | tail -1)
echo "https://${TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
git config --global credential.helper store
```

## Store token directly (no Bitwarden)

```bash
echo "https://<TOKEN>@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
git config --global credential.helper store
git config --global user.name "Marco Olivero"
git config --global user.email "marco.olivero.dev@gmail.com"
```

## Test authentication

```bash
git ls-remote https://github.com/<owner>/<repo>.git 2>&1 | head -3
```

---

## Force-Push via GitHub API (Bypassing Git Push Timeouts)

When `git push --force` times out (network/cloudflare throttling), use the GitHub REST API directly to update branch refs.

**Scenario**: git push hangs for >60s or returns 401/403 despite valid credentials.

**Python pattern:**
```python
import subprocess, requests

# Get local SHA
local_sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd='/home/marco/.hermes',
                           capture_output=True, text=True, timeout=5).stdout.strip()

# Get remote SHA
token = "ghp_XXXXX"  # extract from ~/.git-credentials or env
resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}",
                   headers={"Authorization": f"token {token}"}, timeout=15)
remote_sha = resp.json()['object']['sha']

# Force update if different
if local_sha != remote_sha:
    resp = requests.patch(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}",
        headers={"Authorization": f"token {token}"},
        json={"sha": local_sha, "force": True}, timeout=30
    )
    print(f"Status: {resp.status_code} - {'SUCCESS' if resp.status_code == 200 else 'FAILED'}")
```

**Shell equivalent using curl:**
```bash
TOKEN=$(grep "github.com" ~/.git-credentials | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
OWNER="hermesmarcoai-ai"
REPO="hermes-skills"
BRANCH="master"
LOCAL_SHA=$(git rev-parse HEAD)

# Get remote SHA
REMOTE_SHA=$(curl -s -H "Authorization: token $TOKEN" \
    "https://api.github.com/repos/$OWNER/$REPO/git/refs/heads/$BRANCH" | \
    python3 -c "import sys,json; print(json.load(sys.stdin)['object']['sha'])")

# Force update if different
if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
    curl -X PATCH -H "Authorization: token $TOKEN" -H "Content-Type: application/json" \
        -d "{\"sha\":\"$LOCAL_SHA\",\"force\":true}" \
        "https://api.github.com/repos/$OWNER/$REPO/git/refs/heads/$BRANCH"
fi
```

**When to use this instead of git push:**
- git push hangs >30s with timeout exit 124
- 401/403 despite valid PAT in credentials
- Need quick force-push without credential retry loops
- Token has `repo` scope but git auth cache is slow/expired
