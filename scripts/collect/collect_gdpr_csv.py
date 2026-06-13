"""
collect_gdpr_csv.py - 从GDPR Fines Dataset (GitHub CSV) 采集航空相关案例

数据源: https://github.com/sandykramb/GDPR-fines-Dataset
字段: id, country, price, authority, date, org_fined, articleViolated, type, source, summary
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import csv
import io
import requests
from datetime import datetime
from collect.case_builder import (
    resolve_country_code, get_country_name_zh, generate_id,
    parse_date, parse_fine_amount, build_case
)
from collect.keyword_filter import matches_aviation, matches_privacy

CSV_URL = 'https://raw.githubusercontent.com/sandykramb/GDPR-fines-Dataset/main/GDPR%20Dataset.csv'
CASES_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cases.json')


def load_existing_case_ids():
    """Load existing case IDs for dedup."""
    if os.path.exists(CASES_FILE):
        with open(CASES_FILE, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        return {c['sourceUrl'] for c in cases if c.get('sourceUrl')}
    return set()


def fetch_and_filter():
    """Download CSV and filter for aviation + data privacy cases."""
    print("Downloading GDPR fines CSV...")
    r = requests.get(CSV_URL, timeout=60)
    r.raise_for_status()

    reader = csv.DictReader(io.StringIO(r.text))
    existing_urls = load_existing_case_ids()
    new_cases = []
    seen_orgs = set()

    for row in reader:
        org = row.get('org_fined', '') or ''
        summary = row.get('summary', '') or ''
        source_url = row.get('source', '') or ''
        price_str = row.get('price', '') or ''
        country = row.get('country', '') or ''
        authority = row.get('authority', '') or ''
        date_str = row.get('date', '') or ''
        article = row.get('articleViolated', '') or ''
        violation_type = row.get('type', '') or ''

        # Skip if no org name
        if not org.strip():
            continue

        # Check if this is an aviation entity
        if not matches_aviation(org + ' ' + summary):
            continue

        # Check if this is a data privacy case
        if not matches_privacy(summary + ' ' + violation_type + ' ' + article):
            continue

        # Dedup by source URL
        if source_url and source_url in existing_urls:
            continue

        # Dedup by org name (lowercased, stripped)
        org_key = org.lower().strip()
        if org_key in seen_orgs:
            continue
        seen_orgs.add(org_key)

        # Build case
        alpha2 = resolve_country_code(country)
        if not alpha2:
            alpha2 = 'XX'

        fine_amount, fine_currency = parse_fine_amount(price_str)

        # Clean summary (remove HTML tags)
        import re
        clean_summary = re.sub(r'<[^>]+>', '', summary).strip()
        if len(clean_summary) > 500:
            clean_summary = clean_summary[:497] + '...'

        case = build_case(
            country=country,
            case_type='admin',
            authority=authority or 'Unknown DPA',
            authority_short=authority.split('(')[-1].replace(')', '').strip() if '(' in authority else (authority[:20] if authority else 'DPA'),
            date=date_str or None,
            source_url=source_url or f"https://www.enforcementtracker.com/",
            case_name_en=f"{authority.split('(')[0].strip() if '(' in authority else authority} - {org}" if authority else f"DPA Fine against {org}",
            summary=clean_summary,
            tags=['GDPR'] + (['data-breach'] if 'breach' in summary.lower() else []) + (['aviation'] if matches_aviation(org) else []),
            fine_amount=fine_amount,
            fine_currency=fine_currency,
            sequence=len(new_cases) + 1,
        )

        new_cases.append(case)
        print(f"  Found: {org} ({alpha2}) - {price_str}")

    print(f"\nTotal aviation cases from GDPR CSV: {len(new_cases)}")
    return new_cases


def collect():
    """Main collection function (alias for fetch_and_filter)."""
    return fetch_and_filter()


if __name__ == '__main__':
    cases = fetch_and_filter()
    # Save to a separate file for review before merging
    output_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'collected_gdpr_csv.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
