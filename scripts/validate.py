#!/usr/bin/env python3
"""
validate.py - 数据校验脚本
检查 cases.json 的字段完整性、ID格式、日期有效性等
"""

import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

# ISO 3166-1 alpha-2 常用国家代码（含HK等特殊代码）
VALID_COUNTRY_CODES = {
    "US", "GB", "DE", "FR", "ES", "IT", "NL", "IE", "AT", "BE", "PT", "GR",
    "PL", "CZ", "RO", "HU", "SE", "DK", "FI", "NO", "SK", "BG", "HR", "SI",
    "LU", "MT", "CY", "EE", "LV", "LT", "EU", "CH", "TR", "RU", "UA",
    "CN", "JP", "KR", "SG", "AU", "NZ", "IN", "BR", "CA", "MX", "AR",
    "ZA", "AE", "SA", "IL", "TH", "MY", "ID", "PH", "VN", "TW", "HK", "MO"
}

ID_PATTERN = re.compile(r'^[A-Z]{2}-[CA]-\d{3}$')
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
URL_PATTERN = re.compile(r'^https?://.+')

REQUIRED_FIELDS = ["id", "caseName", "country", "countryName", "caseType", "authority", "date", "sourceUrl", "sourceName", "lastVerified"]

errors = []
warnings = []

def validate_case(case: dict, idx: int):
    """验证单个案例"""
    case_id = case.get("id", f"<missing-{idx}>")

    # 1. 必填字段检查
    for field in REQUIRED_FIELDS:
        if field not in case or not case[field]:
            errors.append(f"[{case_id}] Required field '{field}' is missing or empty")

    # 2. ID格式检查
    if "id" in case and case["id"]:
        if not ID_PATTERN.match(case["id"]):
            errors.append(f"[{case_id}] ID format invalid: '{case['id']}'. Expected: {{ISO2}}-{{C|A}}-{{NNN}}")

    # 3. 日期有效性
    if "date" in case and case["date"]:
        if not DATE_PATTERN.match(case["date"]):
            errors.append(f"[{case_id}] Invalid date format: '{case['date']}'. Expected: YYYY-MM-DD")
        else:
            try:
                case_date = datetime.strptime(case["date"], "%Y-%m-%d").date()
                if case_date > date.today():
                    errors.append(f"[{case_id}] Date is in the future: '{case['date']}'")
            except ValueError:
                errors.append(f"[{case_id}] Invalid date value: '{case['date']}'")

    # 4. country合法性
    if "country" in case and case["country"]:
        if case["country"] not in VALID_COUNTRY_CODES:
            warnings.append(f"[{case_id}] Country code may not be valid ISO 3166-1: '{case['country']}'")

    # 5. caseType合法性
    if "caseType" in case and case["caseType"]:
        if case["caseType"] not in ("court", "admin"):
            errors.append(f"[{case_id}] Invalid caseType: '{case['caseType']}'. Expected: 'court' or 'admin'")

    # 6. sourceUrl格式
    if "sourceUrl" in case and case["sourceUrl"]:
        if not URL_PATTERN.match(case["sourceUrl"]):
            errors.append(f"[{case_id}] Invalid sourceUrl format: '{case['sourceUrl']}'")

def main():
    project_root = Path(__file__).parent.parent
    cases_path = project_root / "data" / "cases.json"

    if not cases_path.exists():
        print(f"Error: {cases_path} not found")
        sys.exit(1)

    with open(str(cases_path), 'r', encoding='utf-8') as f:
        cases = json.load(f)

    # Check for duplicate IDs
    ids = [c.get("id") for c in cases if "id" in c]
    seen_ids = set()
    for cid in ids:
        if cid in seen_ids:
            errors.append(f"Duplicate ID: '{cid}'")
        seen_ids.add(cid)

    # Validate each case
    for idx, case in enumerate(cases):
        validate_case(case, idx)

    # Print results
    print(f"Validated {len(cases)} cases")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print("\n--- ERRORS ---")
        for e in errors:
            print(f"  [E] {e}")

    if warnings:
        print("\n--- WARNINGS ---")
        for w in warnings:
            print(f"  [W] {w}")

    if not errors and not warnings:
        print("\n[PASS] All checks passed!")

    # Exit code
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
