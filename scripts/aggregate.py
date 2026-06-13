#!/usr/bin/env python3
"""
aggregate.py - 数据聚合脚本
从 cases.json 生成 countries.json（国家汇总数据）
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

def load_cases(cases_path: str) -> list:
    """加载案例数据"""
    with open(cases_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def aggregate_countries(cases: list) -> dict:
    """按国家聚合案例数据"""
    country_data = defaultdict(lambda: {
        "countryCode": "",
        "countryName": "",
        "totalCases": 0,
        "courtCases": 0,
        "adminCases": 0,
        "authorities": defaultdict(lambda: {"name": "", "type": "", "caseCount": 0})
    })

    for case in cases:
        cc = case["country"]
        cd = country_data[cc]
        cd["countryCode"] = cc
        cd["countryName"] = case["countryName"]
        cd["totalCases"] += 1

        if case["caseType"] == "court":
            cd["courtCases"] += 1
        else:
            cd["adminCases"] += 1

        auth_name = case["authority"]
        auth = cd["authorities"][auth_name]
        auth["name"] = auth_name
        auth["type"] = case["caseType"]
        auth["caseCount"] += 1

    # Convert authorities from dict to list
    result = {}
    for cc, cd in country_data.items():
        result[cc] = {
            "countryCode": cd["countryCode"],
            "countryName": cd["countryName"],
            "totalCases": cd["totalCases"],
            "courtCases": cd["courtCases"],
            "adminCases": cd["adminCases"],
            "authorities": list(cd["authorities"].values())
        }

    return result

def main():
    project_root = Path(__file__).parent.parent
    cases_path = project_root / "data" / "cases.json"
    output_path = project_root / "data" / "countries.json"

    if not cases_path.exists():
        print(f"Error: {cases_path} not found")
        sys.exit(1)

    cases = load_cases(str(cases_path))
    print(f"Loaded {len(cases)} cases")

    countries = aggregate_countries(cases)

    # Add version for cache invalidation
    output = {
        "version": "2026-06-12-v1",
        "generatedAt": "2026-06-12T22:53:00Z",
        "totalCountries": len(countries),
        "totalCases": len(cases),
        "countries": countries
    }

    with open(str(output_path), 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Generated countries.json with {len(countries)} countries")
    for cc, cd in sorted(countries.items(), key=lambda x: -x[1]["totalCases"]):
        print(f"  {cd['countryName']} ({cc}): {cd['totalCases']} cases "
              f"(court: {cd['courtCases']}, admin: {cd['adminCases']})")

if __name__ == "__main__":
    main()
