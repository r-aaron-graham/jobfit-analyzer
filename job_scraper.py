import json
import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class JobScraper:
    """
    Extensible scraper for multiple job boards using site definitions.

    Define each site with:
      - name: identifier
      - url: listing page or API endpoint
      - method: 'api', 'html', or 'selenium'
      - selectors or json_paths: for parsing title, company, description, salary, tags, apply_link
    """
    def __init__(self, site_configs, remote=None, full_time=None, min_salary=None):
        self.site_configs = site_configs
        self.remote = remote
        self.full_time = full_time
        self.min_salary = min_salary
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape_site(self, config, query=None):
        jobs = []
        try:
            if config['method'] == 'api':
                resp = requests.get(config['url'], params=config.get('params', {}))
                data = resp.json()
                for item in data:
                    job = {field: self._extract_json(item, path)
                           for field, path in config['fields'].items()}
                    job['source'] = config['name']
                    jobs.append(job)
            elif config['method'] == 'html':
                text = requests.get(config['url']).text
                soup = BeautifulSoup(text, 'html.parser')
                for elem in soup.select(config['item_selector']):
                    job = {'source': config['name']}
                    for field, sel in config['fields'].items():
                        sub = elem.select_one(sel)
                        job[field] = sub.get_text(' ', strip=True) if sub else ''
                    jobs.append(job)
            elif config['method'] == 'selenium':
                self.driver.get(config['url'].format(query=query or ''))
                time.sleep(config.get('wait', 2))
                elems = self.driver.find_elements(By.CSS_SELECTOR, config['item_selector'])
                for elem in elems[:config.get('limit', 20)]:
                    job = {'source': config['name']}
                    for field, sel in config['fields'].items():
                        try:
                            if field == 'apply_link':
                                job[field] = elem.find_element(By.CSS_SELECTOR, sel).get_attribute('href')
                            else:
                                job[field] = elem.find_element(By.CSS_SELECTOR, sel).text
                        except:
                            job[field] = ''
                    jobs.append(job)
        except Exception:
            pass
        return jobs

    def _extract_json(self, data, path):
        # path: list of keys for nested JSON
        for key in path:
            data = data.get(key, {})
        return data if isinstance(data, str) else json.dumps(data)

    def filter_jobs(self, jobs):
        filtered = []
        for job in jobs:
            desc = job.get('description', '').lower()
            tags = [t.lower() for t in job.get('tags', [])]
            # remote filter
            if self.remote is not None:
                is_remote = self.remote and ('remote' in tags or 'remote' in desc)
                if is_remote != self.remote: continue
            # full_time filter
            if self.full_time is not None:
                ft = bool(re.search(r'full[- ]?time', desc, re.I))
                if ft != self.full_time: continue
            # salary filter
            if self.min_salary and job.get('salary'):
                nums = re.findall(r"\d+[\d,]*", job['salary'])
                if nums and int(nums[0].replace(',', '')) < self.min_salary: continue
            filtered.append(job)
        return filtered

    def scrape_all(self, query=None):
        all_jobs = []
        for config in self.site_configs:
            all_jobs.extend(self.scrape_site(config, query=query))
        return self.filter_jobs(all_jobs)

# Example site_configs list with placeholders for 20+ sites
SITE_CONFIGS = [
    {
        'name': 'RemoteOK',
        'url': 'https://remoteok.com/',
        'method': 'html',
        'item_selector': 'tr.job',
        'fields': {
            'title': 'h2',
            'company': '.companyLink h3',
            'description': '.description',
            'salary': '.salary',
            'tags': '.tag',
            'apply_link': None  # custom logic in scrape_site
        }
    },
    # Add 20+ similar dicts for Wellfound, GitHub Jobs, Indeed, Dice, HN, WWR, Remote.co,
    # Jobspresso, AngelList API, StackOverflow Jobs, Glassdoor, Monster, LinkedIn etc.
]

if __name__ == '__main__':
    scraper = JobScraper(site_configs=SITE_CONFIGS, remote=True, full_time=True, min_salary=100000)
    results = scraper.scrape_all(query='Data Scientist')
    print(json.dumps(results, indent=2))
