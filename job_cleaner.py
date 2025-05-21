import re
from difflib import SequenceMatcher

# Required fields for a valid job posting\ REQUIRED_FIELDS = ['title', 'company', 'location', 'description', 'apply_link']


def normalize_text(text: str) -> str:
    """
    Normalize whitespace and capitalization for a text field.
    """
    return re.sub(r"\s+", " ", text.strip()).title()


def is_similar(a: str, b: str, threshold: float = 0.85) -> bool:
    """
    Check if two strings are similar above a given threshold.
    """
    if not a or not b:
        return False
    ratio = SequenceMatcher(None, a.lower(), b.lower()).ratio()
    return ratio >= threshold


def deduplicate_jobs(jobs: list, title_threshold: float = 0.85) -> list:
    """
    Remove duplicate job postings based on title, company, and location similarity.
    Keeps the first occurrence.
    """
    unique = []
    for job in jobs:
        duplicate = False
        for kept in unique:
            if (is_similar(job.get('title',''), kept.get('title',''), title_threshold)
                and job.get('company','').lower() == kept.get('company','').lower()
                and job.get('location','').lower() == kept.get('location','').lower()):
                duplicate = True
                break
        if not duplicate:
            unique.append(job)
    return unique


def normalize_jobs(jobs: list) -> list:
    """
    Normalize text fields across job postings.
    """
    normalized = []
    for job in jobs:
        norm_job = job.copy()
        # Normalize required text fields
        for field in ['title', 'company', 'location']:
            if field in norm_job and norm_job[field]:
                norm_job[field] = normalize_text(norm_job[field])
        # Ensure tags are a list of lowercase strings
        tags = norm_job.get('tags', [])
        norm_job['tags'] = [t.lower().strip() for t in tags if isinstance(t, str)]
        normalized.append(norm_job)
    return normalized


def filter_complete_jobs(jobs: list) -> list:
    """
    Filter out any job postings missing required fields or with empty strings.
    """
    filtered = []
    for job in jobs:
        if all(job.get(field) for field in REQUIRED_FIELDS):
            filtered.append(job)
    return filtered


def clean_pipeline(jobs: list) -> list:
    """
    Full cleaning pipeline:
      1. Filter incomplete postings
      2. Normalize text fields
      3. Deduplicate postings
      4. Return cleaned list
    """
    good = filter_complete_jobs(jobs)
    norm = normalize_jobs(good)
    unique = deduplicate_jobs(norm)
    return unique

# Example usage
if __name__ == '__main__':
    sample_jobs = [
        {'title': 'Senior Engineer', 'company': 'Acme Corp', 'location': 'new york',
         'description': '...', 'apply_link': 'http://...', 'tags':['remote']},
        {'title': 'Senior engineer ', 'company': 'acme corp', 'location': 'New York ',
         'description': '...', 'apply_link': 'http://...', 'tags':['Remote']},
        {'title': 'Data Scientist', 'company': 'DataWorks', 'location': '',
         'description': '...', 'apply_link': 'http://...', 'tags':[]},
    ]
    cleaned = clean_pipeline(sample_jobs)
    for job in cleaned:
        print(job)
