import json
import re
from collections import Counter

try:
    from textblob import TextBlob
except ImportError:
    raise ImportError("Please install textblob: pip install textblob")

# Predefined positive/negative tone keywords (example)
POSITIVE_TONE = set(["collaborative", "innovative", "passionate", "motivated", "driven"])
NEGATIVE_TONE = set(["independent", "autonomous", "self-driven"])


def compute_sentiment(text: str) -> float:
    """
    Compute sentiment polarity of text using TextBlob.
    Returns a polarity score between -1 (negative) and 1 (positive).
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity


def extract_keywords(text: str) -> Counter:
    """
    Simple keyword extractor: tokenize on non-alphanumeric characters,
    lowercase, filter out short tokens.
    Returns a Counter of token frequencies.
    """
    tokens = re.findall(r"\b\w{3,}\b", text.lower())
    return Counter(tokens)


def match_score(job_desc: str, user_profile_json: str) -> dict:
    """
    Compute a match score between a job description and a user profile.

    Parameters:
    - job_desc: full job description text
    - user_profile_json: JSON string with fields: skills (list), experience (years), location,
      remote_preference (bool), values (list), desired_salary (number), etc.

    Returns:
    A dict with:
      - score: int match score [0-100]
      - reasons: list of strings explaining contributing factors
    """
    # Parse profile
    profile = json.loads(user_profile_json)
    user_skills = set([s.lower() for s in profile.get('skills', [])])
    user_values = set([v.lower() for v in profile.get('values', [])])
    remote_pref = profile.get('remote_preference', False)

    # Keyword relevance
    job_keywords = extract_keywords(job_desc)
    top_job_keywords = set([kw for kw, _ in job_keywords.most_common(20)])
    keyword_overlap = len(user_skills & top_job_keywords)
    keyword_score = min(1.0, keyword_overlap / 5.0)  # 5 overlapping keywords -> full points

    # Skill overlap
    required_skills = set([s.lower() for s in profile.get('skills', [])])
    profile_skills_set = user_skills
    # For demo assume job description lists skills in a Skills: section
    match = re.search(r"Skills[:\\n](.*)", job_desc, re.IGNORECASE)
    if match:
        job_skills = set(map(str.strip, match.group(1).split(',')))
        skill_overlap_count = len(profile_skills_set & job_skills)
        skill_score = min(1.0, skill_overlap_count / max(len(job_skills), 1))
    else:
        skill_score = 0.0

    # Tone matching via sentiment
    job_sent = compute_sentiment(job_desc)
    user_values_text = ' '.join(profile.get('values', []))
    user_sent = compute_sentiment(user_values_text)
    tone_diff = abs(job_sent - user_sent)
    tone_score = max(0.0, 1.0 - tone_diff)  # closer sentiments give higher score

    # Remote preference matching
    remote_score = 1.0 if ('remote' in job_desc.lower()) == remote_pref else 0.5

    # Weighted aggregation
    weights = {
        'keyword': 0.3,
        'skill': 0.4,
        'tone': 0.2,
        'remote': 0.1
    }
    raw_score = (
        weights['keyword'] * keyword_score +
        weights['skill'] * skill_score +
        weights['tone'] * tone_score +
        weights['remote'] * remote_score
    )
    final_score = int(round(raw_score * 100))

    # Build reasons
    reasons = []
    reasons.append(f"Found {keyword_overlap} overlapping keywords ({keyword_score*100:.0f}% of target).")
    reasons.append(f"Skill overlap score: {skill_score*100:.0f}% based on matched skills.")
    reasons.append(f"Tone compatibility: {tone_score*100:.0f}% (job sentiment {job_sent:.2f} vs user sentiment {user_sent:.2f}).")
    reasons.append(f"Remote fit: {int(remote_score*100)}%.")

    return {
        'score': final_score,
        'reasons': reasons
    }


# Example usage:
if __name__ == "__main__":
    example_job = """
    We are looking for a collaborative and innovative software engineer.
    Skills:
    Python, Django, REST API, Docker, Kubernetes
    This role is remote and ideal for a motivated individual.
    """
    example_profile = json.dumps({
        'skills': ['Python', 'Flask', 'Docker'],
        'values': ['collaborative', 'innovative'],
        'remote_preference': True
    })
    result = match_score(example_job, example_profile)
    print(f"Match score: {result['score']}")
    print("Reasons:")
    for r in result['reasons']:
        print("- ", r)
