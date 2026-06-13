# 全球航空数据处罚案例地图 — 数据源目录

> 编制日期：2026-06-12（修订版）
> **范围定义**：本目录仅收录各国**数据保护机构（DPA）**针对航空业开出的行政决定，以及涉及航空数据隐私/数据泄露/数据保护法违反的**法院判决**。航空安全、飞行标准、消费者延误赔偿、噪音、环境等非数据类处罚不在收录范围。

---

## 一、范围定义与关键词过滤

### 1.1 收录范围

| 类型 | 定义 | 示例 |
|------|------|------|
| **行政决定** | 各国数据保护机构（DPA）针对航空业实体（航空公司、机场、数据处理者、GDS等）开出的罚款、警告、整改令、强制令 | CNIL对法航GDPR违规罚款、ICO对英国航司数据泄露处罚 |
| **法院判决** | 涉及航空数据隐私、数据泄露、个人数据保护法违反的民事或刑事判决 | 欧盟法院PNR数据案、美国FTC诉航司隐私欺诈案 |

### 1.2 排除范围

- 航空安全违规（FAA安全处罚、EASA安全指令）
- 飞行标准违规（飞行员执照处罚）
- 消费者延误赔偿（EU261、美国DOT退款令）
- 噪音/环境处罚
- 反垄断/竞争法处罚（除非涉及数据垄断）

### 1.3 采集关键词过滤规则

每个采集脚本**必须**使用以下关键词组合筛选航空数据相关案例：

**航空实体关键词（OR 组合）：**
```
aviation OR airline OR aircraft OR airport OR passenger OR flight OR
carrier OR airway OR aeronautic OR GDS OR "booking system" OR
航司 OR 航空 OR 航空公司 OR 机场 OR 航班
```

**数据/隐私关键词（OR 组合）：**
```
"data protection" OR "data privacy" OR "personal data" OR "personal information" OR
"data breach" OR GDPR OR PNR OR "passenger name record" OR PIPL OR
"数据保护" OR "个人信息" OR "数据泄露" OR "隐私"
```

**组合逻辑**：`航空实体关键词 AND 数据隐私关键词`。对于无法程序化组合关键词的源，需在采集后人工过滤。

---

## 二、评估等级说明

| 等级 | 含义 | 采集策略 |
|------|------|----------|
| **A** | 结构化数据，稳定HTML列表或API，可全自动采集并关键词过滤 | 编写专用采集脚本，纳入GitHub Actions自动调度 |
| **B** | 半结构化数据（JS动态加载、需多步导航、需后处理过滤），需额外解析 | 编写采集+解析脚本，部分环节可能需人工校验 |
| **C** | 非结构化或分散数据（散落新闻稿、无统一入口、需登录等） | 人工录入工作流（CSV → merge_manual.py） |
| **D** | 暂未找到可访问的数据入口 | 标记为"待补充"，后续调研或用户提供 |

---

## 三、A级数据源（全自动采集）

### 1. 欧盟 — GDPR Enforcement Tracker

| 项目 | 内容 |
|------|------|
| **国家/地区** | 欧盟多国 (EU) |
| **机构名称** | 各国数据保护机构（DPA），由CMS律所汇总 |
| **机构类型** | 行政 |
| **URL** | `https://www.enforcementtracker.com/` |
| **采集方式** | HTML页面抓取 |
| **评估等级** | **A** |
| **数据结构** | 3,194条GDPR执法行动；字段：ETid, Country, Authority, Date, Fine(€), Controller/Processor, Sector, Article(s)；支持按Sector筛选 |
| **航空过滤** | 按Sector筛选 "Transport" 行业，再结合关键词过滤航空实体 |
| **反爬评估** | 中等风险（商业律所运营），需控制频率 |
| **预估航空相关记录** | 约20-50条（需实际筛选确认） |
| **增量更新** | 按 **Date** 字段排序，抓取 `last_fetch_time` 之后的新增记录；Date字段为GDPR执法行动的决定日期，格式 `DD/MM/YYYY` |
| **备注** | 数据每小时刷新；这是覆盖欧盟各国DPA执法的核心数据源 |

### 2. 美国 — FTC Cases and Proceedings

