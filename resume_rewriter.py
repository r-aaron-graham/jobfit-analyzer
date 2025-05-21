import re
import random

# Pools of active verbs and factual templates
active_verbs = [
    'Led', 'Implemented', 'Engineered', 'Optimized', 'Spearheaded',
    'Designed', 'Built', 'Streamlined', 'Enhanced', 'Orchestrated'
]
factual_templates = {
    'github': 'Contributed to {repo_count}+ public repositories (e.g., {top_repo}) on GitHub.',
    'linkedin': 'Connected with {network_size}+ professionals on LinkedIn showcasing leadership and collaboration.',
    'huggingface': 'Published {hf_model_count}+ models on Hugging Face under `{hf_username}` namespace.',
    'certifications': 'Earned certifications: {cert_list}.',
    'chat_history': 'Documented detailed discussions in AI chat histories demonstrating domain expertise.'
}


def extract_metrics(bullet: str) -> str:
    """
    Extract numerical metrics (e.g., percentages, dollar amounts, timeframes).
    """
    metrics = re.findall(r"\b\d+[\d,.%+]*\b", bullet)
    return ' '.join(metrics)


def extract_keywords(text: str) -> set:
    """
    Extract candidate keywords: alphanumeric tokens length>=4.
    """
    tokens = re.findall(r"\b[a-zA-Z]{4,}\b", text)
    return set(tok.lower() for tok in tokens)


def generate_profile_summary(profile: dict) -> str:
    """
    Create a factual summary from user profile:
      - GitHub repos count & top repo
      - LinkedIn network size
      - Hugging Face model count & username
      - List of key certifications
      - Mention chat history expertise
    """
    parts = []
    if profile.get('github'):
        repo_count = profile['github'].get('repo_count', 'N')
        top_repo = profile['github'].get('top_repo', 'repo-name')
        parts.append(factual_templates['github'].format(repo_count=repo_count, top_repo=top_repo))
    if profile.get('linkedin'):
        size = profile['linkedin'].get('network_size', 'N')
        parts.append(factual_templates['linkedin'].format(network_size=size))
    if profile.get('huggingface'):
        hf_user = profile['huggingface'].get('username', 'username')
        model_count = profile['huggingface'].get('model_count', 'N')
        parts.append(factual_templates['huggingface'].format(hf_model_count=model_count, hf_username=hf_user))
    if profile.get('certifications'):
        certs = ', '.join(profile['certifications'])
        parts.append(factual_templates['certifications'].format(cert_list=certs))
    if profile.get('chat_history'):
        parts.append(factual_templates['chat_history'])
    return '\n'.join(parts)


def rewrite_resume_section(resume: str, job_desc: str, profile: dict) -> str:
    """
    Rewrite resume bullets to align with job_desc, preserving metrics,
    injecting keywords, and appending profile facts summary.

    Inputs:
      - resume: bullet-per-line text
      - job_desc: job description text
      - profile: dict with keys:
         * github: {repo_count, top_repo}
         * linkedin: {network_size}
         * huggingface: {username, model_count}
         * certifications: list of strings
         * chat_history: bool
    Output:
      Formatted text: factual summary + rewritten bullets
    """
    # Summary of factual profile data
    summary = generate_profile_summary(profile)

    # Keywords from job description
    jd_keywords = extract_keywords(job_desc)

    rewritten = [summary, '\nExperience:']
    for line in resume.splitlines():
        line = line.strip()
        if not line.startswith('-') and not line.startswith('•'):
            continue
        bullet = re.sub(r'^[\-•]\s*', '', line)
        metrics = extract_metrics(bullet)
        overlap = extract_keywords(bullet) & jd_keywords
        kw_insert = ' '.join(overlap)
        verb = random.choice(active_verbs)

        parts = [verb]
        if kw_insert:
            parts.append(kw_insert.capitalize())
        action = re.match(r"(\w+\s+\w+)", bullet)
        if action:
            parts.append(action.group(1))
        if metrics:
            parts.append(f"by {metrics}")
        sentence = ' '.join(parts)
        if len(sentence.split()) < 6:
            sentence += ", driving results"
        rewritten.append(f"- {sentence}.")

    return '\n'.join(rewritten)

# Example invocation:
if __name__ == '__main__':
    sample_resume = '''
- Engineered modular Python libraries, boosting answer relevance 18%.
- Labeled 10K+ multi-domain records, reducing prep time 40%.
'''
    sample_job = "We seek an innovative Python engineer with data labeling expertise to optimize pipeline performance."
    sample_profile = {
        'github': {'repo_count': 25, 'top_repo': 'coal2cloud'},
        'linkedin': {'network_size': 500},
        'huggingface': {'username': 'raarongraham', 'model_count': 8},
        'certifications': ['ML Specialization (Coursera)', 'Azure LLM Ops (Duke)'],
        'chat_history': True
    }
    print(rewrite_resume_section(sample_resume, sample_job, sample_profile))
