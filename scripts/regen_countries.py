"""Regenerate countries.json from cases.json"""
import json, sys, os
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
with open(os.path.join(DATA_DIR, 'cases.json'), 'r', encoding='utf-8') as f:
    cases = json.load(f)

COUNTRY_NAMES_ZH = {
    'AT':'奥地利','AU':'澳大利亚','BE':'比利时','BR':'巴西',
    'CA':'加拿大','CH':'瑞士','CN':'中国','CY':'塞浦路斯',
    'DE':'德国','DK':'丹麦','ES':'西班牙','FI':'芬兰',
    'FR':'法国','GB':'英国','GR':'希腊','HK':'中国香港',
    'HU':'匈牙利','IE':'爱尔兰','IN':'印度','IT':'意大利',
    'JP':'日本','KR':'韩国','NL':'荷兰','NO':'挪威',
    'PL':'波兰','PT':'葡萄牙','RO':'罗马尼亚','SE':'瑞典',
    'SG':'新加坡','TR':'土耳其','US':'美国','CH':'瑞士',
}
COUNTRY_NAMES_EN = {
    'AT':'Austria','AU':'Australia','BE':'Belgium','BR':'Brazil',
    'CA':'Canada','CH':'Switzerland','CN':'China','CY':'Cyprus',
    'DE':'Germany','DK':'Denmark','ES':'Spain','FI':'Finland',
    'FR':'France','GB':'UK','GR':'Greece','HK':'Hong Kong, China',
    'HU':'Hungary','IE':'Ireland','IN':'India','IT':'Italy',
    'JP':'Japan','KR':'South Korea','NL':'Netherlands','NO':'Norway',
    'PL':'Poland','PT':'Portugal','RO':'Romania','SE':'Sweden',
    'SG':'Singapore','TR':'Turkey','US':'United States',
}

country_data = defaultdict(lambda: {'cases':[],'totalCases':0,'adminCases':0,'courtCases':0,'latestDate':'','authorities':[]})
for c in cases:
    country = c.get('country','')
    if not country: continue
    d = country_data[country]
    d['cases'].append({k:v for k,v in c.items()})
    d['totalCases'] += 1
    if c.get('caseType') == 'admin':
        d['adminCases'] += 1
    else:
        d['courtCases'] += 1
    date = c.get('date') or ''
    if date and (not d['latestDate'] or date > d['latestDate']):
        d['latestDate'] = date
    auth = c.get('authorityShort','')
    if auth and auth not in d['authorities']:
        d['authorities'].append(auth)

result = {}
for code, data in sorted(country_data.items()):
    result[code] = {
        'code': code,
        'name': COUNTRY_NAMES_ZH.get(code, code),
        'nameEn': COUNTRY_NAMES_EN.get(code, code),
        'totalCases': data['totalCases'],
        'adminCases': data['adminCases'],
        'courtCases': data['courtCases'],
        'latestDate': data['latestDate'],
        'authorities': sorted(data['authorities']),
        'cases': sorted(data['cases'], key=lambda x: x.get('date') or '', reverse=True),
    }

countries_json = {
    'version': datetime.now().strftime('%Y%m%d'),
    'generatedAt': datetime.now().isoformat(),
    'totalCases': len(cases),
    'totalCountries': len(result),
    'countries': result,
}

with open(os.path.join(DATA_DIR, 'countries.json'), 'w', encoding='utf-8') as f:
    json.dump(countries_json, f, indent=2, ensure_ascii=False)

print(f'Done! {len(cases)} cases, {len(result)} countries')
for code in sorted(result.keys(), key=lambda x:-result[x]['totalCases']):
    info = result[code]
    print(f'  {code} {info["name"]}: {info["totalCases"]} ({info["adminCases"]}A/{info["courtCases"]}C)')
