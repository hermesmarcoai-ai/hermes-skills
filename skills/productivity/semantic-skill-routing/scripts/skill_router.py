#!/usr/bin/env python3
"""
Semantic Skill Router

Load all skills from ~/.hermes/skills/, build a TF-IDF vectorizer,
and find the most relevant skills for a given query.

Usage:
    python skill_router.py "review my code changes"
    python skill_router.py "schedule a meeting" --top-k 5
    python skill_router.py "deploy to prod" --threshold 0.2
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Default paths
DEFAULT_SKILLS_DIR = Path.home() / ".hermes" / "skills"
DEFAULT_THRESHOLD = 0.1
DEFAULT_TOP_K = 3


class SkillRouter:
    """TF-IDF based skill router."""
    
    def __init__(self, skills_dir: str = None, threshold: float = DEFAULT_THRESHOLD, top_k: int = DEFAULT_TOP_K):
        self.skills_dir = Path(skills_dir) if skills_dir else DEFAULT_SKILLS_DIR
        self.threshold = threshold
        self.top_k = top_k
        self._skills_cache = None
        self._vectorizer = None
        self._tfidf_matrix = None
        self._skillTexts = []
        self._skillNames = []
        self._skillReasons = {}
    
    def _parse_frontmatter(self, content: str) -> dict:
        """Extract YAML frontmatter from SKILL.md content."""
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            frontmatter = {}
            for line in match.group(1).strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    value = value.strip().strip('"').strip("'")
                    frontmatter[key.strip()] = value
            body = content[match.end():].strip()
            return frontmatter, body
        return {}, content
    
    def _load_skill(self, skill_path: Path) -> dict:
        """Load a single skill's SKILL.md and extract relevant info."""
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            return None
        
        try:
            content = skill_md.read_text(encoding='utf-8')
            frontmatter, body = self._parse_frontmatter(content)
            
            name = frontmatter.get('name', skill_path.name)
            description = frontmatter.get('description', '')
            
            # Combine name + description + first 200 chars of body for matching
            combined_text = f"{name} {description} {body[:500]}".lower()
            
            # Generate reason template
            reason = f"Matches skill '{name}' based on keyword overlap"
            
            return {
                'name': name,
                'path': str(skill_path),
                'description': description,
                'text': combined_text,
                'reason_template': reason
            }
        except Exception as e:
            print(f"Warning: Failed to load {skill_md}: {e}", file=sys.stderr)
            return None
    
    def _load_all_skills(self) -> list:
        """Load all skills from the skills directory."""
        if self._skills_cache is not None:
            return self._skills_cache
        
        skills = []
        if not self.skills_dir.exists():
            print(f"Warning: Skills directory not found: {self.skills_dir}", file=sys.stderr)
            return skills
        
        # Scan two levels deep: category/skill-name/SKILL.md
        for category_dir in self.skills_dir.iterdir():
            if not category_dir.is_dir():
                continue
            
            # Check if this is a direct skill directory (has SKILL.md)
            if (category_dir / "SKILL.md").exists():
                skill = self._load_skill(category_dir)
                if skill:
                    skills.append(skill)
            
            # Otherwise, scan for skill subdirectories
            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                skill = self._load_skill(skill_dir)
                if skill:
                    skills.append(skill)
        
        self._skills_cache = skills
        return skills
    
    def _extract_keywords(self, text: str) -> set:
        """Extract simple keywords from text (lowercased, alphanumeric)."""
        words = re.findall(r'\b[a-z][a-z0-9]{2,}\b', text.lower())
        # Common stopwords to filter
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 
                     'has', 'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been',
                     'from', 'with', 'this', 'that', 'these', 'those', 'your', 'their'}
        return set(w for w in words if w not in stopwords)
    
    def _keyword_overlap_score(self, query: str, skill_text: str) -> float:
        """Compute simple keyword overlap score (fallback if no sklearn)."""
        query_kw = self._extract_keywords(query)
        skill_kw = self._extract_keywords(skill_text)
        if not query_kw or not skill_kw:
            return 0.0
        overlap = len(query_kw & skill_kw)
        return overlap / len(query_kw)
    
    def _build_tfidf_index(self):
        """Build TF-IDF index from all skills."""
        skills = self._load_all_skills()
        if not skills:
            return
        
        self._skillTexts = [s['text'] for s in skills]
        self._skillNames = [s['name'] for s in skills]
        self._skillReasons = {s['name']: s['reason_template'] for s in skills}
        
        if HAS_SKLEARN and len(skills) > 1:
            self._vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english',
                lowercase=True
            )
            self._tfidf_matrix = self._vectorizer.fit_transform(self._skillTexts)
        else:
            self._vectorizer = None
            self._tfidf_matrix = None
    
    def _score_query_tfidf(self, query: str) -> list:
        """Score query against all skills using TF-IDF."""
        skills = self._load_all_skills()
        
        if not skills:
            return []
        
        # Rebuild index if needed
        if self._tfidf_matrix is None:
            self._build_tfidf_index()
        
        query_lower = query.lower()
        
        # Check for exact skill name matches first (boost them)
        boosted_scores = {}
        for i, name in enumerate(self._skillNames):
            name_lower = name.lower().replace('-', ' ').replace('_', ' ')
            query_words = set(query_lower.split())
            name_words = set(name_lower.split())
            
            # Check if query contains the skill name or vice versa
            if name_lower in query_lower or query_lower in name_lower:
                boosted_scores[i] = 1.0
            elif name_words & query_words:  # Partial word match
                boosted_scores[i] = 0.8
        
        if HAS_SKLEARN and self._tfidf_matrix is not None:
            query_vec = self._vectorizer.transform([query_lower])
            tfidf_scores = cosine_similarity(query_vec, self._tfidf_matrix).flatten()
            
            for i in range(len(tfidf_scores)):
                base_score = float(tfidf_scores[i])
                # Apply boost if exists
                boosted = boosted_scores.get(i, base_score)
                boosted_scores[i] = max(base_score, boosted) if i in boosted_scores else base_score
        else:
            # Fallback: keyword overlap
            for i, skill_text in enumerate(self._skillTexts):
                base_score = self._keyword_overlap_score(query, skill_text)
                boosted_scores[i] = max(base_score, boosted_scores.get(i, 0))
        
        return [(i, score) for i, score in boosted_scores.items()]
    
    def _generate_reason(self, query: str, skill_name: str, score: float) -> str:
        """Generate a human-readable reason for the match."""
        query_lower = query.lower()
        skill_lower = skill_name.lower().replace('-', ' ').replace('_', ' ')
        
        # Find matching keywords
        query_kw = self._extract_keywords(query)
        skill_kw = self._extract_keywords(skill_lower)
        overlap = query_kw & skill_kw
        
        if overlap:
            return f"Query contains '{', '.join(list(overlap)[:3])}' which matches key terms in this skill"
        elif score > 0.8:
            return f"Strong semantic match (score: {score:.2f})"
        else:
            return f"Moderate semantic match based on TF-IDF similarity"
    
    def route(self, query: str, top_k: int = None, threshold: float = None) -> list:
        """
        Route a query to the most relevant skills.
        
        Args:
            query: The task description to route
            top_k: Number of results to return (default: self.top_k)
            threshold: Minimum score threshold (default: self.threshold)
        
        Returns:
            List of dicts: [{"skill": name, "score": 0.xx, "reason": "..."}]
        """
        top_k = top_k or self.top_k
        threshold = threshold or self.threshold
        
        start_time = time.time()
        
        # Score the query
        scored = self._score_query_tfidf(query)
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Take top-k and filter by threshold
        results = []
        for idx, score in scored[:top_k]:
            if score < threshold:
                continue
            skill_name = self._skillNames[idx]
            results.append({
                'skill': skill_name,
                'score': round(score, 3),
                'reason': self._generate_reason(query, skill_name, score)
            })
        
        elapsed = (time.time() - start_time) * 1000
        if elapsed > 500:
            print(f"Warning: Routing took {elapsed:.0f}ms (target: <500ms)", file=sys.stderr)
        
        return results
    
    def route_json(self, query: str, top_k: int = None, threshold: float = None) -> str:
        """Route query and return results as JSON string."""
        results = self.route(query, top_k, threshold)
        return json.dumps(results, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Semantic Skill Router')
    parser.add_argument('query', nargs='*', help='Query string to route')
    parser.add_argument('--top-k', type=int, default=DEFAULT_TOP_K, help=f'Number of results (default: {DEFAULT_TOP_K})')
    parser.add_argument('--threshold', type=float, default=DEFAULT_THRESHOLD, help=f'Score threshold (default: {DEFAULT_THRESHOLD})')
    parser.add_argument('--skills-dir', type=str, default=None, help=f'Skills directory (default: {DEFAULT_SKILLS_DIR})')
    parser.add_argument('--json', action='store_true', help='Output raw JSON')
    parser.add_argument('--verbose', action='store_true', help='Show timing info')
    
    args = parser.parse_args()
    
    if not args.query:
        print("Error: Query required", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    query = ' '.join(args.query)
    
    router = SkillRouter(
        skills_dir=args.skills_dir,
        threshold=args.threshold,
        top_k=args.top_k
    )
    
    start = time.time()
    results = router.route(query)
    elapsed = (time.time() - start) * 1000
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if results:
            print(f"\n🎯 Top {len(results)} skill matches for: \"{query}\"\n")
            print(f"{'Rank':<6} {'Skill':<35} {'Score':<8} {'Reason'}")
            print("-" * 90)
            for i, r in enumerate(results, 1):
                print(f"{i:<6} {r['skill']:<35} {r['score']:<8.3f} {r['reason']}")
            print("-" * 90)
        else:
            print(f"\n❌ No skills matched '{query}' above threshold {args.threshold}")
    
    if args.verbose:
        print(f"\n⏱️  Routing completed in {elapsed:.1f}ms")
    
    return 0 if results else 1


if __name__ == '__main__':
    sys.exit(main())
