import re

# Patterns for vague phrases and mapping to enriched suggestion templates
VAGUE_PATTERNS = {
    r"\bled \w+ projects\b": (
        "Replace 'led many projects' with a quantified statement. "
        "E.g., 'Led 5 cross-functional projects, delivering a 20% increase in system efficiency.'"
    ),
    r"\bgreat communicator\b": (
        "Replace 'great communicator' with specific context and outcome. "
        "E.g., 'Facilitated weekly stakeholder meetings, improving cross-team collaboration by 30%.'"
    ),
    r"\bresponsible for\b": (
        "Replace 'responsible for' with active accomplishments. "
        "E.g., 'Managed a team of 4 engineers to deploy feature X, reducing delivery time by 25%.'"
    ),
    r"\bexperienced in?\b": (
        "Clarify experience scope and outcome. "
        "E.g., '3 years of experience in Python development, automating tasks that cut processing time by 40%.'"
    ),
    r"\benthusiastic about\b": (
        "Replace 'enthusiastic about' with a concrete project. "
        "E.g., 'Spearheaded open-source contributions to XYZ library, increasing adoption by 15%.'"
    ),
    r"\bstrong background in\b": (
        "Specify background details and impact. "
        "E.g., 'Strong background in data analysis, generating insights that improved sales forecasting accuracy by 10%.'"
    ),
    r"\bproven track record\b": (
        "Replace 'proven track record' with examples and metrics. "
        "E.g., 'Achieved 95% on-time delivery rate over 12 projects in the last 2 years.'"
    ),
    r"\bteam player\b": (
        "Illustrate collaborative achievements. "
        "E.g., 'Collaborated with UX and backend teams to launch feature Y, boosting user engagement by 25%.'"
    ),
    r"\bdetail[- ]?oriented\b": (
        "Add evidence of attention to detail. "
        "E.g., 'Reviewed and improved QA processes, reducing defects by 30%.'"
    ),
    r"\bresults?[- ]?driven\b": (
        "Support 'results-driven' with outcomes. "
        "E.g., 'Delivered a 50% increase in customer satisfaction scores through process optimization.'"
    ),
    r"\bhandled\b": (
        "Specify scope and outcomes of 'handled'. "
        "E.g., 'Handled deployment of 50+ microservices, achieving zero downtime.'"
    ),
    r"\bparticipated in\b": (
        "Replace 'participated in' with leadership or contribution. "
        "E.g., 'Contributed core algorithms to Project Z, reducing computation time by 35%.'"
    ),
    r"\binvolved in\b": (
        "Clarify role and impact in 'involved in'. "
        "E.g., 'Involved in strategic planning for product launch, resulting in 20% revenue growth.'"
    ),
    r"\bextensive experience\b": (
        "Quantify 'extensive experience' with years and achievements. "
        "E.g., 'Over 5 years of experience in cloud architecture, designing systems serving 100K+ users.'"
    ),
    r"\bstrong leadership\b": (
        "Demonstrate leadership results. "
        "E.g., 'Led a cross-functional team of 6, delivering Project A two weeks ahead of schedule.'"
    ),
    r"\bpassionate about\b": (
        "Show passion through action. "
        "E.g., 'Passionate contributor to open-source community, mentoring 10+ developers.'"
    ),
    r"\bfast learner\b": (
        "Highlight learning outcomes. "
        "E.g., 'Quickly mastered React.js, reducing onboarding time by 50% and shipping feature B.'"
    ),
    r"\bexcellent communication skills\b": (
        "Provide communication context. "
        "E.g., 'Led client presentations, securing 3 new contracts worth $200K.'"
    ),
    r"\bhighly skilled\b": (
        "Detail skill level and outcomes. "
        "E.g., 'Highly skilled in SQL, optimizing queries that improved report generation time by 60%.'"
    ),
    r"\bstrategic thinker\b": (
        "Demonstrate strategy with results. "
        "E.g., 'Developed 3-year product roadmap, resulting in 15% annual revenue growth.'"
    )
}

# Compile patterns
COMPILED_VAGUE = [(re.compile(pat, re.IGNORECASE), suggestion)
                  for pat, suggestion in VAGUE_PATTERNS.items()]


def flag_vague_bullets(resume_text: str):
    """
    Identify vague bullets and provide enriched, factual suggestions.

    Returns a list of dicts with:
      - bullet: original text
      - issues: matched vague phrases
      - suggestion: enriched, example rewrite template
    """
    flagged = []
    for line in resume_text.splitlines():
        line = line.strip()
        if not line.startswith('-'):
            continue
        bullet = line.lstrip('-').strip()
        issues = []
        suggestion = None
        for pattern, tmpl in COMPILED_VAGUE:
            match = pattern.search(bullet)
            if match:
                issues.append(match.group(0))
                suggestion = tmpl  # last matched template
        if issues:
            flagged.append({
                'bullet': bullet,
                'issues': issues,
                'suggestion': suggestion
            })
    return flagged

# Example usage
if __name__ == '__main__':
    sample = '''
- Led many projects to improve system performance.
- Great communicator and team player in agile settings.
- Responsible for data migration across platforms.
- Fast learner who picks up new tools quickly.
'''
    for item in flag_vague_bullets(sample):
        print(f"Bullet: {item['bullet']}")
        print(f"Issues: {item['issues']}")
        print(f"Suggestion: {item['suggestion']}\n")
