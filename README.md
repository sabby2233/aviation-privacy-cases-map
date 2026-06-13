# 全球航空数据保护执法案例地图

> **Global Aviation Data Protection Enforcement Case Map**
> 
> 交互式世界地图，收录全球各国数据保护机构（DPA）针对航空业的行政执法决定及涉及航空数据隐私的法院判决。

🌐 **在线访问**: [GitHub Pages 部署地址]（部署后填写）

---

## 功能特性

- **交互式世界地图**：使用 D3.js + TopoJSON 渲染，悬停显示案例数，点击国家进入详情
- **分色渲染**：1-2 案例浅蓝、3-4 案例中蓝、5+ 案例深蓝
- **侧边栏**：展示案例分类列表，支持行政处罚 / 法院判决切换
- **案例超链接**：每个案例名称链接至官方来源
- **全球覆盖**：目前收录 **30 个案例 / 13 个国家**，持续增长

## 数据范围

### 收录标准
✅ DPA（数据保护机构）针对**航空实体**（航空公司、机场、GDS系统等）的行政决定  
✅ 涉及**航空数据隐私**的法院判决（含集体诉讼）  
✅ 各国数据保护法框架下的执法案例（GDPR、CCPA、BIPA、PIPL 等）

### 排除范围
❌ 航空安全、飞行标准执法  
❌ 消费者延误赔偿、票价纠纷  
❌ 噪音、环境类处罚

## 当前数据统计

| 国家 | 案例数 | 行政 | 司法 |
|------|--------|------|------|
| 西班牙 (ES) | 7 | 7 | 0 |
| 美国 (US) | 7 | 4 | 3 |
| 英国 (GB) | 3 | 3 | 0 |
| 比利时 (BE) | 2 | 1 | 1 |
| 法国 (FR) | 2 | 2 | 0 |
| 土耳其 (TR) | 2 | 2 | 0 |
| 澳大利亚 (AU) | 1 | 1 | 0 |
| 中国 (CN) | 1 | 0 | 1 |
| 塞浦路斯 (CY) | 1 | 1 | 0 |
| 中国香港 (HK) | 1 | 1 | 0 |
| 意大利 (IT) | 1 | 1 | 0 |
| 罗马尼亚 (RO) | 1 | 1 | 0 |
| 瑞典 (SE) | 1 | 1 | 0 |
| **合计** | **30** | **25** | **5** |

---

## 技术架构

```
├── index.html                  # 主页面
├── js/
│   ├── data-loader.js          # 数据加载 + ISO 映射
│   ├── map.js                  # D3 地图渲染
│   ├── sidebar.js              # 侧边栏交互
│   └── main.js                 # 入口模块
├── css/
│   └── style.css               # 深色主题样式
├── data/
│   ├── cases.json              # 主案例数据（源数据）
│   ├── countries.json          # 聚合统计（前端直接消费）
│   └── world-110m.json         # Natural Earth TopoJSON 地图数据
├── scripts/
│   └── collect/
│       ├── merge_and_generate.py   # 主采集 + 合并脚本
│       ├── collect_ico.py          # ICO (英国) 采集
│       ├── collect_cnil_aepd.py    # CNIL (法国) + AEPD (西班牙) 采集
│       ├── collect_ftc.py          # FTC + DOT (美国) 采集
│       ├── collect_courtlistener.py # CourtListener API 采集
│       ├── collect_gdpr_csv.py     # GDPR Fines Dataset CSV 采集
│       ├── keyword_filter.py       # 关键词过滤模块
│       ├── case_builder.py         # 案例数据构建工具
│       ├── dedup.py                # 去重模块
│       └── state_manager.py        # 增量采集状态管理
└── .github/
    └── workflows/
        ├── update-cases.yml        # 每月1日自动采集更新
        └── deploy-pages.yml        # 自动部署至 GitHub Pages
```

