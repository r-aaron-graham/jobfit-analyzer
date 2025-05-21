# Job Matcher

A lightweight Python module to compute a match score (0–100) between a job description and a user profile JSON.

## Repository Structure

```
job-matcher/
├── job_matcher.py    # Core matching logic
├── example.py        # CLI runner
├── demo.ipynb        # Interactive Jupyter demo
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/your-username/job-matchmaker.git
   cd job-matchmaker
   ```
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command-line `example.py`

```bash
python example.py --job path/to/job.txt --profile path/to/profile.json
```

### Interactive `demo.ipynb`

Launch JupyterLab in the repo root and open `demo.ipynb` for an interactive exploration.

## Module API

```python
from job_matcher import match_score

# job_desc: str (full text of the job posting)
# profile_json: str (JSON-encoded user profile)
result = match_score(job_desc, profile_json)
print(result['score'])      # e.g. 85
print(result['reasons'])    # list of explanation strings
```

### Profile JSON Format

```json
{
  "skills": ["Python", "Django", "Docker"],
  "values": ["collaborative", "innovative"],
  "remote_preference": true,
  "desired_salary": 120000
}
```

## Customization

* Adjust weights in `job_matcher.py` under the `weights` dict.
* Enhance NLP: swap in spaCy, use embeddings, customize keyword extraction.
* Extend remote-work logic, salary checks, location matching, etc.

## License

MIT © Your Name
