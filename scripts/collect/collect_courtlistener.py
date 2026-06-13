"""
collect_courtlistener.py - 从CourtListener API采集航空数据隐私案例

API文档: https://www.courtlistener.com/api/rest/v3/
认证: Token-based (Bearer token in header)
搜索端点: /api/rest/v3/search/?type=o&q=<query>

无token时也可搜索，但有更严格的速率限制。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import re
import time
import requests
from datetime import datetime
from collect.case_builder import (
    resolve_country_code, get_country_name_zh, generate_id,
    parse_date, parse_fine_amount, build_case
)
from collect.keyword_filter import matches_aviation, matches_privacy

CASES_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cases.json')
BASE_URL = "https://www.courtlistener.com/api/rest/v3/"

# CourtListener API token (optional, needed for higher rate limits)
# Set env var CL_API_TOKEN or place token here
API_TOKEN = os.environ.get('CL_API_TOKEN', '')

# Targeted aviation + privacy search queries
SEARCH_QUERIES = [
    "airline privacy data breach",
    "airline biometric BIPA",
    "aviation data protection personal information",
    "airline passenger data surveillance",
    "airline data security class action",
    "airport facial recognition privacy",
    "PNR passenger name record privacy",
]


def get_headers():
    """Build request headers."""
    headers = {"Accept": "application/json", "User-Agent": "aviation-privacy-map/1.0"}
    if API_TOKEN:
        headers["Authorization"] = f"Token {API_TOKEN}"
    return headers


def search_opinions(query, page=1):
    """Search CourtListener opinion database."""
    params = {
        "type": "o",
        "q": query,
        "order_by": "score desc",
        "stat_Precedential": "on",
        "stat_Non-Precedential": "on",
        "page": page,
    }
    url = f"{BASE_URL}search/"
    r = requests.get(url, params=params, headers=get_headers(), timeout=30)
    if r.status_code == 429:
        print(f"  Rate limited, waiting 60s...")
        time.sleep(60)
        r = requests.get(url, params=params, headers=get_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def load_existing_urls():
    """Load existing case source URLs for dedup."""
    if os.path.exists(CASES_FILE):
        with open(CASES_FILE, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        return {c.get('sourceUrl', '') for c in cases}
    return set()


def extract_cases_from_results(results, existing_urls, seen_ids):
    """Extract aviation privacy cases from search results."""
    new_cases = []

    for result in results.get('results', []):
        case_name = result.get('caseName', '') or ''
        snippet = result.get('snippet', '') or result.get('text', '') or ''
        court = result.get('court', '') or result.get('court_id', '') or ''
        docket_url = result.get('absolute_url', '') or ''
        date_filed = result.get('dateFiled', '') or result.get('dateArgued', '') or ''

        # Build full URL
        if docket_url and not docket_url.startswith('http'):
            docket_url = f"https://www.courtlistener.com{docket_url}"

        combined_text = case_name + ' ' + snippet

        # Filter: must involve aviation AND privacy
        if not matches_aviation(combined_text):
            continue
        if not matches_privacy(combined_text):
            continue

        # Dedup by URL
        if docket_url in existing_urls:
            continue
        case_id = result.get('id', '') or result.get('cluster_id', '')
        if case_id in seen_ids:
            continue
        if case_id:
            seen_ids.add(str(case_id))

        # Clean snippet (remove HTML)
        clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
        if len(clean_snippet) > 500:
            clean_snippet = clean_snippet[:497] + '...'

        tags = ['privacy', 'court-case', 'US']
        if 'breach' in combined_text.lower():
            tags.append('data-breach')
        if 'biometric' in combined_text.lower() or 'BIPA' in combined_text:
            tags.append('biometric')
        if 'class action' in combined_text.lower():
            tags.append('class-action')
        if 'BIPA' in combined_text:
            tags.append('BIPA')
        if 'facial recognition' in combined_text.lower():
            tags.append('facial-recognition')

        case = {
            'id': f"US-C-CL-{case_id}",
            'caseName': case_name,
            'caseNameEn': case_name,
            'country': 'US',
            'countryName': '美国',
            'caseType': 'court',
            'authority': f"U.S. Court ({court})" if court else "U.S. Federal Court",
            'authorityShort': court.upper()[:20] if court else 'US Court',
            'date': parse_date(date_filed) or date_filed,
            'sourceUrl': docket_url,
            'summary': clean_snippet if clean_snippet else f"Case: {case_name}",
            'tags': tags,
            'fineAmount': None,
            'fineCurrency': None,
            'sector': 'Aviation',
            'sourceName': 'CourtListener',
            'lastVerified': datetime.now().strftime('%Y-%m-%d'),
        }
        new_cases.append(case)
        print(f"  Found: {case_name[:80]} ({date_filed})")

    return new_cases


def collect():
    """Main collection function."""
    print("=== CourtListener API Collection ===")
    existing_urls = load_existing_urls()
    seen_ids = set()
    all_cases = []

    for query in SEARCH_QUERIES:
        print(f"\nQuery: '{query}'")
        try:
            data = search_opinions(query)
            total = data.get('count', 0)
            print(f"  Total results: {total}")

            cases = extract_cases_from_results(data, existing_urls, seen_ids)
            all_cases.extend(cases)

            # Only fetch page 2 if we got results and they look relevant
            if total > 20 and len(cases) > 0:
                time.sleep(2)
                data2 = search_opinions(query, page=2)
                cases2 = extract_cases_from_results(data2, existing_urls, seen_ids)
                all_cases.extend(cases2)

            time.sleep(2)  # Rate limiting
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(5)
            continue

    print(f"\nTotal new aviation privacy cases: {len(all_cases)}")
    return all_cases


if __name__ == '__main__':
    cases = collect()
    output_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'collected_courtlistener.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
