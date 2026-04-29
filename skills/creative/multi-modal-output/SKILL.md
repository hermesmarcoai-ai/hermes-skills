---
name: multi-modal-output
description: Generate video, animation, and PDF output directly. Integrates content-factory (video pipeline), Remotion (animations), and pandoc/Python PDF generation. Use when users request: "make me a video", "create an animation", "generate a PDF report", "render this as video", "export to PDF", "create an animated explainer", or any task requiring direct output in video/animation/PDF format.
version: 1.0.0
category: creative
trigger: multi-modal-output
---

# Multi-Modal Output Generator

Generate video, animation, and PDF output directly — no separate setup required. Three integrated pipelines sharing a unified project structure.

## System Overview

```
INPUT --> [Video Pipeline | Animation Pipeline | PDF Pipeline] --> OUTPUT
              |                   |                  |
         content-factory      Remotion         pandoc/Python
```

## When to Use

| Request | Pipeline | Skill Reference |
|---------|----------|-----------------|
| "Make me a video" | Video | content-factory pipeline |
| "Create an animation" | Animation | Remotion (this skill) |
| "Generate a PDF report" | PDF | pandoc/Python |
| "Render this as a video" | Video | content-factory |
| "Export to PDF" | PDF | pandoc/Python |
| "Animated explainer" | Animation | Remotion |
| "Logo animation" | Animation | Remotion |
| "Data report PDF" | PDF | pandoc/Python |
| "Social media video" | Video | content-factory |

## Project Structure

```
~/multi-modal-output/
├── content/              # Input content (scripts, data, assets)
│   ├── script.md
│   └── assets/
├── output/               # Generated output
│   ├── video/
│   ├── animation/
│   └── pdf/
├── video/                # content-factory video project
│   └── script.py
├── animation/            # Remotion project
│   ├── src/
│   │   └── index.ts
│   └── package.json
└── pdf/                  # pandoc/Python project
    ├── template.md
    └── generate.py
```

## Pipeline 1: Video (content-factory)

Use the content-factory architecture for scripted video production.

### Quick Start

```bash
mkdir -p ~/multi-modal-output/video
cd ~/multi-modal-output/video

# Write script
cat > script.py << 'EOF'
"""
Content Factory Video Script
"""
import subprocess
import json
from pathlib import Path

class VideoPipeline:
    def __init__(self, project_dir="."):
        self.project_dir = Path(project_dir)
        
    def generate_thumbnail(self, prompt: str, output_path: str):
        """Generate thumbnail using Flux API or DALL-E"""
        # Use BFL FLUX API via bfl-api skill
        # or fallback to placeholder
        pass
        
    def render_video(self, script_path: str, output_path: str):
        """Render video from script"""
        # Use ffmpeg with source frames
        pass
EOF

# For full content-factory integration, load the skill
# skill: content-factory
```

### Video Workflow

```bash
# Step 1: Create project
cd ~/multi-modal-output/video

# Step 2: Generate thumbnail
python3 script.py --generate-thumbnail "video topic"

# Step 3: Render video
python3 script.py --render --script script.md --output output.mp4
```

## Pipeline 2: Animation (Remotion)

Use Remotion for programmatic animations with React-like components.

### Prerequisites

- Node.js 20+
- npx
- FFmpeg
- Chromium/Chrome

### Quick Start

```bash
# Step 1: Create Remotion project
cd ~/multi-modal-output/animation
npx create-video@latest . --template hello

# Step 2: Edit src/index.ts
# Write your animation components

# Step 3: Preview
npx remotion preview

# Step 4: Render
npx remotion render out animation.mp4
```

### Animation Reference

| File | Purpose |
|------|---------|
| `src/index.ts` | Entry point - root component |
| `src/HelloWorld/index.ts` | Example animation |
| `package.json` | Dependencies |
| `remotion.config.ts` | Configuration |

### Common Remotion Patterns

```typescript
// Basic animation structure
import { AbsoluteFill, Sequence, useCurrentFrame } from 'remotion';

const MyAnimation: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = Math.min(frame / 30, 1);
  
  return (
    <AbsoluteFill style={{ backgroundColor: '#1a1a2e' }}>
      <Sequence from={0} duration={60}>
        <div style={{ opacity, fontSize: 48, color: 'white' }}>
          Hello World
        </div>
      </Sequence>
    </AbsoluteFill>
  );
};
```

### Full Remotion Setup (from remotion-vps-setup skill)

```bash
# Install system deps
sudo apt update && sudo apt install -y ffmpeg chromium-browser

# Install Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20

# Create project
cd ~/multi-modal-output/animation
npx create-video@latest . --template hello

# Render with specific quality
npx remotion render HelloWorld out/video.mp4 --quality=0.8
```

## Pipeline 3: PDF (pandoc/Python)

Generate PDFs using pandoc with LaTeX or Python with ReportLab/WeasyPrint.

### Method A: pandoc (Markdown to PDF)

```bash
# Install pandoc + LaTeX
sudo apt install -y pandoc texlive-full

# Create markdown template
cat > template.md << 'EOF'
---
title: "Report Title"
author: "Author Name"
date: "`date +%Y-%m-%d`"
geometry: margin=1in
fontsize: 11pt
output:
  pdf_document:
    latex_engine: xelatex
---

# Section 1

Content here.

## Subsection 1.1

More content.

EOF

# Convert to PDF
pandoc template.md -o output.pdf
```

### Method B: Python PDF Generation

#### WeasyPrint (HTML to PDF)

```bash
pip install weasyprint
```

