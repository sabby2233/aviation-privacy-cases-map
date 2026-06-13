"""
merge_and_generate.py - 合并所有采集结果，去重，生成最终 cases.json + countries.json

运行方式：
    cd c:/Users/qwesz/WorkBuddy/2026-06-12-15-13-12
    python scripts/collect/merge_and_generate.py

流程：
1. 运行所有采集器（ICO, CNIL/AEPD, FTC, CourtListener, GDPR CSV）
2. 与现有 cases.json 合并
3. 去重（URL精确匹配 + 案件名相似度）
4. 重新分配ID（按国家+类型+序号）
5. 生成 countries.json（聚合统计）
6. 写回 data/cases.json 和 data/countries.json
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Fix Windows console encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import re
from datetime import datetime
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
CASES_FILE = os.path.join(DATA_DIR, 'cases.json')
COUNTRIES_FILE = os.path.join(DATA_DIR, 'countries.json')

COUNTRY_NAMES_ZH = {
    'AT': '奥地利', 'AU': '澳大利亚', 'BE': '比利时', 'BR': '巴西',
    'CA': '加拿大', 'CH': '瑞士', 'CN': '中国', 'CY': '塞浦路斯',
    'CZ': '捷克', 'DE': '德国', 'DK': '丹麦', 'EE': '爱沙尼亚',
    'ES': '西班牙', 'FI': '芬兰', 'FR': '法国', 'GB': '英国',
    'GR': '希腊', 'HK': '中国香港', 'HR': '克罗地亚', 'HU': '匈牙利',
    'IE': '爱尔兰', 'IN': '印度', 'IT': '意大利', 'JP': '日本',
    'KR': '韩国', 'LT': '立陶宛', 'LU': '卢森堡', 'LV': '拉脱维亚',
    'MT': '马耳他', 'NL': '荷兰', 'NO': '挪威', 'PL': '波兰',
    'PT': '葡萄牙', 'RO': '罗马尼亚', 'SE': '瑞典', 'SG': '新加坡',
    'SI': '斯洛文尼亚', 'SK': '斯洛伐克', 'TR': '土耳其', 'US': '美国',
}

COUNTRY_NAMES_EN = {
    'AT': 'Austria', 'AU': 'Australia', 'BE': 'Belgium', 'BR': 'Brazil',
    'CA': 'Canada', 'CH': 'Switzerland', 'CN': 'China', 'CY': 'Cyprus',
    'CZ': 'Czech Republic', 'DE': 'Germany', 'DK': 'Denmark', 'EE': 'Estonia',
    'ES': 'Spain', 'FI': 'Finland', 'FR': 'France', 'GB': 'United Kingdom',
    'GR': 'Greece', 'HK': 'Hong Kong, China', 'HR': 'Croatia', 'HU': 'Hungary',
    'IE': 'Ireland', 'IN': 'India', 'IT': 'Italy', 'JP': 'Japan',
    'KR': 'South Korea', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia',
    'MT': 'Malta', 'NL': 'Netherlands', 'NO': 'Norway', 'PL': 'Poland',
    'PT': 'Portugal', 'RO': 'Romania', 'SE': 'Sweden', 'SG': 'Singapore',
    'SI': 'Slovenia', 'SK': 'Slovakia', 'TR': 'Turkey', 'US': 'United States',
}


def normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, strip punctuation)."""
    if not text:
        return ''
    t = text.lower()
    t = re.sub(r'[^\w\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def is_duplicate(case_a: dict, case_b: dict) -> bool:
    """Check if two cases are duplicates."""
    # Exact URL match
    url_a = case_a.get('sourceUrl', '')
    url_b = case_b.get('sourceUrl', '')
    if url_a and url_b and url_a == url_b:
        return True

    # Same country + similar name
    if case_a.get('country') != case_b.get('country'):
        return False

    name_a = normalize_text(case_a.get('caseName', '') or case_a.get('caseNameEn', ''))
    name_b = normalize_text(case_b.get('caseName', '') or case_b.get('caseNameEn', ''))

    if not name_a or not name_b:
        return False

    # High similarity check: if one name contains the other
    if name_a in name_b or name_b in name_a:
        return True

    # Jaccard similarity on word sets
    words_a = set(name_a.split())
    words_b = set(name_b.split())
    if not words_a or not words_b:
        return False
    
    intersection = words_a & words_b
    union = words_a | words_b
    similarity = len(intersection) / len(union)
    
    return similarity > 0.75


def dedup_cases(cases: list) -> list:
    """Remove duplicate cases, keeping the one with more complete data."""
    unique = []
    for case in cases:
        found_dup = False
        for i, existing in enumerate(unique):
            if is_duplicate(case, existing):
                found_dup = True
                # Keep the one with more fields filled
                score_case = sum(1 for v in case.values() if v)
                score_existing = sum(1 for v in existing.values() if v)
                if score_case > score_existing:
                    unique[i] = case  # Replace with richer version
                break
        if not found_dup:
            unique.append(case)
    return unique


def assign_ids(cases: list) -> list:
    """Reassign sequential IDs by country+type."""
    # Group by (country, caseType)
    groups = defaultdict(list)
    for case in cases:
        country = case.get('country', 'XX')
        case_type = case.get('caseType', 'admin')
        # Map type: admin→A, court→C
        type_code = 'A' if case_type == 'admin' else 'C'
        groups[(country, type_code)].append(case)

    result = []
    for (country, type_code), group in sorted(groups.items()):
        # Sort by date within group
        group.sort(key=lambda c: c.get('date') or '0000-00-00')
        for i, case in enumerate(group, start=1):
            case = dict(case)
            case['id'] = f"{country}-{type_code}-{i:03d}"
            # Ensure countryName is set
            if not case.get('countryName'):
                case['countryName'] = COUNTRY_NAMES_ZH.get(country, country)
            result.append(case)

    return result


def generate_countries_json(cases: list) -> dict:
    """Generate countries.json from cases list."""
    country_data = defaultdict(lambda: {
        'cases': [],
        'totalCases': 0,
        'adminCases': 0,
        'courtCases': 0,
        'latestDate': '',
        'authorities': [],
    })

    for case in cases:
        country = case.get('country', '')
        if not country:
            continue
        data = country_data[country]
        case_type = case.get('caseType', 'admin')
        
        data['cases'].append({
            'id': case.get('id', ''),
            'caseName': case.get('caseName', ''),
            'caseNameEn': case.get('caseNameEn', ''),
            'date': case.get('date', ''),
            'caseType': case_type,
            'authority': case.get('authority', ''),
            'authorityShort': case.get('authorityShort', ''),
            'sourceUrl': case.get('sourceUrl', ''),
            'summary': case.get('summary', ''),
            'tags': case.get('tags', []),
            'fineAmount': case.get('fineAmount'),
            'fineCurrency': case.get('fineCurrency'),
        })
        data['totalCases'] += 1
        if case_type == 'admin':
            data['adminCases'] += 1
        else:
            data['courtCases'] += 1
        
        date = case.get('date') or ''
        if date and date > data['latestDate']:
            data['latestDate'] = date
        
        auth = case.get('authorityShort', '')
        if auth and auth not in data['authorities']:
            data['authorities'].append(auth)

    # Build final structure
    result = {}
    for country, data in sorted(country_data.items()):
        result[country] = {
            'code': country,
            'name': COUNTRY_NAMES_ZH.get(country, country),
            'nameEn': COUNTRY_NAMES_EN.get(country, country),
            'totalCases': data['totalCases'],
            'adminCases': data['adminCases'],
            'courtCases': data['courtCases'],
            'latestDate': data['latestDate'],
            'authorities': sorted(data['authorities']),
            'cases': sorted(data['cases'], key=lambda c: c.get('date') or '0000-00-00', reverse=True),
        }

    return {
        'version': datetime.now().strftime('%Y%m%d'),
        'generatedAt': datetime.now().isoformat(),
        'totalCases': len(cases),
        'totalCountries': len(result),
        'countries': result,
    }


def run_collectors():
    """Run all collection scripts and return combined new cases."""
    all_new = []
    
    collectors = [
        ('ICO', 'collect_ico', 'collect'),
        ('CNIL+AEPD', 'collect_cnil_aepd', 'collect'),
        ('FTC', 'collect_ftc', 'collect'),
        ('CourtListener', 'collect_courtlistener', 'collect'),
        ('GDPR CSV', 'collect_gdpr_csv', 'collect'),
    ]
    
    for name, module_name, func_name in collectors:
        print(f"\n{'='*50}")
        print(f"Running {name} collector...")
        print('='*50)
        try:
            mod = __import__(f'collect.{module_name}', fromlist=[func_name])
            func = getattr(mod, func_name)
            cases = func()
            print(f"  → {len(cases)} cases collected")
            all_new.extend(cases)
        except Exception as e:
            print(f"  [FAIL] {name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    return all_new


def main():
    print("=" * 60)
    print("  Merge & Generate: Aviation Data Protection Cases")
    print("=" * 60)

    # 1. Load existing cases
    existing_cases = []
    if os.path.exists(CASES_FILE):
        with open(CASES_FILE, 'r', encoding='utf-8') as f:
            existing_cases = json.load(f)
        print(f"\n[Load] Existing cases: {len(existing_cases)}")
    else:
        print("\n[Load] No existing cases.json, starting fresh.")

    # 2. Run all collectors
    new_cases = run_collectors()
    print(f"\n[Collect] Total new cases from collectors: {len(new_cases)}")

    # 3. Merge
    all_cases = existing_cases + new_cases
    print(f"[Merge] Total before dedup: {len(all_cases)}")

    # 4. Dedup
    deduped = dedup_cases(all_cases)
    print(f"[Dedup] After dedup: {len(deduped)} (removed {len(all_cases) - len(deduped)} duplicates)")

    # 5. Assign IDs
    final_cases = assign_ids(deduped)
    print(f"[IDs] Assigned IDs to {len(final_cases)} cases")

    # Print summary by country
    print("\n[Summary] Cases by country:")
    country_counts = defaultdict(int)
    for c in final_cases:
        country_counts[c.get('country', 'XX')] += 1
    for country, count in sorted(country_counts.items(), key=lambda x: -x[1]):
        print(f"  {country}: {count}")

    # 6. Save cases.json
    with open(CASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_cases, f, indent=2, ensure_ascii=False)
    print(f"\n[Save] cases.json: {len(final_cases)} cases → {CASES_FILE}")

    # 7. Generate and save countries.json
    countries_data = generate_countries_json(final_cases)
    with open(COUNTRIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(countries_data, f, indent=2, ensure_ascii=False)
    print(f"[Save] countries.json: {len(countries_data['countries'])} countries → {COUNTRIES_FILE}")

    print("\n✓ Done!")
    return final_cases, countries_data


if __name__ == '__main__':
    main()