| 项目 | 内容 |
|------|------|
| **国家/地区** | 美国 (US) |
| **机构名称** | Federal Trade Commission |
| **机构类型** | 行政+法院（FTC兼具行政和诉讼职能） |
| **URL** | `https://www.ftc.gov/enforcement/cases-proceedings` |
| **采集方式** | HTML分页抓取 |
| **评估等级** | **A** |
| **数据结构** | 6,086条记录，305页（每页20/50/100条可选）；字段：案件名称、Type of Action、Last Updated、FTC Matter Number、Case Status；支持关键词搜索、行业筛选（含Transportation）、日期范围筛选 |
| **航空过滤** | ① Industry筛选选"Transportation"；② 关键词搜索"aviation OR airline OR flight OR passenger" |
| **反爬评估** | 低风险，政府公开网站 |
| **预估航空相关记录** | 约50-100条（含交通行业非航空案例，需二次过滤） |
| **增量更新** | 按 **Last Updated** 字段筛选，设置日期范围 ≥ `last_fetch_time`；该字段反映案件的最新更新时间，支持URL参数筛选 |
| **备注** | FTC对航司隐私/数据安全执法频繁（如2014年对Delta的隐私指控），是重要的美国行政数据源 |

### 3. 美国 — CourtListener (Free Law Project)

| 项目 | 内容 |
|------|------|
| **国家/地区** | 美国 (US) |
| **机构名称** | CourtListener — 聚合美国联邦及州法院判决 |
| **机构类型** | 法院 |
| **URL** | `https://www.courtlistener.com/api/rest/v4/search/` |
| **采集方式** | REST API（免费注册获取Token） |
| **评估等级** | **A** |
| **数据结构** | Search API：支持关键词搜索、类型过滤；返回字段：caseName, court, dateFiled, citation, docketNumber, absolute_url等 |
| **航空过滤** | API查询：`q=aviation data privacy OR airline data breach OR airline personal information` |
| **API限制** | 125次/天（免费Token） |
| **反爬评估** | 无需爬虫，API访问 |
| **预估航空相关记录** | 约20-80条（需多关键词组合查询） |
| **增量更新** | 通过 API参数 `filed_after={last_fetch_date}` 增量查询；按 **dateFiled** 字段筛选新立案案件；也可使用Alert API设置关键词监控自动推送 |
| **备注** | 速率限制较严，月度采集需合理分配请求；覆盖3,358个司法管辖区 |

### 4. 法国 — CNIL Sanctions

| 项目 | 内容 |
|------|------|
| **国家/地区** | 法国 (FR) |
| **机构名称** | Commission Nationale de l'Informatique et des Libertés |
| **机构类型** | 行政 |
| **URL** | `https://www.cnil.fr/en/investigation-powers-cnil/sanctions-issued-cnil` |
| **采集方式** | HTML页面抓取（静态表格，按年份分组） |
| **评估等级** | **A** |
| **数据结构** | 约252条制裁记录（2018-2026），按年份降序排列；字段：Date, Type of organisation, Main breaches/Theme, Decision（含罚款金额和Légifrance链接） |
| **航空过滤** | ① 全量采集后按"Type of organisation"和关键词（aviation, airline, air transport, compagnie aérienne）过滤；② 部分条目仅显示组织类型而非名称，需结合summary判断 |
| **反爬评估** | 低风险，政府公开网站，无反爬 |
| **预估航空相关记录** | 约5-15条 |
| **增量更新** | 按 **Date** 字段检查新增条目；每年份组按日期降序排列，首条记录日期 > `last_fetch_time` 时存在新增；可结合 `data.gouv.fr` 开放数据集的更新频率检测 |
| **备注** | 另有开放数据集：`https://www.data.gouv.fr/datasets/les-deliberations-de-la-cnil`（含所有CNIL决议，可编程获取） |

### 5. 英国 — ICO Enforcement Action

| 项目 | 内容 |
|------|------|
| **国家/地区** | 英国 (GB) |
| **机构名称** | Information Commissioner's Office |
| **机构类型** | 行政 |
| **URL** | `https://ico.org.uk/action-weve-taken/enforcement/` |
| **采集方式** | JS动态加载页面，需发现后端API或使用轻量级渲染 |
| **评估等级** | **A**（有结构化筛选器，需解析动态加载） |
| **数据结构** | 动态列表，含筛选器：Type（Enforcement notices/Reprimands/Monetary penalties/Prosecutions）、Sector（含"Transport and leisure"）、Date range、Sort |
| **航空过滤** | ① Sector筛选"Transport and leisure"；② 关键词过滤aviation/airline/airport |
| **反爬评估** | 中等风险（JS渲染），需分析网络请求获取数据API |
| **预估航空相关记录** | 约10-30条 |
| **增量更新** | 按 **Date range** 筛选器设置 ≥ `last_fetch_time` 增量查询；需发现后端API的日期参数格式 |
| **备注** | 页面列表为JS动态加载，需通过浏览器开发工具发现后端API端点，或使用Selenium/Playwright渲染 |

### 6. 西班牙 — AEPD Resoluciones

