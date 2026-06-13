"""
keyword_filter.py — 航空数据保护案例关键词过滤模块

按照data-source-catalog.md定义的关键词规则：
  航空实体关键词(OR) AND 数据/隐私关键词(OR)
"""

import re
from typing import List

# ── 航空实体关键词（OR组合） ──
AVIATION_KEYWORDS = [
    # English
    r'\baviation\b', r'\bairline\b', r'\bairlines\b', r'\baircraft\b',
    r'\bairport\b', r'\bairports\b', r'\bpassenger\b', r'\bflight\b',
    r'\bflights\b', r'\bcarrier\b', r'\bairway\b', r'\bairways\b',
    r'\baeronautic\b', r'\bGDS\b', r'\bbooking system\b',
    r'\bair transport\b', r'\bair travel\b', r'\bairline industry\b',
    # Specific airlines (common ones for filtering)
    r'\bBritish Airways\b', r'\bLufthansa\b', r'\bAir France\b',
    r'\bKLM\b', r'\bRyanair\b', r'\beasyJet\b', r'\bWizz Air\b',
    r'\bSAS\b', r'\bTAP\b', r'\bIberia\b', r'\bAlitalia\b',
    r'\bEmirates\b', r'\bQatar Airways\b', r'\bEtihad\b',
    r'\bSingapore Airlines\b', r'\bQantas\b', r'\bCathay Pacific\b',
    r'\bTurkish Airlines\b', r'\bPegasus\b',
    r'\bAmerican Airlines\b', r'\bDelta\b', r'\bUnited Airlines\b',
    r'\bSouthwest\b', r'\bJetBlue\b', r'\bAlaska Airlines\b',
    r'\bAir Canada\b', r'\bWestJet\b',
    r'\bAmadeus\b', r'\bSabre\b', r'\bTravelport\b',
    # Airport operators
    r'\bAENA\b', r'\bHeathrow\b', r'\bSchiphol\b', r'\bFraport\b',
    r'\bBrussels Airport\b', r'\bAeroport\b', r'\bAeroporto\b',
    # PNR specific
    r'\bPNR\b', r'\bpassenger name record\b',
    # Chinese
    r'航司', r'航空', r'航空公司', r'机场', r'航班', r'乘客',
]

# ── 数据/隐私关键词（OR组合） ──
DATA_PRIVACY_KEYWORDS = [
    # English
    r'\bdata protection\b', r'\bdata privacy\b', r'\bpersonal data\b',
    r'\bpersonal information\b', r'\bdata breach\b', r'\bdata breaches\b',
    r'\bGDPR\b', r'\bPIPL\b', r'\bCCPA\b', r'\bBIPA\b',
    r'\bprivacy\b', r'\bdata security\b', r'\bdata leak\b',
    r'\bidentity theft\b', r'\bcyber security\b', r'\bcybersecurity\b',
    r'\bsurveillance\b', r'\bbiometric\b', r'\bcookie\b', r'\bcookies\b',
    r'\bconsent\b', r'\bdata processing\b', r'\bdata controller\b',
    r'\bdata processor\b', r'\bfine\b', r'\bpenalty\b', r'\bsanction\b',
    r'\benforcement\b', r'\breprimand\b', r'\bundertaking\b',
    # French
    r'\bprotection des donn\b', r'\bdonnées personnelles\b',
    r'\bviolation de données\b',
    # Spanish
    r'\bprotección de datos\b', r'\bdatos personales\b',
    r'\bviolación de datos\b',
    # Chinese
    r'数据保护', r'个人信息', r'数据泄露', r'隐私',
]

# Pre-compile patterns
_AVIATION_PATTERNS = [re.compile(p, re.IGNORECASE) for p in AVIATION_KEYWORDS]
_PRIVACY_PATTERNS = [re.compile(p, re.IGNORECASE) for p in DATA_PRIVACY_KEYWORDS]


def matches_aviation(text: str) -> bool:
    """Check if text contains any aviation keyword."""
    if not text:
        return False
    return any(p.search(text) for p in _AVIATION_PATTERNS)


def matches_privacy(text: str) -> bool:
    """Check if text contains any data/privacy keyword."""
    if not text:
        return False
    return any(p.search(text) for p in _PRIVACY_PATTERNS)


def is_aviation_data_case(text: str) -> bool:
    """Check if text matches BOTH aviation AND data/privacy keywords."""
    return matches_aviation(text) and matches_privacy(text)


def filter_cases(cases: List[dict], text_fields: List[str] = None) -> List[dict]:
    """
    Filter a list of case dicts, keeping only those that match
    aviation AND data/privacy keywords.

    Args:
        cases: List of case dictionaries
        text_fields: Fields to search in (default: common case fields)

    Returns:
        Filtered list of case dictionaries
    """
    if text_fields is None:
        text_fields = ['caseName', 'caseNameEn', 'summary', 'tags', 'authority']

    filtered = []
    for case in cases:
        combined_text = ' '.join(
            str(case.get(f, '')) for f in text_fields if case.get(f)
        )
        if is_aviation_data_case(combined_text):
            filtered.append(case)

    return filtered


def get_aviation_matches(text: str) -> List[str]:
    """Return list of matched aviation keywords in text."""
    if not text:
        return []
    return [p.pattern for p in _AVIATION_PATTERNS if p.search(text)]


def get_privacy_matches(text: str) -> List[str]:
    """Return list of matched privacy keywords in text."""
    if not text:
        return []
    return [p.pattern for p in _PRIVACY_PATTERNS if p.search(text)]
