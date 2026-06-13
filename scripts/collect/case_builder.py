"""
case_builder.py - Case data builder utility

Convert raw data from various sources into the standard cases.json format.
"""

import re
from typing import Optional
from datetime import datetime

COUNTRY_CODE_MAP = {
    'Austria': 'AT', 'Belgium': 'BE', 'Bulgaria': 'BG', 'Croatia': 'HR',
    'Cyprus': 'CY', 'Czech Republic': 'CZ', 'Czechia': 'CZ',
    'Denmark': 'DK', 'Estonia': 'EE', 'Finland': 'FI', 'France': 'FR',
    'Germany': 'DE', 'Greece': 'GR', 'Hungary': 'HU', 'Ireland': 'IE',
    'Italy': 'IT', 'Latvia': 'LV', 'Lithuania': 'LT', 'Luxembourg': 'LU',
    'Malta': 'MT', 'Netherlands': 'NL', 'Norway': 'NO', 'Poland': 'PL',
    'Portugal': 'PT', 'Romania': 'RO', 'Slovakia': 'SK', 'Slovenia': 'SI',
    'Spain': 'ES', 'Sweden': 'SE', 'United Kingdom': 'GB', 'UK': 'GB',
    'United States': 'US', 'USA': 'US', 'Canada': 'CA',
    'Australia': 'AU', 'Singapore': 'SG', 'India': 'IN',
    'Brazil': 'BR', 'South Korea': 'KR', 'Turkey': 'TR',
    'China': 'CN', 'Hong Kong': 'HK',
}

COUNTRY_NAMES_ZH = {
    'AT': '\u5965\u5730\u5229', 'AU': '\u6fb3\u5927\u5229\u4e9a', 'BE': '\u6bd4\u5229\u65f6',
    'BR': '\u5df4\u897f', 'CA': '\u52a0\u62ff\u5927', 'CN': '\u4e2d\u56fd',
    'DE': '\u5fb7\u56fd', 'DK': '\u4e39\u9ea6', 'ES': '\u897f\u73ed\u7259',
    'FI': '\u82ac\u5170', 'FR': '\u6cd5\u56fd', 'GB': '\u82f1\u56fd',
    'GR': '\u5e0c\u814a', 'HK': '\u4e2d\u56fd\u9999\u6e2f', 'HR': '\u514b\u7f57\u5730\u4e9a',
    'HU': '\u5308\u7259\u5229', 'IE': '\u7231\u5c14\u5170', 'IN': '\u5370\u5ea6',
    'IT': '\u610f\u5927\u5229', 'KR': '\u97e9\u56fd', 'LT': '\u7acb\u9676\u5b9b',
    'LU': '\u5362\u68ee\u5821', 'NL': '\u8377\u5170', 'NO': '\u632a\u5a01',
    'PL': '\u6ce2\u5170', 'PT': '\u8461\u8404\u7259', 'RO': '\u7f57\u9a6c\u5c3c\u4e9a',
    'SE': '\u745e\u5178', 'SG': '\u65b0\u52a0\u5761', 'TR': '\u571f\u8033\u5176',
    'US': '\u7f8e\u56fd',
}


def resolve_country_code(country_input):
    """Resolve various country name formats to ISO alpha-2 code."""
    if not country_input:
        return None
    if len(country_input) == 2 and country_input.isalpha():
        return country_input.upper()
    return COUNTRY_CODE_MAP.get(country_input.strip(), None)


def get_country_name_zh(alpha2):
    """Get Chinese country name from ISO alpha-2 code."""
    return COUNTRY_NAMES_ZH.get(alpha2, alpha2)


def generate_id(country, case_type, sequence):
    """Generate case ID: {country}-{type}-{NNN}"""
    return f"{country}-{case_type}-{sequence:03d}"


def parse_date(date_str):
    """Parse various date formats into ISO 8601 (YYYY-MM-DD)."""
    if not date_str:
        return None
    date_str = str(date_str).strip()
    # DD/MM/YYYY
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            pass
    # YYYY-MM-DD
    m = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # YYYY/MM/DD
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # Month DD, YYYY
    for fmt in ['%B %d, %Y', '%d %B %Y']:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None


def parse_fine_amount(fine_str):
    """Parse fine amount string -> (amount: float, currency: str)."""
    if not fine_str:
        return (None, None)
    fine_str = str(fine_str).strip()
    currency = None
    for cur in ['EUR', 'GBP', 'USD', 'SEK', 'NOK', 'DKK', 'PLN', 'AUD', 'CAD', 'KRW', 'BRL', 'CNY', 'INR', 'SGD']:
        if cur in fine_str:
            currency = cur
            break
    # Millions suffix
    m = re.search(r'([\d,]+\.?\d*)\s*M', fine_str, re.IGNORECASE)
    if m:
        amount = float(m.group(1).replace(',', '')) * 1_000_000
        return (amount, currency)
    # Regular number
    m = re.search(r'([\d,]+\.?\d*)', fine_str)
    if m:
        amount = float(m.group(1).replace(',', ''))
        return (amount, currency)
    return (None, None)


def build_case(country, case_type, authority, authority_short, date, source_url,
               case_name_en, case_name='', summary='', tags=None,
               fine_amount=None, fine_currency=None, sector='Aviation', sequence=1):
    """Build a standardized case dictionary."""
    alpha2 = resolve_country_code(country)
    if not alpha2:
        alpha2 = country
    return {
        'id': generate_id(alpha2, case_type, sequence),
        'caseName': case_name or case_name_en,
        'caseNameEn': case_name_en,
        'country': alpha2,
        'caseType': case_type,
        'authority': authority,
        'authorityShort': authority_short,
        'date': parse_date(date) or date,
        'sourceUrl': source_url,
        'summary': summary,
        'tags': tags or ['aviation', 'data-protection'],
        'fineAmount': fine_amount,
        'fineCurrency': fine_currency,
        'sector': sector,
        'lastVerified': datetime.now().strftime('%Y-%m-%d'),
    }