| 项目 | 内容 |
|------|------|
| **国家/地区** | 西班牙 (ES) |
| **机构名称** | Agencia Española de Protección de Datos |
| **机构类型** | 行政 |
| **URL** | `https://www.aepd.es/publicaciones-y-resoluciones`（入口页）；制裁相关概念标签：`/buscador?f[0]=conceptos:Reclamaciones+infracciones+y+sanciones` |
| **采集方式** | HTML页面抓取（需多步导航至制裁列表） |
| **评估等级** | **A** |
| **数据结构** | 通过概念筛选器"Reclamaciones, infracciones y sanciones"可获取制裁决议列表；支持按概念（含行业相关分类）和文档类型筛选 |
| **航空过滤** | ① 概念筛选器定位制裁类决议；② 全量采集后按关键词（aerolínea, aviación, aeropuerto, aerolinea, airline, aviation）过滤 |
| **反爬评估** | 低风险，政府公开网站 |
| **预估航空相关记录** | 约10-30条（AEPD 2025年处理299项制裁程序，累计罚款约€40M） |
| **增量更新** | 按概念筛选器的发布日期排序，检查最新页面是否含 `last_fetch_time` 之后的条目；可结合开放数据门户的数据集版本号检测 |
| **备注** | AEPD另有开放数据门户：`https://www.aepd.es/la-agencia/datos-abiertos`，可能提供结构化数据集 |

---

## 四、B级数据源（半自动采集）

### 7. 欧盟 — CURIA (Court of Justice of the EU)

| 项目 | 内容 |
|------|------|
| **国家/地区** | 欧盟 (EU) |
| **机构名称** | Court of Justice of the European Union |
| **机构类型** | 法院 |
| **URL** | `https://juris.curia.europa.eu/jrecherche.jsf?language=en` |
| **采集方式** | HTML搜索结果页抓取 |
| **评估等级** | **B** |
| **数据结构** | 欧盟法院判例数据库；支持按关键词、案件类型、日期范围搜索 |
| **航空过滤** | 搜索关键词："aviation data protection" / "airline personal data" / "PNR" / "passenger data" |
| **反爬评估** | 低风险，法院公开数据库 |
| **预估航空相关记录** | 约5-20条 |
| **增量更新** | 按日期范围增量查询 |
| **备注** | 另有DPcuria.eu专门收录数据保护相关CJEU判例 |

### 8. 加拿大 — OPC Actions and Decisions

| 项目 | 内容 |
|------|------|
| **国家/地区** | 加拿大 (CA) |
| **机构名称** | Office of the Privacy Commissioner of Canada |
| **机构类型** | 行政 |
| **URL** | `https://www.priv.gc.ca/en/opc-actions-and-decisions/` |
| **采集方式** | HTML页面抓取（需导航至Investigations子页面） |
| **评估等级** | **B** |
| **数据结构** | 分类导航（Investigations, Audits, Reports to Parliament等）；调查列表含标题、编号、日期；无行业筛选器 |
| **航空过滤** | ① 全量采集Investigations列表；② 按关键词（aviation, airline, airport, flight, air transport, WestJet, Air Canada）过滤标题和摘要 |
| **反爬评估** | 低风险，政府公开网站 |
| **预估航空相关记录** | 约3-10条 |
| **增量更新** | 检查Investigations子页面新增条目 |
| **备注** | 有RSS订阅可用于变更检测 |

### 9. 澳大利亚 — OAIC Privacy Decisions

| 项目 | 内容 |
|------|------|
| **国家/地区** | 澳大利亚 (AU) |
| **机构名称** | Office of the Australian Information Commissioner |
| **机构类型** | 行政 |
| **URL** | `https://www.oaic.gov.au/privacy/privacy-assessments-and-decisions/privacy-decisions` |
| **采集方式** | HTML页面抓取（需导航至3个子分类：Enforceable undertakings / Investigation reports / Privacy determinations） |
| **评估等级** | **B** |
| **数据结构** | 导航枢纽页面，分3个子分类；子页面含决定列表，但无行业筛选 |
| **航空过滤** | ① 全量采集3个子分类的所有决定；② 按关键词（aviation, airline, airport, Qantas, Virgin, Jetstar）过滤 |
| **反爬评估** | 低风险，政府公开网站 |
| **预估航空相关记录** | 约3-10条 |
| **增量更新** | 检查子页面新增条目 |
| **备注** | OAIC的NDB（可通知数据泄露）报告按行业统计，含"Transport"类别，可辅助定位航空相关泄露事件 |

### 10. 新加坡 — PDPC Enforcement Decisions

