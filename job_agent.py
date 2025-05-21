import json
import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from job_scraper import JobScraper
from job_cleaner import clean_pipeline
from job_categorizer import JobCategorizer
from job_ranker import JobRanker
from resume_star_enhancer import enhance_with_star
import smtplib
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)

class JobSearchAgent:
    """
    Scheduled agent to discover and deliver personalized job matches.

    Modules:
      1. Scrape listings via JobScraper
      2. Clean data via clean_pipeline
      3. Categorize via JobCategorizer
      4. Score via JobRanker
      5. Rewrite resume bullets via enhance_with_star
      6. Notify via email or Slack

    All inputs/outputs are JSON-friendly.
    """
    def __init__(self, profile, site_configs, notify_cfg):
        # profile: dict of user preferences for scoring & resume enhancement
        # site_configs: list of site config dicts for JobScraper
        # notify_cfg: dict with email or slack settings
        self.profile = profile
        self.scraper = JobScraper(site_configs,
                                  remote=profile.get('remote_preference'),
                                  full_time=profile.get('full_time'),
                                  min_salary=profile.get('desired_salary'))
        self.cleaner = clean_pipeline
        self.categorizer = JobCategorizer()
        self.ranker = JobRanker()
        self.notify_cfg = notify_cfg

    def fetch_and_process(self, query=None):
        logging.info('Scraping jobs...')
        raw_jobs = self.scraper.scrape_all(query=query)
        logging.info(f'Fetched {len(raw_jobs)} raw jobs')

        logging.info('Cleaning jobs...')
        jobs = self.cleaner(raw_jobs)
        logging.info(f'{len(jobs)} jobs after cleaning')

        logging.info('Categorizing jobs...')
        for job in jobs:
            tags = self.categorizer.categorize(job.get('description', ''))
            job.update(tags)

        logging.info('Ranking jobs...')
        ranked_json = self.ranker.rank(jobs, self.profile, top_n=5)
        ranked = json.loads(ranked_json)['ranked_jobs']

        logging.info('Enhancing resume for top jobs...')
        enhanced_resumes = {}
        original_resume = self.profile.get('resume_text', '')
        for entry in ranked:
            job = entry['job']
            jd = job.get('description', '')
            enhanced = enhance_with_star(original_resume, jd)
            enhanced_resumes[job.get('source') + '_' + job.get('title')] = enhanced

        payload = {
            'timestamp': time.time(),
            'ranked_jobs': ranked,
            'enhanced_resumes': enhanced_resumes
        }
        return payload

    def notify(self, payload):
        # Email notification
        if 'email' in self.notify_cfg:
            self._send_email(payload)
        # Slack notification
        if 'slack_webhook' in self.notify_cfg:
            self._send_slack(payload)

    def _send_email(self, payload):
        cfg = self.notify_cfg['email']
        msg = json.dumps(payload, indent=2)
        server = smtplib.SMTP(cfg['smtp_server'], cfg.get('smtp_port', 587))
        server.starttls()
        server.login(cfg['username'], cfg['password'])
        server.sendmail(cfg['from_addr'], cfg['to_addrs'], msg)
        server.quit()
        logging.info('Email sent')

    def _send_slack(self, payload):
        cfg = self.notify_cfg['slack_webhook']
        text = '*Top Job Matches*\n'
        for entry in payload['ranked_jobs']:
            job = entry['job']
            text += f"• {job['title']} at {job['company']} ({entry['score']}%) <{job['apply_link']}>\n"
        requests.post(cfg['url'], json={'text': text})
        logging.info('Slack message sent')

def schedule_agent(profile, site_configs, notify_cfg, interval_minutes=60):
    agent = JobSearchAgent(profile, site_configs, notify_cfg)
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: agent.notify(agent.fetch_and_process(query=profile.get('query'))),
                      'interval', minutes=interval_minutes)
    logging.info(f'Starting scheduler: every {interval_minutes} minutes')
    scheduler.start()

if __name__ == '__main__':
    # Load user profile, site configs, and notification settings from JSON files
    with open('profile.json') as f:
        profile = json.load(f)
    with open('site_configs.json') as f:
        site_configs = json.load(f)
    with open('notify_cfg.json') as f:
        notify_cfg = json.load(f)

    # Kick off the scheduled agent
    schedule_agent(profile, site_configs, notify_cfg, interval_minutes=120)
