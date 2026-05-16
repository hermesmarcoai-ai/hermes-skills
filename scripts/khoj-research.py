#!/usr/bin/env python3
"""
Khoj AI Second Brain - Hermes Integration Script
Quick research using Khoj API. Saves findings to Obsidian.
"""

import sys, os, requests
from datetime import datetime

KHOJ_API_URL = os.environ.get("KHOJ_API_URL", "https://app.khoj.dev/api")
KHOJ_API_KEY = os.environ.get("KHOJ_API_KEY", "")
OBSIDIAN_VAULT = os.path.expanduser("~/Obsidian-Vault")

def khoj_chat(query):
    headers = {"Content-Type": "application/json"}
    if KHOJ_API_KEY:
        headers["Authorization"] = f"Bearer {KHOJ_API_KEY}"
    try:
        r = requests.post(f"{KHOJ_API_URL}/chat", json={"q": query, "stream": False}, headers=headers, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: khoj-research.py <query> [--save]")
        sys.exit(1)
    query = sys.argv[1]
    save = "--save" in sys.argv
    print(f"🔍 Researching: {query}")
    result = khoj_chat(query)
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        print("💡 Set KHOJ_API_KEY for authenticated requests")
    else:
        print(f"\n📝 Response: {result.get('response', result)}")
        if save:
            date = datetime.now().strftime('%Y-%m-%d')
            path = f"{OBSIDIAN_VAULT}/research/{date}/{query[:30].replace(' ','-')}.md"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(f"# Research: {query}\nDate: {date}\n\n## Response\n{result.get('response', result)}\n")
            print(f"💾 Saved to: {path}")

if __name__ == "__main__":
    main()