| 项目 | 内容 |
|------|------|
| **国家/地区** | 新加坡 (SG) |
| **机构名称** | Personal Data Protection Commission |
| **机构类型** | 行政 |
| **URL** | `https://www.pdpc.gov.sg/organisations/regulations-decisions/enforcement-decisions` |
| **采集方式** | JS动态加载页面，需发现后端API或使用轻量级渲染 |
| **评估等级** | **B** |
| **数据结构** | 动态列表；筛选器：Type（Commission's Decisions / Voluntary Undertakings）、Year（2016-2026） |
| **航空过滤** | ① 全量采集后按关键词（aviation, airline, airport, Changi, SIA, Singapore Airlines, Scoot）过滤 |
| **反爬评估** | 中等风险（JS渲染），需分析网络请求获取数据API |
| **预估航空相关记录** | 约3-8条 |
| **增量更新** | 按年份筛选检查新增条目 |
| **备注** | 新加坡PDPA执法日趋活跃，PDPC的决定质量高 |

### 11. 英国 — BAILII (British and Irish Legal Information Institute)

| 项目 | 内容 |
|------|------|
| **国家/地区** | 英国 (GB) |
| **机构名称** | British and Irish Legal Information Institute |
| **机构类型** | 法院 |
| **URL** | `https://www.bailii.org/` |
| **采集方式** | HTML搜索结果页抓取 |
| **评估等级** | **B** |
| **数据结构** | 免费访问的英爱判例法数据库；搜索功能支持关键词、日期范围、法院层级筛选；搜索URL格式：`https://www.bailii.org/recent-decisions?query={keywords}`；返回字段：案件名称、法院、日期、引用编号、全文链接 |
| **航空过滤** | 搜索关键词组合："aviation data protection" / "airline personal data" / "airline data breach" / "airline privacy" |
| **反爬评估** | 高风险 — 网站已部署 **Anubis反爬系统**（PoW工作量证明），自动化采集受限；需降低频率或使用Selenium模拟浏览器通过验证 |
| **预估航空相关记录** | 约5-15条 |
| **增量更新** | 按日期范围增量搜索 |
| **备注** | BAILII是CourtListener之外补充英国判例的关键来源，覆盖英格兰威尔士高等法院、上诉法院、最高法院等。因反爬限制，建议月度采集时使用低频Selenium方案，或通过 `https://www.bailii.org/uk/cases/` 按法院层级分批浏览。与ICO（行政）互补，构成英国DPA执法+法院判决的完整覆盖 |

---

## 五、C级数据源（人工录入）

### 12. 德国 — BfDI

| 项目 | 内容 |
|------|------|
| **国家/地区** | 德国 (DE) |
| **机构名称** | Der Bundesbeauftragte für den Datenschutz und die Informationsfreiheit |
| **机构类型** | 行政 |
| **URL** | `https://www.bfdi.bund.de/EN/Home/home_node.html` |
| **评估等级** | **C** |
| **数据结构** | 无结构化执法数据库；BfDI的执法信息仅通过年度活动报告（Tätigkeitsbericht）和新闻稿发布 |
| **采集策略** | 人工录入：阅读年度报告和新闻稿，提取航空相关案例后填写 `data/manual_entries.csv` |
| **预估航空相关记录** | 约2-5条 |
| **备注** | **主要依赖GDPR Enforcement Tracker覆盖德国案例**。BfDI无公开结构化列表，实际采集接近纯人工；德国各州(Land)DPA也可能有独立执法，数据更分散。GDPR Tracker已收录BfDI的大部分执法行动 |

### 13. 中国 — 网信办/各地网信办

| 项目 | 内容 |
|------|------|
| **国家/地区** | 中国 (CN) |
| **机构名称** | 国家互联网信息办公室 / 各省市级网信办 |
| **机构类型** | 行政 |
| **URL** | `https://www.cac.gov.cn/`（国家网信办）；各地网信办分散 |
| **评估等级** | **C** |
| **数据结构** | 无统一处罚公示数据库；处罚信息通过新闻发布和专题文章披露 |
| **采集策略** | 人工监测网信办官网和权威新闻（如：某航空公司数据被间谍网络窃取案——国家安全机关公布） |
| **备注** | 中国《数据安全法》《个人信息保护法》执法信息分散，航空相关案例需从新闻源人工提取。CAAC行政处罚公示（`http://www.caac.gov.cn/caaccredit/frontend/credit/creditinfopublicity/list`）含部分数据类处罚，但非专门数据保护源 |

### 14. 印度 — DPA (Data Protection Board of India)