### 技术选型
| 组件 | 选择 | 原因 |
|------|------|------|
| 地图渲染 | D3.js v7 + TopoJSON | 免费、高性能、无后端 |
| 地图投影 | geoEqualEarth | D3 v7 内置，效果优秀 |
| CSS框架 | Tailwind CSS CDN | 快速开发深色主题 |
| 数据存储 | JSON 文件 | 零成本，Git 版本控制 |
| 部署 | GitHub Pages | 完全免费 |
| 自动化 | GitHub Actions Cron | 每月自动更新 |
| 采集 | Python + requests + BS4 | 轻量、易维护 |

---

## 本地开发

### 方式一：直接打开（推荐用于查看）
```bash
# 直接在浏览器中打开
open index.html
```

### 方式二：本地服务器（推荐用于开发）
```bash
# Python 3
python -m http.server 8000
# 然后访问 http://localhost:8000
```

### 方式三：Node.js
```bash
npx serve .
```

---

## 手动触发数据更新

### 运行采集脚本
```bash
# 创建 Python 虚拟环境（首次）
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install requests beautifulsoup4 lxml

# 运行全量采集 + 合并
cd scripts
python collect/merge_and_generate.py
```

### 设置 CourtListener API Token（可选）
```bash
# 注册免费账号: https://www.courtlistener.com/sign-in/
# 获取 token: https://www.courtlistener.com/api/
export CL_API_TOKEN=your_token_here
python collect/merge_and_generate.py
```

---

## GitHub Pages 部署步骤

1. **Fork 或推送到 GitHub**
2. **启用 GitHub Pages**：仓库 Settings → Pages → Source: GitHub Actions
3. **（可选）设置 Secrets**：Settings → Secrets → `COURTLISTENER_TOKEN`
4. 推送代码后自动部署；每月 1 日自动更新数据

---

## 添加新案例

编辑 `data/cases.json`，按以下格式添加：

```json
{
  "id": "XX-A-001",
  "caseName": "案件名称（本地语言）",
  "caseNameEn": "Case Name in English",
  "country": "XX",
  "countryName": "国家中文名",
  "caseType": "admin",
  "authority": "执法机构全称",
  "authorityShort": "简称",
  "date": "YYYY-MM-DD",
  "sourceUrl": "https://official-source.gov/...",
  "summary": "案件摘要（中文，100-300字）",
  "tags": ["GDPR", "data-breach", "airline"],
  "fineAmount": 100000,
  "fineCurrency": "EUR",
  "sector": "Aviation",
  "lastVerified": "2026-06-13"
}
```

字段说明：
- `caseType`: `"admin"`（行政处罚）或 `"court"`（法院判决）
- `fineAmount`: 数字（null 表示无罚款或金额未公开）
- `fineCurrency`: `"EUR"`, `"GBP"`, `"USD"`, `"AUD"` 等

添加后运行脚本重建 `countries.json`：
```bash
python scripts/collect/merge_and_generate.py
```

---

## 数据来源

| 级别 | 来源 | 覆盖范围 |
|------|------|----------|
| A | GDPR Enforcement Tracker (GitHub CSV) | 全球 GDPR 执法案例 |
| A | ICO (ico.org.uk) | 英国数据保护 |
| A | CNIL (cnil.fr) | 法国数据保护 |
| A | AEPD (aepd.es) | 西班牙数据保护 |
| A | FTC (ftc.gov) | 美国联邦贸易委员会 |
| A | CourtListener API | 美国联邦法院判决 |
| B | EDPB (edpb.europa.eu) | 欧盟 DPA 决定 |
| B | OAIC (oaic.gov.au) | 澳大利亚 |
| B | PDPC (pdpc.gov.sg) | 新加坡 |
| C | KVKK (kvkk.gov.tr) | 土耳其 |
| C | PCPD (pcpd.org.hk) | 中国香港 |

---

## 贡献指南

1. Fork 本仓库
2. 发现新的航空数据保护案例？请提交 Issue 或 PR
3. 确保案例来源为官方 DPA 决定或法院公开判决
4. 案例摘要需包含中文翻译

---

## 许可证

数据来源均为公开的政府或法院文件，遵循各来源的开放数据许可证。
代码部分采用 MIT 许可证。

---

*最后更新：2026-06-13 | 数据版本：20260613*
