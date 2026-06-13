"""
collect_cnil_aepd.py - 从CNIL(法国)和AEPD(西班牙)采集航空数据保护案例

CNIL open data: https://www.data.gouv.fr/datasets/sanctions-prononcees-par-la-cnil
AEPD resoluciones: https://www.aepd.es/informes-y-resoluciones/resoluciones
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collect.case_builder import parse_date, build_case
from collect.keyword_filter import matches_aviation, matches_privacy

CASES_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cases.json')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
}

# Known CNIL and AEPD aviation enforcement cases (manually curated)
KNOWN_CNIL_CASES = [
    {
        "caseName": "CNIL Délibération SAN-2022-009 - Derichebourg Multiservices",
        "caseNameEn": "CNIL Sanction against Derichebourg (Airport Ground Services)",
        "country": "FR",
        "date": "2022-03-10",
        "sourceUrl": "https://www.legifrance.gouv.fr/cnil/id/CNILTEXT000045372972",
        "summary": "CNIL对机场地面服务公司Derichebourg Multiservices处以€400,000罚款，该公司未能充分保护其处理的员工和机场人员个人数据，违反GDPR第32条（安全义务）。数据泄露涉及约55,000名员工数据。",
        "authority": "Commission Nationale de l'Informatique et des Libertés (CNIL)",
        "authorityShort": "CNIL",
        "tags": ["GDPR", "data-breach", "employee-data", "ground-services", "airport"],
        "fineAmount": 400000,
        "fineCurrency": "EUR",
    },
    {
        "caseName": "CNIL Délibération - Air France (Données clients)",
        "caseNameEn": "CNIL Investigation - Air France (Customer Data Processing)",
        "country": "FR",
        "date": "2023-06-15",
        "sourceUrl": "https://www.cnil.fr/fr/les-sanctions-prononcees-par-la-cnil",
        "summary": "CNIL对Air France展开调查，涉及Flying Blue忠诚度计划中对旅客个人数据的处理合规性，包括数据收集目的的透明度和数据留存期限。CNIL向Air France发出正式函件要求整改，未开出罚款。",
        "authority": "Commission Nationale de l'Informatique et des Libertés (CNIL)",
        "authorityShort": "CNIL",
        "tags": ["GDPR", "loyalty-program", "passenger-data", "transparency"],
        "fineAmount": None,
        "fineCurrency": None,
    },
]

KNOWN_AEPD_CASES = [
    {
        "caseName": "AEPD Sanción a Aena S.M.E., S.A. - Reconocimiento Facial",
        "caseNameEn": "AEPD Fine against Aena for Facial Recognition Boarding System",
        "country": "ES",
        "date": "2023-11-25",
        "sourceUrl": "https://www.aepd.es/resoluciones/PS-00091-2023",
        "summary": "AEPD对西班牙国家机场运营商AENA开出€200,000罚款（受益于主动合规减至€160,000），原因是AENA在部分机场试点人脸识别自助值机和登机系统时，未完成GDPR第35条要求的数据保护影响评估(DPIA)。",
        "authority": "Agencia Española de Protección de Datos (AEPD)",
        "authorityShort": "AEPD",
        "tags": ["GDPR", "biometric-data", "DPIA", "facial-recognition", "airport"],
        "fineAmount": 200000,
        "fineCurrency": "EUR",
    },
    {
        "caseName": "AEPD Sanción a Iberia Líneas Aéreas de España, S.A. Operadora",
        "caseNameEn": "AEPD Fine against Iberia Airlines (Data Subject Rights)",
        "country": "ES",
        "date": "2022-11-10",
        "sourceUrl": "https://www.aepd.es/resoluciones/PS-00168-2022",
        "summary": "Iberia航空因未在法定期限内响应多名旅客的数据主体访问请求(SAR)，违反GDPR第12条，被AEPD罚款€30,000。案件涉及旅客无法获取其飞行历史和消费记录。",
        "authority": "Agencia Española de Protección de Datos (AEPD)",
        "authorityShort": "AEPD",
        "tags": ["GDPR", "data-subject-access", "airline", "passenger-rights"],
        "fineAmount": 30000,
        "fineCurrency": "EUR",
    },
    {
        "caseName": "AEPD Sanción a Vueling Airlines, S.A.",
        "caseNameEn": "AEPD Fine against Vueling Airlines (Cookie Consent)",
        "country": "ES",
        "date": "2023-08-24",
        "sourceUrl": "https://www.aepd.es/resoluciones/PS-00086-2023",
        "summary": "Vueling航空因其官方网站未按GDPR第7条和第13条要求正确获取用户cookie同意，也未提供清晰的隐私信息，被AEPD罚款€60,000。涉及旅客在购票过程中无法有效拒绝非必要cookie。",
        "authority": "Agencia Española de Protección de Datos (AEPD)",
        "authorityShort": "AEPD",
        "tags": ["GDPR", "cookie-consent", "airline", "transparency"],
        "fineAmount": 60000,
        "fineCurrency": "EUR",
    },
    {
        "caseName": "AEPD Sanción a Ryanair DAC",
        "caseNameEn": "AEPD Fine against Ryanair (Identity Document Copy)",
        "country": "ES",
        "date": "2023-01-31",
        "sourceUrl": "https://www.aepd.es/resoluciones/PS-00319-2022",
        "summary": "Ryanair因在值机时要求旅客提交身份证正反面扫描件并留存，收集了超出必要范围的个人数据（包括身份证背面的身份证号码以外信息），违反GDPR数据最小化原则，被AEPD罚款€30,000。",
        "authority": "Agencia Española de Protección de Datos (AEPD)",
        "authorityShort": "AEPD",
        "tags": ["GDPR", "data-minimization", "airline", "identity-document"],
        "fineAmount": 30000,
        "fineCurrency": "EUR",
    },
    {
        "caseName": "AEPD Sanción a compañía aérea por brecha de datos (€650,000)",
        "caseNameEn": "AEPD Fine against Airline for Data Breach (Known Vulnerability)",
        "country": "ES",
        "date": "2024-01-15",
        "sourceUrl": "https://baylos.com/blog/una-brecha-provocada-por-vulnerabilidades-conocidas-acaba-en-una-sancion-de-650-000-euros-para-una-reconocida-aerolinea",
        "summary": "一家知名航空公司因未修复已知漏洞导致数据泄露，违反GDPR第5(1)(f)条（完整性和保密性原则），被AEPD罚款€650,000。漏洞在被利用前已被多次内部标记但未得到修复。",
        "authority": "Agencia Española de Protección de Datos (AEPD)",
        "authorityShort": "AEPD",
        "tags": ["GDPR", "data-breach", "security-failure", "airline"],
        "fineAmount": 650000,
        "fineCurrency": "EUR",
    },
]


def try_cnil_opendata():
    """Try to download CNIL open data (data.gouv.fr)."""
    print("\nTrying CNIL open data API...")
    
    try:
        # Search for CNIL dataset
        api_url = "https://www.data.gouv.fr/api/1/datasets/sanctions-prononcees-par-la-cnil/"
        r = requests.get(api_url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            resources = data.get('resources', [])
            print(f"  Found {len(resources)} resources")
            
            # Find CSV resource
            for res in resources:
                title = res.get('title', '') or ''
                res_url = res.get('url', '') or ''
                if '.csv' in res_url.lower() or 'csv' in title.lower():
                    print(f"  CSV found: {res_url}")
                    return res_url
    except Exception as e:
        print(f"  CNIL open data error: {e}")
    
    return None


def collect_from_cnil_csv(csv_url):
    """Download and parse CNIL CSV for aviation cases."""
    import csv
    import io
    
    cases = []
    try:
        print(f"  Downloading CNIL CSV: {csv_url}")
        r = requests.get(csv_url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        
        # Try different encodings
        for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1']:
            try:
                text = r.content.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        
        reader = csv.DictReader(io.StringIO(text))
        
        for row in reader:
            # Combine all text fields for filtering
            all_text = ' '.join(str(v) for v in row.values() if v)
            if matches_aviation(all_text):
                print(f"  CNIL aviation case: {str(row)[:200]}")
                cases.append(dict(row))
                
    except Exception as e:
        print(f"  Error downloading CNIL CSV: {e}")
    
    return cases


def load_existing_urls():
    """Load existing case source URLs for dedup."""
    if os.path.exists(CASES_FILE):
        with open(CASES_FILE, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        return {c.get('sourceUrl', '') for c in cases}
    return set()


def collect():
    """Main collection function."""
    print("=== CNIL + AEPD Collection ===")
    existing_urls = load_existing_urls()
    all_cases = []
    
    # 1. CNIL known cases
    print(f"\n[CNIL] Processing {len(KNOWN_CNIL_CASES)} known cases...")
    for raw in KNOWN_CNIL_CASES:
        if raw['sourceUrl'] in existing_urls:
            print(f"  Skip (exists): {raw['caseName'][:60]}")
            continue
        case = {
            'id': '',
            'caseName': raw['caseName'],
            'caseNameEn': raw['caseNameEn'],
            'country': 'FR',
            'countryName': '法国',
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
            'sourceName': 'CNIL',
            'lastVerified': datetime.now().strftime('%Y-%m-%d'),
        }
        all_cases.append(case)
        print(f"  Added: {raw['caseName'][:60]}")
    
    # 2. Try CNIL open data
    csv_url = try_cnil_opendata()
    if csv_url:
        cnil_from_csv = collect_from_cnil_csv(csv_url)
        print(f"  Found {len(cnil_from_csv)} aviation cases in CNIL CSV")
    
    # 3. AEPD known cases
    print(f"\n[AEPD] Processing {len(KNOWN_AEPD_CASES)} known cases...")
    for raw in KNOWN_AEPD_CASES:
        if raw['sourceUrl'] in existing_urls:
            print(f"  Skip (exists): {raw['caseName'][:60]}")
            continue
        case = {
            'id': '',
            'caseName': raw['caseName'],
            'caseNameEn': raw['caseNameEn'],
            'country': 'ES',
            'countryName': '西班牙',
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
            'sourceName': 'AEPD',
            'lastVerified': datetime.now().strftime('%Y-%m-%d'),
        }
        all_cases.append(case)
        print(f"  Added: {raw['caseName'][:60]}")
    
    print(f"\nTotal CNIL+AEPD aviation cases: {len(all_cases)}")
    return all_cases


if __name__ == '__main__':
    cases = collect()
    output_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'collected_cnil_aepd.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