| 项目 | 内容 |
|------|------|
| **国家/地区** | 印度 (IN) |
| **机构名称** | Data Protection Board of India（依据2023年DPDP Act设立） |
| **机构类型** | 行政 |
| **URL** | 待确认（机构新成立，网站尚未完善） |
| **评估等级** | **C** |
| **数据结构** | 印度数字个人数据保护法(DPDP Act)2023年通过，执法机构尚在建设中 |
| **采集策略** | 人工监测新闻和政府公告 |

### 15. 巴西 — ANPD

| 项目 | 内容 |
|------|------|
| **国家/地区** | 巴西 (BR) |
| **机构名称** | Autoridade Nacional de Proteção de Dados |
| **机构类型** | 行政 |
| **URL** | `https://www.gov.br/anpd/pt-br` |
| **评估等级** | **C** |
| **数据结构** | ANPD 2020年成立，执法尚在早期阶段；已发布部分行政制裁程序 |
| **采集策略** | 人工监测ANPD官网和开放数据门户 |

### 16. 韩国 — PIPC

| 项目 | 内容 |
|------|------|
| **国家/地区** | 韩国 (KR) |
| **机构名称** | Personal Information Protection Commission (개인정보보호위원회) |
| **机构类型** | 行政 |
| **URL** | `https://www.pipc.go.kr/` |
| **评估等级** | **C** |
| **数据结构** | 有制裁决议发布，但网站主要为韩语，结构化程度待验证 |
| **采集策略** | 人工监测PIPC制裁公告，可能需要韩语能力 |

---

## 六、D级数据源（待补充）

| 国家/地区 | 机构 | 说明 |
|-----------|------|------|
| 日本 (JP) | PPC (個人情報保護委員会) | 日本个人信息保护委员会，执法信息可能以日语发布 |
| 瑞士 (CH) | FDPIC | 联邦数据保护和信息专员，非EU但遵循类似GDPR框架 |
| 阿联酋 (AE) | UAEDPCA | 阿联酋数据保护法2021年生效，执法机构较新 |
| 南非 (ZA) | InfoReg | 南非信息监管机构，POPIA执法逐步推进 |
| 土耳其 (TR) | KVKK | 土耳其数据保护局，有执法决定但网站结构待验证 |
| 新西兰 (NZ) | OPC New Zealand | 新西兰隐私专员办公室 |

---

## 七、汇总统计

| 等级 | 数量 | 来源 |
|------|------|------|
| **A**（全自动） | 6 | GDPR Tracker (EU), FTC (US), CourtListener (US), CNIL (FR), ICO (GB), AEPD (ES) |
| **B**（半自动） | 5 | CURIA (EU), OPC (CA), OAIC (AU), PDPC (SG), BAILII (GB) |
| **C**（人工录入） | 5 | BfDI (DE), 网信办 (CN), DPA (IN), ANPD (BR), PIPC (KR) |
| **D**（待补充） | 6 | 日本, 瑞士, 阿联酋, 南非, 土耳其, 新西兰 |

**总计：21个数据源，覆盖20+个国家/地区**

---

## 八、从旧版目录移除的数据源

以下来源因**不涉及数据保护/隐私执法**而移除：

| 原编号 | 来源 | 移除原因 |
|--------|------|----------|
| 1 | U.S. DOT — Aviation Enforcement Orders | 消费者保护/退款令，非数据保护 |
| 2 | FAA — Enforcement Reports | 航空安全/飞行标准处罚，非数据保护 |
| 4 | CASA — Recent Enforcement Actions | 航空安全执法，非数据保护 |
| 5 | CTA — Decisions and Determinations | 交通运输决定（含消费者投诉），非专门数据保护 |
| 6 | CAAC — 行政处罚公示 | 航空行政违规处罚，非专门数据保护（中国数据保护由网信办管辖） |
| 9 | UK CAA — Enforcement and Prosecutions | 航空安全/消费者执法，非数据保护 |
| 10 | 德国 LBA | 航空安全监管机构，非数据保护 |
| 11 | 法国 DGAC | 民航行政机构，非数据保护 |
| 12 | 新加坡 CAAS | 航空安全监管机构，非数据保护 |
| 13 | 印度 DGCA | 航空安全监管机构，非数据保护 |
| 14 | 日本 JCAB/MLIT | 航空安全监管机构，非数据保护 |
| 15 | 韩国 MOLIT | 交通/航空行政机构，非数据保护 |
| 16 | 巴西 ANAC | 民航行政机构，非数据保护 |
| 17 | 阿联酋 GCAA | 民航行政机构，非数据保护 |

> **核心转变**：从"航空管理机构"转向"数据保护机构"。航空业仅作为被执法的行业过滤器，而非执法主体。
