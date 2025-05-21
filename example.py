# example.py
"""
A quick command-line runner for the job_matcher module.
"""
import json
import argparse
from job_matcher import match_score


def main():
    parser = argparse.ArgumentParser(
        description="Compute match score between a job description and a user profile JSON.")
    parser.add_argument("--job", "-j", required=True,
                        help="Path to a text file containing the job description.")
    parser.add_argument("--profile", "-p", required=True,
                        help="Path to a JSON file containing the user profile.")
    args = parser.parse_args()

    # Load job description
    with open(args.job, 'r', encoding='utf-8') as f:
        job_desc = f.read()

    # Load profile JSON
    with open(args.profile, 'r', encoding='utf-8') as f:
        profile_json = f.read()

    # Compute match
    result = match_score(job_desc, profile_json)

    # Output results
    print(f"Match score: {result['score']}/100")
    print("Reasons:")
    for reason in result['reasons']:
        print(f"- {reason}")


if __name__ == '__main__':
    main()
