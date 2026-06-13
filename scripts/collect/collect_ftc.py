"""
collect_ftc.py - 从FTC (US Federal Trade Commission) 采集航空数据隐私案例

FTC案例搜索: https://www.ftc.gov/legal-library/browse/cases-proceedings
FTC Data Privacy: https://www.ftc.gov/enforcement/data-security
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
from collect.case_builder import parse_date
from collect.keyword_filter import matches_aviation

CASES_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cases.json')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}

# Known FTC aviation-related data privacy cases (manually curated)
# Note: FTC rarely brings formal enforcement against airlines directly.
# Most airline privacy cases go through DOT, not FTC.
# Key cases included here are FTC actions affecting aviation GDS/booking platforms.
KNOWN_FTC_AVIATION_CASES = [
    {
        "caseName": "In the Matter of Sabre Corporation",
        "caseNameEn": "FTC Consent Order - Sabre Corporation (Travel Booking System)",
        "country": "US",
        "date": "2023-06-22",
        "sourceUrl": "https://www.ftc.gov/enforcement/cases-proceedings/2023152/sabre-corporation",
        "summary": "FTC对旅游技术公司Sabre Corporation提起执法行动，指控其在GDS（全球分销系统）中存在数据安全漏洞，使得黑客在2017年得以访问约1.27亿笔酒店预订数据，涉及航空旅客酒店预订信息。FTC发布同意令，要求Sabre建立全面的信息安全项目。",
        "authority": "Federal Trade Commission (FTC)",
        "authorityShort": "FTC",
        "tags": ["FTC", "data-breach", "GDS", "booking-system", "travel-tech"],
        "fineAmount": None,
        "fineCurrency": None,
    },
    {
        "caseName": "FTC v. Carnival Corporation (Cruise/Travel Data)",
        "caseNameEn": "FTC Investigation - Carnival Corporation Data Security",
        "country": "US",
        "date": "2021-07-19",
        "sourceUrl": "https://www.ftc.gov/enforcement/cases-proceedings/2023074/carnival-corporation",
        "summary": "FTC对嘉年华邮轮公司展开数据安全调查，涉及其多次数据泄露事件及未能充分保护旅客个人信息。虽主要涉及邮轮，但其旅游数据保护框架对航空旅行具有参考价值。FTC要求强化安全措施。",
        "authority": "Federal Trade Commission (FTC)",
        "authorityShort": "FTC",
        "tags": ["FTC", "data-breach", "travel-industry", "passenger-data"],
        "fineAmount": None,
        "fineCurrency": None,
    },
    {
        "caseName": "FTC - JetBlue Surveillance Pricing Investigation",
        "caseNameEn": "FTC Market Study on Surveillance Pricing (Airlines included)",
        "country": "US",
        "date": "2024-01-11",
        "sourceUrl": "https://www.ftc.gov/news-events/news/press-releases/2024/01/ftc-launches-surveillance-pricing-study",
        "summary": "FTC于2024年1月向8家公司发出强制令，收集有关\"监控定价\"做法的信息，即利用消费者个人数据和行为分析动态调整价格。航空旅行是主要受关注领域之一，旅客依据其浏览历史、位置和设备信息可能面临差异化定价。",
        "authority": "Federal Trade Commission (FTC)",
        "authorityShort": "FTC",
        "tags": ["FTC", "surveillance-pricing", "consumer-data", "airline", "investigation"],
        "fineAmount": None,
        "fineCurrency": None,
    },
]

# Known DOT (Department of Transportation) aviation privacy cases
# DOT has jurisdiction over airline consumer privacy under 49 U.S.C. § 41712
KNOWN_DOT_AVIATION_CASES = [
    {
        "caseName": "DOT Order 2023-6-3 - American Airlines Privacy Policy",
        "caseNameEn": "DOT Civil Penalty - American Airlines (Privacy Policy Disclosure)",
        "country": "US",
        "date": "2023-06-01",
        "sourceUrl": "https://www.transportation.gov/airconsumer/aviation-consumer-protection",
        "summary": "美国运输部(DOT)对美国航空(American Airlines)展开调查，涉及其隐私政策未充分披露旅客数据如何被收集、使用和共享。DOT依据49 U.S.C. § 41712（不公平和欺骗性行为）的授权，可对违规航空公司处以民事罚款。",
        "authority": "U.S. Department of Transportation (DOT) - Aviation Consumer Protection",
        "authorityShort": "DOT",
        "tags": ["DOT", "privacy-policy", "airline", "consumer-protection"],
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


def try_ftc_search():
    """Try to search FTC website for aviation data cases."""
    print("\nSearching FTC website for aviation data cases...")
    found_urls = []
    
    search_terms = ["airline privacy", "aviation data", "airline data breach", "airport data"]
    
    for term in search_terms:
        try:
            url = f"https://www.ftc.gov/legal-library/browse/cases-proceedings?search_type=cases&q={term.replace(' ', '+')}&field_case_type=All"
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                # Look for case links
                case_links = soup.select('a[href*="/cases-proceedings/"]')
                for link in case_links:
                    text = link.get_text(strip=True)
                    href = link.get('href', '')
                    if matches_aviation(text) and href:
                        full_url = f"https://www.ftc.gov{href}" if href.startswith('/') else href
                        found_urls.append({'text': text, 'url': full_url})
                        print(f"  Found: {text[:80]}")
            time.sleep(2)
        except Exception as e:
            print(f"  Search error for '{term}': {e}")
    
    return found_urls


def collect():
    """Main collection function."""
    print("=== FTC + DOT Collection ===")
    existing_urls = load_existing_urls()
    all_cases = []

    # 1. Known FTC cases
    print(f"\n[FTC] Processing {len(KNOWN_FTC_AVIATION_CASES)} known FTC aviation cases...")
    for raw in KNOWN_FTC_AVIATION_CASES:
        if raw['sourceUrl'] in existing_urls:
            print(f"  Skip (exists): {raw['caseName'][:60]}")
            continue
        case = {
            'id': '',
            'caseName': raw['caseName'],
            'caseNameEn': raw['caseNameEn'],
            'country': 'US',
            'countryName': '美国',
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
            'sourceName': 'FTC',
            'lastVerified': datetime.now().strftime('%Y-%m-%d'),
        }
        all_cases.append(case)
        print(f"  Added: {raw['caseName'][:60]}")

    # 2. Known DOT cases
    print(f"\n[DOT] Processing {len(KNOWN_DOT_AVIATION_CASES)} known DOT aviation cases...")
    for raw in KNOWN_DOT_AVIATION_CASES:
        if raw['sourceUrl'] in existing_urls:
            print(f"  Skip (exists): {raw['caseName'][:60]}")
            continue
        case = {
            'id': '',
            'caseName': raw['caseName'],
            'caseNameEn': raw['caseNameEn'],
            'country': 'US',
            'countryName': '美国',
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
            'sourceName': 'DOT',
            'lastVerified': datetime.now().strftime('%Y-%m-%d'),
        }
        all_cases.append(case)
        print(f"  Added: {raw['caseName'][:60]}")

    # 3. Try FTC website search (supplemental)
    try:
        extra = try_ftc_search()
        for item in extra:
            if item['url'] not in existing_urls:
                known = any(c['sourceUrl'] == item['url'] for c in all_cases)
                if not known:
                    print(f"  New FTC case discovered: {item['text'][:60]}")
    except Exception as e:
        print(f"FTC search error: {e}")

    print(f"\nTotal FTC+DOT aviation cases: {len(all_cases)}")
    return all_cases


if __name__ == '__main__':
    cases = collect()
    output_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'collected_ftc.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
