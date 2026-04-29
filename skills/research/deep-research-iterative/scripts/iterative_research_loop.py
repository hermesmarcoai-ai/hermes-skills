#!/usr/bin/env python3
"""
Iterative Deep Research Loop
Research → Synthesize → Gap Analysis → Research (refined)

Usage:
    from iterative_research_loop import IterativeResearchLoop
    
    loop = IterativeResearchLoop(topic="your research topic")
    results = loop.run(max_passes=5)
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class GapSeverity(Enum):
    CRITICAL = "Critical"
    IMPORTANT = "Important"
    MINOR = "Minor"


class GapType(Enum):
    FACTUAL_UNKNOWN = "Factual unknown"
    CONTRADICTORY_EVIDENCE = "Contradictory evidence"
    OUTDATED_INFO = "Outdated info"
    MISSING_PERSPECTIVE = "Missing perspective"


class Researchability(Enum):
    YES = "Yes (online sources exist)"
    NO = "No (requires expert consultation)"
    PARTIAL = "Partial"


@dataclass
class Gap:
    description: str
    severity: GapSeverity
    gap_type: GapType
    researchable: Researchability
    question: str
    answered: bool = False
    answer: Optional[str] = None


@dataclass
class IterationState:
    pass_num: int = 1
    topic: str = ""
    research_findings: list = field(default_factory=list)
    syntheses: list = field(default_factory=list)
    gaps: list = field(default_factory=list)
    stop_reason: Optional[str] = None


class IterativeResearchLoop:
    """
    Iterative deep research workflow manager.
    
    Cycles through: RESEARCH → SYNTHESIZE → GAP_ANALYSIS → RESEARCH (refined)
    """
    
    def __init__(self, topic: str, max_passes: int = 5):
        self.topic = topic
        self.max_passes = max_passes
        self.state = IterationState(topic=topic)
    
    def set_deep_research_model(self):
        """Configure Perplexity Sonar Deep Research model."""
        os.environ["AUXILIARY_WEB_EXTRACT_MODEL"] = "perplexity/sonar-deep-research"
        os.environ["AUXILIARY_WEB_EXTRACT_PROVIDER"] = "openrouter"
        os.environ["AUXILIARY_WEB_EXTRACT_BASE_URL"] = "https://openrouter.ai/api/v1"
    
    def reset_model(self):
        """Reset to standard model after research completion."""
        os.environ["AUXILIARY_WEB_EXTRACT_MODEL"] = "perplexity/sonar-pro"
        os.environ["AUXILIARY_WEB_EXTRACT_PROVIDER"] = "openrouter"
        os.environ["AUXILIARY_WEB_EXTRACT_BASE_URL"] = "https://openrouter.ai/api/v1"
    
    def research(self, topic: str, refined_topic: Optional[str] = None) -> str:
        """
        Phase 1: Conduct research using deep research model.
        
        Args:
            topic: Original research topic
            refined_topic: Optional refined focus based on gaps
            
        Returns:
            Research findings as string
        """
        self.set_deep_research_model()
        
        if refined_topic:
            prompt = f"""
Follow-up research to address specific gaps:

Original topic: {topic}
Refined focus: {refined_topic}

Conduct targeted searches to fill identified knowledge gaps.
"""
        else:
            prompt = f"""
Research topic: {topic}

Provide a comprehensive overview covering:
1. Core concepts and definitions
2. Current state of knowledge
3. Key players, developments, or perspectives
4. Recent innovations or findings (last 1-2 years)
5. Controversies or debates
6. Practical applications or implications

Search multiple sources and synthesize findings.
"""
        
        # TODO: Call web_extract with the prompt
        # findings = web_extract(prompt)
        return f"[Research findings for pass {self.state.pass_num}]"
    
    def synthesize(self, findings: str) -> str:
        """
        Phase 2: Synthesize research findings.
        
        Args:
            findings: Raw research findings
            
        Returns:
            Synthesized summary
        """
        prompt = f"""
Synthesize the following research findings into a structured summary:

{findings}

Organize into:
- Key findings (top 5-7)
- Supporting evidence
- Conflicting viewpoints or gaps in evidence
- Emerging trends or developments

