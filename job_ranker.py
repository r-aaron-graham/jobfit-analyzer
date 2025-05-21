import json

class JobRanker:
    """
    Ranks parsed job listings against a user preference profile.

    Weights can be customized for skills match, mission alignment,
    salary fit, location fit, company size preference, and growth potential.
    """

    DEFAULT_WEIGHTS = {
        'skills': 0.25,
        'mission': 0.15,
        'salary': 0.2,
        'location': 0.15,
        'company_size': 0.1,
        'growth': 0.15
    }

    def __init__(self, weights=None):
        # Use provided weights or defaults
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

    def _score_skills(self, job, profile):
        # job['skills'] and profile['desired_skills'] are sets
        overlap = job.get('skills', set()) & profile.get('desired_skills', set())
        total = profile.get('desired_skills', set())
        return len(overlap) / max(len(total), 1)

    def _score_mission(self, job, profile):
        # match on shared mission keywords
        overlap = set(job.get('mission_keywords', [])) & set(profile.get('mission_keywords', []))
        total = set(profile.get('mission_keywords', []))
        return len(overlap) / max(len(total), 1)

    def _score_salary(self, job, profile):
        # normalize salary within range
        desired = profile.get('desired_salary', 0)
        low, high = job.get('salary_range', (0, float('inf')))
        if low <= desired <= high:
            return 1.0
        # if outside, score declines linearly to 0 at 50% deviation
        diff = 0
        if desired < low:
            diff = (low - desired) / max(desired, 1)
        else:
            diff = (desired - high) / max(high, 1)
        return max(0.0, 1.0 - diff)

    def _score_location(self, job, profile):
        pref = profile.get('location_preference')  # 'remote', 'on_site', or 'either'
        job_loc = job.get('work_location', 'unspecified')
        if pref == 'either' or job_loc == 'unspecified':
            return 1.0
        return 1.0 if pref == job_loc else 0.0

    def _score_company_size(self, job, profile):
        # profile['preferred_company_size'] is a list or set
        pref = profile.get('preferred_company_size', [])
        size = job.get('company_size')
        return 1.0 if size in pref else 0.0

    def _score_growth(self, job, profile):
        # job['growth_potential'] is a number 0-1, profile may weight growth
        return job.get('growth_potential', 0.0)

    def rank(self, jobs, profile, top_n=None):
        """
        Rank a list of job dicts based on profile preferences.

        Each job dict should include keys:
          - skills: set of skills
          - mission_keywords: list of mission words
          - salary_range: (low, high) tuple
          - work_location: 'remote'/'on_site'/'unspecified'
          - company_size: e.g. 'startup', 'mid', 'enterprise'
          - growth_potential: float between 0 and 1

        Profile dict should include:
          - desired_skills: set
          - mission_keywords: list
          - desired_salary: number
          - location_preference: 'remote'/'on_site'/'either'
          - preferred_company_size: list or set

        Returns a JSON string of ranked jobs with scores and reasons.
        """
        ranked = []
        for job in jobs:
            reasons = []
            # Calculate component scores
            scores = {
                'skills': self._score_skills(job, profile),
                'mission': self._score_mission(job, profile),
                'salary': self._score_salary(job, profile),
                'location': self._score_location(job, profile),
                'company_size': self._score_company_size(job, profile),
                'growth': self._score_growth(job, profile)
            }
            # Weighted sum
            total = 0.0
            for k, v in scores.items():
                w = self.weights.get(k, 0)
                total += w * v
                reasons.append(f"{k}: {v*100:.0f}% (weight {w})")

            score = round(total * 100)
            ranked.append({
                'job': job,
                'score': score,
                'reasons': reasons
            })

        # Sort descending by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        if top_n:
            ranked = ranked[:top_n]

        return json.dumps({'ranked_jobs': ranked}, indent=2)

# Example usage
if __name__ == '__main__':
    sample_jobs = [
        {
            'id': 1,
            'skills': {'python', 'docker', 'kubernetes'},
            'mission_keywords': ['sustainability', 'open source'],
            'salary_range': (90000, 120000),
            'work_location': 'remote',
            'company_size': 'startup',
            'growth_potential': 0.9
        },
        {
            'id': 2,
            'skills': {'java', 'aws', 'microservices'},
            'mission_keywords': ['enterprise', 'scalability'],
            'salary_range': (110000, 150000),
            'work_location': 'on_site',
            'company_size': 'enterprise',
            'growth_potential': 0.5
        }
    ]
    user_profile = {
        'desired_skills': {'python', 'kubernetes', 'ml'},
        'mission_keywords': ['open source'],
        'desired_salary': 100000,
        'location_preference': 'remote',
        'preferred_company_size': {'startup', 'mid'},
    }
    ranker = JobRanker()
    print(ranker.rank(sample_jobs, user_profile))
