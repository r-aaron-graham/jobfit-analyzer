import re
import random

# Precompiled regex patterns for efficiency
METRICS_PATTERN = re.compile(r"\b\d+[\d,.%+]*\b")
KEYWORD_PATTERN = re.compile(r"\b[a-zA-Z]{4,}\b")
SPLIT_PATTERN = re.compile(r",|;|\.| and ")
VERB_PATTERN = re.compile(r"\b(\w+ed|\w+s)\b.*", re.IGNORECASE)

# Pools of STAR verbs
STAR_VERBS = [
    'Led', 'Guided', 'Directed', 'Executed', 'Coordinated', 'Engineered',
    'Implemented', 'Optimized', 'Spearheaded', 'Designed', 'Built',
    'Streamlined', 'Enhanced', 'Orchestrated'
]

# File: resume_star_enhancer.py
# Renamed from resume_rewriter to clarify STAR enhancement focus

def extract_metrics(bullet: str) -> str:
    """Return comma-separated numeric metrics."""
    return ', '.join(METRICS_PATTERN.findall(bullet))


def extract_keywords(text: str) -> set:
    """Return set of lowercase tokens length>=4."""
    return {tok.lower() for tok in KEYWORD_PATTERN.findall(text)}


def format_star_bullet(bullet: str, jd_keywords: set) -> str:
    """
    Convert a single bullet into STAR format with:
      - Preceding 'Situation/Task', 'Action', 'Result' labels
      - Active STAR verb
      - Preserved metrics
      - Highlighted overlapping keywords
    """
    metrics = extract_metrics(bullet)
    bullet_kw = extract_keywords(bullet)
    highlights = bullet_kw & jd_keywords
    highlight_str = f" Highlights: {', '.join(highlights)}" if highlights else ''

    parts = [p.strip() for p in SPLIT_PATTERN.split(bullet) if p.strip()]
    situation = parts[0] if parts else ''
    result = parts[-1] if len(parts) > 1 else metrics

    # Extract action phrase
    match = VERB_PATTERN.match(situation)
    action_phrase = match.group(0) if match else situation

    verb = random.choice(STAR_VERBS)
    return (
        f"Situation/Task: {situation}. "
        f"Action: {verb} by {action_phrase}. "
        f"Result: {result}.{highlight_str}"
    )


def enhance_with_star(resume: str, job_desc: str) -> str:
    """
    Enhance resume bullets using STAR format:
      - Preserve numeric facts
      - Improve verbs
      - Highlight job-specific skills
      - Maintain human-like style
    """
    jd_keywords = extract_keywords(job_desc)
    enhanced = []
    for line in resume.splitlines():
        stripped = line.strip()
        if not stripped.startswith('-'):
            continue
        bullet = stripped.lstrip('-').strip()
        star = format_star_bullet(bullet, jd_keywords)
        enhanced.append(f"- {star}")
    return '\n'.join(enhanced)

# Example usage
if __name__ == '__main__':
    sample = '''
- Engineered Python modules boosting answer relevance 18% and reducing errors.
- Labeled 10K+ records cutting prep time by 40% and improving accuracy.
'''
    jd = "Seeking a proactive Python engineer skilled in data labeling and accuracy optimization."
    print(enhance_with_star(sample, jd))
