import re

class JobCategorizer:
    """
    Categorizes a job listing by industry, role type (IC vs management),
    skill category (frontend, backend, data science, etc.), and remote/on-site status.
    Uses keyword-based regex matching.
    """

    INDUSTRY_KEYWORDS = {
        'finance': [r"\bfinance\b", r"\bbanking\b", r"\binvestment\b"],
        'healthcare': [r"\bhealthcare\b", r"\bmedical\b", r"\bpharma\b"],
        'tech': [r"\bsoftware\b", r"\btechnology\b", r"\bit\b", r"\btech\b"],
        'education': [r"\beducation\b", r"\bschool\b", r"\bteaching\b"],
        'retail': [r"\bretail\b", r"\be-commerce\b", r"\becommerce\b"],
        # add more industries as needed
    }

    ROLE_KEYWORDS = {
        'management': [r"\bmanager\b", r"\bdirector\b", r"\bhead of\b", r"\blead\b", r"\bsupervisor\b"],
        'individual_contributor': [r"\bintern\b", r"\bengineer\b", r"\bdeveloper\b", r"\bspecialist\b", r"\banalyst\b"],
    }

    SKILL_CATEGORIES = {
        'frontend': [r"\bfrontend\b", r"\breact\b", r"\bvue\b", r"\bangular\b", r"\bhtml\b", r"\bcss\b", r"\bjavascript\b"],
        'backend': [r"\bbackend\b", r"\bpython\b", r"\bjava\b", r"\bnode\b", r"\bb\.net\b", r"\bruby\b"],
        'data_science': [r"\bdata science\b", r"\bmachine learning\b", r"\bdeep learning\b", r"\bpandas\b", r"\bscikit-learn\b"],
        'devops': [r"\bdevops\b", r"\bci/cd\b", r"\bdocker\b", r"\bkubernetes\b", r"\bjenkins\b"],
        'design': [r"\bux\b", r"\bui\b", r"\bdesigner\b", r"\b\bfigma\b", r"\bsketch\b"],
        # add more skill categories as needed
    }

    REMOTE_PATTERNS = {
        'remote': [r"\bremote\b", r"\bwork from home\b", r"\btelecommute\b"],
        'on_site': [r"\bon[- ]site\b", r"\bin[- ]office\b", r"\blocal\b"],
    }

    def __init__(self):
        # Precompile regex patterns for speed
        self.industry_regex = {
            k: [re.compile(pat, re.IGNORECASE) for pat in pats]
            for k, pats in self.INDUSTRY_KEYWORDS.items()
        }
        self.role_regex = {
            k: [re.compile(pat, re.IGNORECASE) for pat in pats]
            for k, pats in self.ROLE_KEYWORDS.items()
        }
        self.skill_regex = {
            k: [re.compile(pat, re.IGNORECASE) for pat in pats]
            for k, pats in self.SKILL_CATEGORIES.items()
        }
        self.remote_regex = {
            k: [re.compile(pat, re.IGNORECASE) for pat in pats]
            for k, pats in self.REMOTE_PATTERNS.items()
        }

    def categorize(self, job_text: str) -> dict:
        """
        Analyze job_text and return tags:
          - industry
          - role_type ('management' or 'individual_contributor')
          - skill_categories (list)
          - work_location ('remote', 'on_site', or 'unspecified')
        """
        tags = {
            'industry': 'unknown',
            'role_type': 'unknown',
            'skill_categories': [],
            'work_location': 'unspecified'
        }

        # Industry detection
        for industry, patterns in self.industry_regex.items():
            if any(p.search(job_text) for p in patterns):
                tags['industry'] = industry
                break

        # Role type detection (management first)
        for role, patterns in self.role_regex.items():
            if any(p.search(job_text) for p in patterns):
                tags['role_type'] = role
                break

        # Skill category detection
        for skill_cat, patterns in self.skill_regex.items():
            if any(p.search(job_text) for p in patterns):
                tags['skill_categories'].append(skill_cat)

        # Work location detection
        for loc, patterns in self.remote_regex.items():
            if any(p.search(job_text) for p in patterns):
                tags['work_location'] = loc
                break

        return tags

# Example usage
def example():
    job_post = """
    We are hiring a Senior Software Engineer (Frontend) in our tech team.
    Must have 5+ years React and JavaScript experience.
    This is a remote-friendly position for an autonomous engineer.
    """
    categorizer = JobCategorizer()
    print(categorizer.categorize(job_post))  # {'industry': 'tech', 'role_type': 'individual_contributor', ...}

if __name__ == '__main__':
    example()
