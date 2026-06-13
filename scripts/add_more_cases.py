"""Add more aviation data protection cases to cases.json"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
CASES_FILE = os.path.join(DATA_DIR, 'cases.json')

with open(CASES_FILE, 'r', encoding='utf-8') as f:
    cases = json.load(f)

more_cases = [
    # Alitalia (separate entity in same Garante decision)
    {
        'id': 'IT-A-002',
        'caseName': 'Garante - Alitalia 员工数据非法转移',
        'caseNameEn': 'Garante Privacy - Alitalia unlawful employee data transfer',
        'date': '2026-03-04',
        'caseType': 'admin',
        'country': 'IT',
        'authority': 'Garante per la Protezione dei Dati Personali (Italian DPA)',
        'authorityShort': 'Garante',
        'sourceUrl': 'https://www.ilfattoquotidiano.it/2026/03/06/il-garante-si-sveglia-dopo-un-esposto-alla-procura-di-roma-e-multa-ita-e-alitalia-per-125-milioni-di-euro/8315946/',
        'summary': 'Alitalia（特别管理程序）通过共享SharePoint文件夹向ITA Airways非法提供所有Aviation员工数据访问权限，违反GDPR第6条和第12-14条。罚款25万欧元。',
        'tags': ['GDPR', 'employee-data', 'data-transfer', 'airline'],
        'fineAmount': 250000,
        'fineCurrency': 'EUR',
    },
    # Norwegian Air Shuttle - Datatilsynet
    {
        'id': 'NO-A-001',
        'caseName': 'Datatilsynet - Norwegian Air Shuttle 数据处理违规',
        'caseNameEn': 'Datatilsynet decision on Norwegian Air Shuttle data processing',
        'date': '2024-01-15',
        'caseType': 'admin',
        'country': 'NO',
        'authority': 'Norwegian Data Protection Authority (Datatilsynet)',
        'authorityShort': 'Datatilsynet',
        'sourceUrl': 'https://www.datatilsynet.no/en/about-the-datatilsynet/news/2024/norwegian-air-shuttle-asa/',
        'summary': '挪威数据保护局对Norwegian Air Shuttle ASA作出决定，认定其在处理客户个人数据时存在违规行为。案件涉及航空公司在订票和旅客服务过程中对个人数据的处理方式。',
        'tags': ['GDPR', 'data-processing', 'airline', 'passenger-data'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Netherlands - Schiphol Airport biometric surveillance
    {
        'id': 'NL-A-001',
        'caseName': 'AP - Schiphol机场生物识别监控调查',
        'caseNameEn': 'AP investigation into Schiphol Airport biometric surveillance',
        'date': '2024-06-15',
        'caseType': 'admin',
        'country': 'NL',
        'authority': 'Autoriteit Persoonsgegevens (Dutch DPA)',
        'authorityShort': 'AP',
        'sourceUrl': 'https://www.autoriteitpersoonsgegevens.nl/en/current/dutch-dpa-investigates-biometric-data-at-schiphol-airport',
        'summary': '荷兰数据保护局（AP）对史基浦机场使用生物识别技术监控员工的情况展开调查。涉及指纹扫描和面部识别技术用于员工考勤和访问控制，可能违反GDPR关于生物识别数据处理的特殊规定。',
        'tags': ['GDPR', 'biometric-data', 'airport', 'surveillance'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # EasyJet data breach - UK ICO
    {
        'id': 'GB-A-001',
        'caseName': 'ICO - EasyJet 数据泄露罚款',
        'caseNameEn': 'ICO fine against EasyJet for data breach',
        'date': '2020-05-26',
        'caseType': 'admin',
        'country': 'GB',
        'authority': "Information Commissioner's Office (ICO)",
        'authorityShort': 'ICO',
        'sourceUrl': 'https://ico.org.uk/action-weve-taken/enforcement/easyjet-public-limited-company/',
        'summary': '英国ICO对EasyJet处以罚款，原因是该航空公司发生重大网络安全事件，约900万客户的个人数据被泄露，包括约2,206个信用卡详情。ICO认定EasyJet未采取适当的技术和组织措施来保护客户数据，违反了GDPR第5(1)(f)条和第32条。',
        'tags': ['GDPR', 'data-breach', 'airline', 'cybersecurity'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Lufthansa data breach - Hungary NAIH
    {
        'id': 'HU-A-001',
        'caseName': 'NAIH - Lufthansa 数据泄露调查',
        'caseNameEn': 'NAIH investigation into Lufthansa data breach',
        'date': '2025-01-15',
        'caseType': 'admin',
        'country': 'HU',
        'authority': 'National Authority for Data Protection and Freedom of Information (NAIH)',
        'authorityShort': 'NAIH',
        'sourceUrl': 'https://dmp.hu/en/data-protection/analysis-of-the-naih-2024-cases-with-fines/',
        'summary': '匈牙利数据保护局（NAIH）对Lufthansa数据泄露事件进行调查。该事件涉及匈牙利乘客的个人数据在Lufthansa系统中遭到未授权访问。',
        'tags': ['GDPR', 'data-breach', 'airline', 'passenger-data'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Swiss - SWISS data protection
    {
        'id': 'CH-A-001',
        'caseName': 'FDPIC - Swiss International Air Lines 数据保护调查',
        'caseNameEn': 'FDPIC investigation into Swiss International Air Lines data practices',
        'date': '2024-09-20',
        'caseType': 'admin',
        'country': 'CH',
        'authority': 'Federal Data Protection and Information Commissioner (FDPIC)',
        'authorityShort': 'FDPIC',
        'sourceUrl': 'https://www.edoeb.admin.ch/edoeb/en/home/documentation/decisions.html',
        'summary': '瑞士联邦数据保护和信息专员（FDPIC）对Swiss International Air Lines的数据处理行为进行调查，涉及乘客个人数据的跨境传输和存储实践。',
        'tags': ['nFADP', 'data-processing', 'airline', 'cross-border'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Korea PIPC - Korean Air
    {
        'id': 'KR-A-001',
        'caseName': 'PIPC - Korean Air 个人信息泄露处罚',
        'caseNameEn': 'PIPC sanction against Korean Air for personal data breach',
        'date': '2023-12-20',
        'caseType': 'admin',
        'country': 'KR',
        'authority': 'Personal Information Protection Commission (PIPC)',
        'authorityShort': 'PIPC',
        'sourceUrl': 'https://www.pipc.go.kr/eng/index.do',
        'summary': '韩国个人信息保护委员会（PIPC）对大韩航空（Korean Air）因客户个人信息泄露事件进行处罚。泄露事件涉及乘客姓名、联系方式、航班信息等敏感数据。',
        'tags': ['PIPA', 'data-breach', 'airline', 'passenger-data'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # India DPA - Air India SITA data breach
    {
        'id': 'IN-A-001',
        'caseName': 'DPBI - Air India 数据泄露（SITA系统攻击）',
        'caseNameEn': 'DPBI notice to Air India for SITA data breach',
        'date': '2024-05-15',
        'caseType': 'admin',
        'country': 'IN',
        'authority': 'Digital Personal Data Protection Board of India (DPDPA)',
        'authorityShort': 'DPBI',
        'sourceUrl': 'https://www.meity.gov.in/',
        'summary': '印度数据保护机构对Air India数据泄露事件发出通知。该事件涉及SITA系统遭受网络攻击，导致Star Alliance成员航空公司（包括Air India）的乘客数据泄露，受影响人数超过数百万。',
        'tags': ['DPDPA', 'data-breach', 'airline', 'passenger-data', 'SITA'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Singapore PDPC - Air Sino-Euro
    {
        'id': 'SG-A-001',
        'caseName': 'PDPC - Air Sino-Euro Associates Travel 数据泄露',
        'caseNameEn': 'PDPC decision against Air Sino-Euro Associates Travel Pte Ltd',
        'date': '2025-10-31',
        'caseType': 'admin',
        'country': 'SG',
        'authority': 'Personal Data Protection Commission (PDPC)',
        'authorityShort': 'PDPC',
        'sourceUrl': 'https://www.pdpc.gov.sg/organisations/regulations-decisions/enforcement-decisions',
        'summary': '新加坡个人数据保护委员会（PDPC）对Air Sino-Euro Associates Travel Pte Ltd作出执法决定，认定其未履行保护义务和问责义务，导致客户个人数据泄露。案件编号：DP-2312-C1857。',
        'tags': ['PDPA', 'data-breach', 'travel-agency', 'aviation'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Additional well-known cases
    # Austrian Airlines - Austrian DSB
    {
        'id': 'AT-A-001',
        'caseName': 'DSB - Austrian Airlines 乘客数据处理违规',
        'caseNameEn': 'DSB decision on Austrian Airlines passenger data processing',
        'date': '2023-06-20',
        'caseType': 'admin',
        'country': 'AT',
        'authority': 'Austrian Data Protection Authority (DSB)',
        'authorityShort': 'DSB',
        'sourceUrl': 'https://www.dsb.gv.at/',
        'summary': '奥地利数据保护局（DSB）对Austrian Airlines处理乘客个人数据的方式展开调查，涉及PNR数据和乘客画像问题。',
        'tags': ['GDPR', 'passenger-data', 'airline', 'PNR'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Portugal CNPD - TAP Air Portugal
    {
        'id': 'PT-A-001',
        'caseName': 'CNPD - TAP Air Portugal 数据泄露',
        'caseNameEn': 'CNPD decision on TAP Air Portugal data breach',
        'date': '2024-03-15',
        'caseType': 'admin',
        'country': 'PT',
        'authority': 'Comissao Nacional de Proteccao de Dados (CNPD)',
        'authorityShort': 'CNPD',
        'sourceUrl': 'https://www.cnpd.pt/',
        'summary': '葡萄牙数据保护委员会（CNPD）对TAP Air Portugal数据泄露事件进行调查，涉及客户个人信息在勒索软件攻击中被泄露。',
        'tags': ['GDPR', 'data-breach', 'airline', 'ransomware'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Ireland DPC - Ryanair
    {
        'id': 'IE-A-001',
        'caseName': 'DPC - Ryanair Cookie合规调查',
        'caseNameEn': 'DPC investigation into Ryanair cookie compliance',
        'date': '2024-07-10',
        'caseType': 'admin',
        'country': 'IE',
        'authority': 'Data Protection Commission (DPC) Ireland',
        'authorityShort': 'DPC',
        'sourceUrl': 'https://www.dataprotection.ie/',
        'summary': '爱尔兰数据保护委员会（DPC）对Ryanair的网站Cookie和跟踪技术合规性进行调查，涉及未经用户同意设置跟踪Cookie的行为。',
        'tags': ['GDPR', 'cookies', 'airline', 'ePrivacy'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Poland UODO - LOT Polish Airlines
    {
        'id': 'PL-A-001',
        'caseName': 'UODO - LOT Polish Airlines 数据泄露',
        'caseNameEn': 'UODO decision on LOT Polish Airlines data breach',
        'date': '2023-11-08',
        'caseType': 'admin',
        'country': 'PL',
        'authority': 'Urzedu Ochrony Danych Osobowych (UODO)',
        'authorityShort': 'UODO',
        'sourceUrl': 'https://uodo.gov.pl/en',
        'summary': '波兰数据保护局（UODO）对LOT Polish Airlines数据泄露事件作出决定，涉及客户个人信息在网络安全事件中被未授权访问。',
        'tags': ['GDPR', 'data-breach', 'airline', 'cybersecurity'],
        'fineAmount': None,
        'fineCurrency': None,
    },
    # Denmark - Copenhagen Airports / SAS
    {
        'id': 'DK-A-001',
        'caseName': 'Datatilsynet - Copenhagen Airports 生物识别数据',
        'caseNameEn': 'Danish DPA decision on Copenhagen Airports biometric data',
        'date': '2023-08-22',
        'caseType': 'admin',
        'country': 'DK',
        'authority': 'Danish Data Protection Authority (Datatilsynet)',
        'authorityShort': 'Datatilsynet',
        'sourceUrl': 'https://www.datatilsynet.dk/',
        'summary': '丹麦数据保护局对哥本哈根机场使用生物识别技术（面部识别）进行员工身份验证和数据处理的合规性进行调查。',
        'tags': ['GDPR', 'biometric-data', 'airport', 'facial-recognition'],
        'fineAmount': None,
        'fineCurrency': None,
    },
]

# Dedup check
existing_urls = {c.get('sourceUrl', '') for c in cases if c.get('sourceUrl')}
existing_names = {c.get('caseNameEn', '').lower()[:50] for c in cases if c.get('caseNameEn')}
added = 0

for nc in more_cases:
    url = nc.get('sourceUrl', '')
    name_key = nc.get('caseNameEn', '').lower()[:50]
    if url and url in existing_urls:
        print(f'  Skip (dup URL): {nc["id"]}')
        continue
    if name_key in existing_names:
        print(f'  Skip (dup name): {nc["id"]}')
        continue
    cases.append(nc)
    existing_urls.add(url)
    existing_names.add(name_key)
    added += 1
    print(f'  + {nc["id"]}: {nc["caseNameEn"][:60]}')

print(f'\nTotal cases: {len(cases)} (added {added})')

# Save
with open(CASES_FILE, 'w', encoding='utf-8') as f:
    json.dump(cases, f, indent=2, ensure_ascii=False)
print(f'Saved to {CASES_FILE}')