```python
#!/usr/bin/env python3
"""
PDF Generator using WeasyPrint
"""
from pathlib import Path
from weasyprint import HTML, CSS

def generate_pdf(html_path: str, output_path: str, css: str = None):
    """Generate PDF from HTML"""
    html = HTML(filename=html_path)
    stylesheets = [CSS(filename=css)] if css else []
    html.write_pdf(output_path, stylesheets=stylesheets)

def html_from_template(template_path: str, context: dict) -> str:
    """Render HTML template with context"""
    with open(template_path) as f:
        content = f.read()
    for key, value in context.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content

if __name__ == "__main__":
    # Example usage
    html = """
    <html>
    <head><style>
        body { font-family: Arial; margin: 40px; }
        h1 { color: #1a1a2e; }
    </style></head>
    <body>
        <h1>{{title}}</h1>
        <p>{{content}}</p>
    </body>
    </html>
    """
    HTML(string=html).write_pdf("output.pdf")
```

#### ReportLab (Pure Python)

```bash
pip install reportlab
```

```python
#!/usr/bin/env python3
"""
PDF Generator using ReportLab
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor

def create_pdf(output_path: str, title: str, sections: list):
    """Create a styled PDF report"""
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title2',
                              fontName='Helvetica-Bold',
                              fontSize=24,
                              textColor=HexColor('#1a1a2e'),
                              spaceAfter=30))
    styles.add(ParagraphStyle(name='Heading2',
                              fontName='Helvetica-Bold',
                              fontSize=16,
                              textColor=HexColor('#16213e'),
                              spaceAfter=12,
                              spaceBefore=20))
    styles.add(ParagraphStyle(name='Body2',
                              fontName='Helvetica',
                              fontSize=11,
                              leading=16,
                              textColor=HexColor('#333333'),
                              spaceAfter=12))
    
    story = []
    story.append(Paragraph(title, styles['Title2']))
    story.append(Spacer(1, 0.3*inch))
    
    for section in sections:
        story.append(Paragraph(section['heading'], styles['Heading2']))
        story.append(Paragraph(section['content'], styles['Body2']))
    
    doc.build(story)
    return output_path

if __name__ == "__main__":
    sections = [
        {'heading': 'Introduction', 'content': 'This is the introduction.'},
        {'heading': 'Methods', 'content': 'These are the methods used.'},
        {'heading': 'Results', 'content': 'These are the results.'},
        {'heading': 'Conclusion', 'content': 'This is the conclusion.'},
    ]
    create_pdf("report.pdf", "Research Report", sections)
```

## Quick Command Reference

### Video

```bash
# Generate thumbnail
python3 script.py --generate-thumbnail "topic"

# Render video
python3 script.py --render --script script.md --output video.mp4
```

### Animation

```bash
# Preview in browser
npx remotion preview

# Render to MP4
npx remotion render SceneName output.mp4

# Render to GIF
npx remotion render SceneName output.gif
```

### PDF

```bash
# pandoc conversion
pandoc input.md -o output.pdf

# WeasyPrint
python3 generate.py --input template.html --output report.pdf

# ReportLab
python3 generate.py --title "Report" --output report.pdf
```

## Unified Interface Script

Create `~/multi-modal-output/generate.py` for unified access:

```python
#!/usr/bin/env python3
"""
Multi-Modal Output Generator
Unified interface for video, animation, and PDF generation
"""
import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent

def generate_video(script: str, output: str):
    """Generate video using content-factory pipeline"""
    print(f"Generating video: {output}")
    # Add video generation logic here
    pass

def generate_animation(scene: str, output: str):
    """Generate animation using Remotion"""
    print(f"Generating animation: {output}")
    subprocess.run([
        "npx", "remotion", "render", scene, output
    ], cwd=PROJECT_DIR / "animation", check=True)

def generate_pdf(input_file: str, output: str, engine: str = "pandoc"):
    """Generate PDF using pandoc or Python"""
    print(f"Generating PDF: {output}")
    if engine == "pandoc":
        subprocess.run([
            "pandoc", input_file, "-o", output
        ], check=True)
    else:
        subprocess.run([
            "python3", str(PROJECT_DIR / "pdf" / "generate.py"),
            "--input", input_file,
            "--output", output
        ], check=True)

def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Output Generator")
    parser.add_argument("--type", choices=["video", "animation", "pdf"],
                       required=True, help="Output type")
    parser.add_argument("--input", help="Input file")
    parser.add_argument("--output", required=True, help="Output file")
    parser.add_argument("--engine", choices=["pandoc", "weasyprint", "reportlab"],
                       default="pandoc", help="PDF engine")
    
    args = parser.parse_args()
    
    if args.type == "video":
        generate_video(args.input, args.output)
    elif args.type == "animation":
        generate_animation(args.input or "HelloWorld", args.output)
    elif args.type == "pdf":
        generate_pdf(args.input, args.output, args.engine)

if __name__ == "__main__":
    main()
```

Usage:

```bash
# Generate video
python3 generate.py --type video --input script.md --output output/video.mp4

# Generate animation
python3 generate.py --type animation --input MyScene --output output/animation.mp4

# Generate PDF (pandoc)
python3 generate.py --type pdf --input content.md --output output/report.pdf

# Generate PDF (WeasyPrint)
python3 generate.py --type pdf --input template.html --output output/report.pdf --engine weasyprint
```

## Skills Reference

| Related Skill | Purpose |
|-------------|---------|
| `content-factory` | Full video pipeline architecture |
| `remotion-vps-setup` | Remotion installation guide |
| `ascii-video` | ASCII art video production |
| `manim-video` | Mathematical animation production |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Remotion preview fails | `sudo apt install -y chromium-browser` |
| Pandoc PDF fails | `sudo apt install -y texlive-full` |
| WeasyPrint fails | `sudo apt install -y libpango-1.0-0 libcairo2` |
| FFmpeg not found | `sudo apt install -y ffmpeg` |
| Node version error | `nvm install 20 && nvm use 20` |