Format as a clear, hierarchical document.
"""
        
        # TODO: Call web_extract with synthesis prompt
        # return web_extract(prompt)
        return f"[Synthesis for pass {self.state.pass_num}]"
    
    def gap_analysis(self, synthesized_content: str) -> list[Gap]:
        """
        Phase 3: Identify knowledge gaps.
        
        Args:
            synthesized_content: Synthesized research content
            
        Returns:
            List of identified gaps
        """
        prompt = f"""
Analyze the synthesized research and identify knowledge gaps:

{synthesized_content}

For each gap, rate:
- Severity: Critical / Important / Minor
- Type: Factual unknown, contradictory evidence, outdated info, or missing perspective
- Researchable: Yes (online sources exist) / No (requires expert consultation) / Partial

Output a ranked list of gaps by severity, with specific questions to answer in next pass.
"""
        
        # TODO: Call web_extract with gap analysis prompt
        # analysis = web_extract(prompt)
        # Parse into Gap objects
        return []
    
    def should_continue(self, gaps: list[Gap]) -> tuple[bool, Optional[str]]:
        """
        Determine if research loop should continue.
        
        Returns:
            (should_continue, stop_reason)
        """
        if not gaps:
            return False, "No gaps identified - topic fully covered"
        
        critical_gaps = [g for g in gaps if g.severity == GapSeverity.CRITICAL]
        important_gaps = [g for g in gaps if g.severity == GapSeverity.IMPORTANT]
        researchable = [g for g in gaps if g.researchable in (Researchability.YES, Researchability.PARTIAL) and not g.answered]
        
        # Stop if no researchable critical/important gaps remain
        remaining_important = [g for g in researchable if g.severity in (GapSeverity.CRITICAL, GapSeverity.IMPORTANT)]
        if not remaining_important:
            return False, "Gap saturation - all critical/important gaps answered"
        
        # Stop at max passes
        if self.state.pass_num >= self.max_passes:
            return False, f"Max passes ({self.max_passes}) reached"
        
        return True, None
    
    def run(self, max_passes: Optional[int] = None) -> dict:
        """
        Run the iterative research loop.
        
        Args:
            max_passes: Override max passes (default: self.max_passes)
            
        Returns:
            Final research results with iteration log
        """
        max_passes = max_passes or self.max_passes
        self.set_deep_research_model()
        
        try:
            while self.state.pass_num <= max_passes:
                # Phase 1: Research
                refined_topic = None
                if self.state.gaps:
                    refined_topic = self._build_refined_topic()
                
                findings = self.research(self.topic, refined_topic)
                self.state.research_findings.append(findings)
                
                # Phase 2: Synthesize
                synthesis = self.synthesize(findings)
                self.state.syntheses.append(synthesis)
                
                # Phase 3: Gap Analysis
                gaps = self.gap_analysis(synthesis)
                self.state.gaps = gaps
                
                # Check continuation
                should_continue, stop_reason = self.should_continue(gaps)
                if not should_continue:
                    self.state.stop_reason = stop_reason
                    break
                
                self.state.pass_num += 1
            
            return self._build_final_results()
        
        finally:
            self.reset_model()
    
    def _build_refined_topic(self) -> str:
        """Build refined topic from unanswered gaps."""
        unanswered = [g for g in self.state.gaps if not g.answered]
        if not unanswered:
            return self.topic
        
        gap_questions = "\n".join([f"- {g.question}" for g in unanswered[:5]])
        return f"{self.topic}\n\nFocus on addressing these gaps:\n{gap_questions}"
    
    def _build_final_results(self) -> dict:
        """Build final output structure."""
        return {
            "topic": self.topic,
            "total_passes": self.state.pass_num,
            "stop_reason": self.state.stop_reason,
            "final_synthesis": self.state.syntheses[-1] if self.state.syntheses else None,
            "all_findings": self.state.research_findings,
            "all_syntheses": self.state.syntheses,
            "gaps": [
                {
                    "description": g.description,
                    "severity": g.severity.value,
                    "type": g.gap_type.value,
                    "researchable": g.researchable.value,
                    "answered": g.answered,
                    "answer": g.answer
                }
                for g in self.state.gaps
            ]
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python iterative_research_loop.py <topic>")
        print("       python iterative_research_loop.py --interactive")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    loop = IterativeResearchLoop(topic=topic)
    results = loop.run()
    print(f"Research complete: {results['total_passes']} passes")
    print(f"Stop reason: {results['stop_reason']}")
