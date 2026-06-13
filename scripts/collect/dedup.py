"""
dedup.py — 案例去重模块

去重规则（按technical-spec.md第7章）：
1. sourceUrl 精确匹配 → 视为同一案例
2. caseName 归一化匹配（小写+去除标点空格） → 视为同一案例
"""

import re
import unicodedata
from typing import List, Dict, Tuple


def normalize_case_name(name: str) -> str:
    """
    Normalize a case name for comparison:
    - Lowercase
    - Remove accents/diacritics
    - Remove all non-alphanumeric characters
    - Collapse whitespace
    """
    if not name:
        return ''
    # Normalize unicode (NFD decomposes, then remove combining marks)
    nfkd = unicodedata.normalize('NFD', name)
    ascii_only = ''.join(c for c in nfkd if not unicodedata.combining(c))
    # Lowercase
    ascii_only = ascii_only.lower()
    # Remove all non-alphanumeric
    ascii_only = re.sub(r'[^a-z0-9]', '', ascii_only)
    return ascii_only


def find_duplicates(cases: List[dict]) -> List[Tuple[int, int, str]]:
    """
    Find duplicate pairs in a list of cases.

    Returns:
        List of (idx1, idx2, reason) tuples where idx1 < idx2
    """
    duplicates = []

    # Build indices
    url_index: Dict[str, int] = {}
    name_index: Dict[str, int] = {}

    for i, case in enumerate(cases):
        # 1. sourceUrl exact match
        url = case.get('sourceUrl', '').strip()
        if url:
            if url in url_index:
                duplicates.append((url_index[url], i, f'sourceUrl match: {url}'))
            else:
                url_index[url] = i

        # 2. caseName normalized match
        name = case.get('caseNameEn', '') or case.get('caseName', '')
        norm_name = normalize_case_name(name)
        if norm_name and len(norm_name) > 5:  # Avoid trivial short matches
            if norm_name in name_index:
                dup_idx = name_index[norm_name]
                # Only flag if different sourceUrls (otherwise already caught by rule 1)
                if cases[dup_idx].get('sourceUrl') != url:
                    duplicates.append((dup_idx, i, f'caseName match: {name}'))
            else:
                name_index[norm_name] = i

    return duplicates


def deduplicate(cases: List[dict], prefer: str = 'later') -> List[dict]:
    """
    Remove duplicates from a list of cases.

    Args:
        cases: List of case dictionaries
        prefer: When duplicates found, keep 'earlier' (lower index) or 'later' (higher index)
                'later' is useful when newer data is more complete

    Returns:
        Deduplicated list of case dictionaries
    """
    duplicates = find_duplicates(cases)
    remove_indices = set()

    for idx1, idx2, reason in duplicates:
        if prefer == 'later':
            remove_indices.add(idx1)
        else:
            remove_indices.add(idx2)

    return [c for i, c in enumerate(cases) if i not in remove_indices]


def merge_existing(new_cases: List[dict], existing_cases: List[dict]) -> List[dict]:
    """
    Merge new cases with existing cases, deduplicating.

    Strategy:
    - If sourceUrl matches existing → skip new (keep existing, which may have manual edits)
    - If caseName matches existing → skip new
    - Otherwise → add new case

    Returns:
        Merged list of cases (existing + truly new)
    """
    # Build existing indices
    existing_urls = set()
    existing_names = set()

    for case in existing_cases:
        url = case.get('sourceUrl', '').strip()
        if url:
            existing_urls.add(url)

        name = case.get('caseNameEn', '') or case.get('caseName', '')
        norm = normalize_case_name(name)
        if norm and len(norm) > 5:
            existing_names.add(norm)

    # Filter new cases
    truly_new = []
    for case in new_cases:
        # Check URL
        url = case.get('sourceUrl', '').strip()
        if url and url in existing_urls:
            continue

        # Check name
        name = case.get('caseNameEn', '') or case.get('caseName', '')
        norm = normalize_case_name(name)
        if norm and len(norm) > 5 and norm in existing_names:
            continue

        truly_new.append(case)

    return existing_cases + truly_new
