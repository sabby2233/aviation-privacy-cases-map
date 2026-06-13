"""
collect_ico.py - 从ICO (UK Information Commissioner's Office) 采集航空数据案例

ICO Enforcement Notices: https://ico.org.uk/action-weve-taken/enforcement/
ICO Reprimands: https://ico.org.uk/action-weve-taken/reprimands/
ICO Fines: https://ico.org.uk/action-weve-taken/enforcement/
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collect.case_builder import parse_date, build_case
from collect.keyword_filter import matches_aviation

CASES_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cases.json')

ICO_SEARCH_URL = "https://ico.org.uk/action-weve-taken/enforcement/"
ICO_REPRIMANDS_URL = "https://ico.org.uk/action-weve-taken/reprimands/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Known aviation enforcement cases from ICO (manually curated + auto-found)
KNOWN_ICO_AVIATION_CASES = [
    {
        "caseName": "ICO Fine against British Airways plc",
        "caseNameEn": "ICO Fine against British Airways plc (2018 Data Breach)",
        "country": "GB",
        "date": "2020-10-16",
        "sourceUrl": "https://ico.org.uk/action-weve-taken/enforcement/british-airways-pecr/",
        "summary": "British Airways因2018年网络攻击导致约429,612名客户的个人和财务数据泄露，被ICO依据GDPR罚款£20,000,000。原始拟议罚款为£183,390,000，后经考虑合作态度及COVID-19影响大幅降低。该攻击通过在BA网站植入恶意代码实现，属供应链攻击。",
        "authority": "Information Commissioner's Office (ICO)",
        "authorityShort": "ICO",
        "tags": ["GDPR", "data-breach", "passenger-data", "cyber-attack", "supply-chain"],
        "fineAmount": 20000000,
        "fineCurrency": "GBP",
    },
    {
        "caseName": "ICO Fine against Cathay Pacific Airways Limited",
        "caseNameEn": "ICO Fine against Cathay Pacific Airways (2018 Data Breach)",
        "country": "GB",
        "date": "2020-03-04",
        "sourceUrl": "https://ico.org.uk/action-weve-taken/enforcement/cathay-pacific-airways-limited/",
        "summary": "国泰航空2018年数据泄露，超过900万名全球旅客的个人信息（包括护照号码、身份证号码和历史旅行信息）被黑客获取。ICO认为国泰航空未采取足够措施保护客户数据，依据DPA 2018罚款£500,000（发生在GDPR生效之前）。",
        "authority": "Information Commissioner's Office (ICO)",
        "authorityShort": "ICO",
        "tags": ["DPA2018", "data-breach", "passenger-data", "passport-data"],
        "fineAmount": 500000,
        "fineCurrency": "GBP",
    },
    {
        "caseName": "ICO Reprimand - easyJet plc (2020 Data Breach)",
        "caseNameEn": "ICO Reprimand against easyJet plc (2020 Cyber Attack)",
        "country": "GB",
        "date": "2020-05-19",
        "sourceUrl": "https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2020/05/statement-easyjet/",
        "summary": "easyJet遭网络攻击，约900万名客户的电子邮件和旅行详情泄露，其中约2,208名客户的信用卡信息也被获取。ICO对此展开调查，easyJet主动向ICO通报，ICO最终未开出罚款但发出正式告诫。",
        "authority": "Information Commissioner's Office (ICO)",
        "authorityShort": "ICO",
        "tags": ["GDPR", "data-breach", "passenger-data", "credit-card-data"],
        "fineAmount": None,
        "fineCurrency": None,
    },
]


def load_existing_urls():
    """Load existing case source URLs for dedup."""
    if os.path.exists(CASES_FILE):
        with open(CASES_FILE, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        return {c.get('sourceUrl', '') for c in cases}
    return set()


def scrape_ico_enforcement_page():
    """Try to scrape ICO enforcement page for any aviation cases."""
    found_cases = []
    
    for url in [ICO_SEARCH_URL, ICO_REPRIMANDS_URL]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  ICO page returned {r.status_code}: {url}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Find enforcement case links
            links = soup.find_all('a', href=True)
            for link in links:
                link_text = link.get_text(strip=True)
                href = link.get('href', '')
                
                if not href.startswith('/action-weve-taken/'):
                    continue
                
                full_url = f"https://ico.org.uk{href}"
                
                # Filter for aviation-related text
                if matches_aviation(link_text):
                    found_cases.append({
                        'text': link_text,
                        'url': full_url
                    })
                    print(f"  Aviation link found: {link_text[:80]}")
            
            time.sleep(1)
        except Exception as e:
            print(f"  Error scraping {url}: {e}")
    
    return found_cases


def collect():
    """Main collection function."""
    print("=== ICO UK Collection ===")
    existing_urls = load_existing_urls()
    all_cases = []
    
    # 1. Use manually curated known cases
    print(f"\nProcessing {len(KNOWN_ICO_AVIATION_CASES)} known ICO aviation cases...")
    for i, raw in enumerate(KNOWN_ICO_AVIATION_CASES):
        if raw['sourceUrl'] in existing_urls:
            print(f"  Skip (exists): {raw['caseName'][:60]}")
            continue
        
        case = {
            'id': '',  # Will be reassigned in merge step
            'caseName': raw['caseName'],
            'caseNameEn': raw['caseNameEn'],
            'country': 'GB',
            'countryName': '英国',
            'caseType': 'admin',
            'authority': raw['authority'],
            'authorityShort': raw['authorityShort'],
            'date': raw['date'],
            'sourceUrl': raw['sourceUrl'],
            'summary': raw['summary'],
            'tags': raw['tags'],
            'fineAmount': raw.get('fineAmount'),
            'fineCurrency': raw.get('fineCurrency'),
            'sector': 'Aviation',
            'sourceName': 'ICO',
            'lastVerified': datetime.now().strftime('%Y-%m-%d'),
        }
        all_cases.append(case)
        print(f"  Added: {raw['caseName'][:60]}")
    
    # 2. Try to scrape for additional cases
    print("\nScraping ICO enforcement pages for additional aviation cases...")
    scrape_results = scrape_ico_enforcement_page()
    
    for item in scrape_results:
        if item['url'] in existing_urls:
            continue
        # Already covered by KNOWN cases?
        already_known = any(c['sourceUrl'] == item['url'] for c in all_cases)
        if already_known:
            continue
        # Add as a stub for manual review
        all_cases.append({
            'id': '',
            'caseName': item['text'],
            'caseNameEn': item['text'],
            'country': 'GB',
            'countryName': '英国',
            'caseType': 'admin',
            'authority': 'Information Commissioner\'s Office (ICO)',
            'authorityShort': 'ICO',
            'date': None,
            'sourceUrl': item['url'],
            'summary': f"ICO enforcement action: {item['text']}",
            'tags': ['ICO', 'UK', 'aviation'],
            'fineAmount': None,
            'fineCurrency': None,
            'sector': 'Aviation',
            'sourceName': 'ICO',
            'lastVerified': datetime.now().strftime('%Y-%m-%d'),
        })
    
    print(f"\nTotal ICO aviation cases: {len(all_cases)}")
    return all_cases


if __name__ == '__main__':
    cases = collect()
    output_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'collected_ico.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
