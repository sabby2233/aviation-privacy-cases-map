# 全球航空数据处罚案例地图 — 技术选型文档

## 一、数据字段规范

### 案例主表 (`cases`)

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `id` | string | 是 | 唯一标识，格式：`{ISO2}-{类型缩写}-{序号}` | `US-C-001`, `GB-A-012` |
| `caseName` | string | 是 | 案例名称（原文语言） | `"FTC v. Delta Air Lines, Inc."` |
| `caseNameEn` | string | 否 | 案例英文名（非英语案例需提供） | `"CNIL Sanction against Air France"` |
| `country` | string | 是 | ISO 3166-1 alpha-2 国家代码 | `US`, `CN`, `DE` |
| `countryName` | string | 是 | 国家中文名 | `"美国"`, `"德国"` |
| `caseType` | enum | 是 | `court`（法院判决）/ `admin`（行政决定） | `court` |
| `authority` | string | 是 | 审理法院或行政机构全称 | `"U.S. District Court for the Northern District of Georgia"` |
| `authorityShort` | string | 否 | 机构简称 | `"N.D. Ga."` |
| `date` | string | 是 | 裁决/决定日期，ISO 8601 | `"2024-03-15"` |
| `sourceUrl` | string | 是 | 来源官方URL | `"https://www.courtlistener.com/..."` |
| `summary` | string | 否 | 案例摘要（200字内） | — |
| `tags` | string[] | 否 | 标签分类 | `["GDPR", "data-breach", "passenger-data"]` |
| `sourceName` | string | 是 | 来源网站名称 | `"CourtListener"`, `"CAAC"` |
| `lastVerified` | string | 是 | 最后验证日期 | `"2026-06-01"` |

### 国家汇总表 (`countries`，由主表自动聚合生成)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `countryCode` | string | ISO 3166-1 alpha-2 |
| `countryName` | string | 国家中文名 |
| `totalCases` | number | 案例总数 |
| `courtCases` | number | 法院案例数 |
| `adminCases` | number | 行政案例数 |
| `authorities` | object[] | `[{name, type, caseCount}]` |

---

## 二、技术栈选型

### 2.1 前端框架

| 层面 | 选型 | 理由 |
|------|------|------|
| **地图渲染** | **D3.js v7** + TopoJSON | ① 原生SVG渲染，完全控制国家边界交互；② 内置地理投影（Natural Earth / Mercator等）；③ 悬停/点击事件绑定灵活；④ 社区成熟，choropleth地图案例丰富 |
| **GeoJSON数据** | **Natural Earth** 1:110m（简化版） | ① 公共领域许可，免费商用；② 文件体积小（~200KB TopoJSON）；③ 包含ISO国家代码，便于数据关联 |
| **UI层** | **原生HTML/CSS/JS** + Tailwind CSS（CDN） | ① 项目为单页面可视化，无需React/Vue等框架的构建复杂度；② Tailwind CDN模式零构建步骤；③ 静态部署友好 |
| **构建工具** | 无需构建 | 纯静态文件，CDN引入依赖，GitHub Pages直接托管 |

### 2.2 数据存储

| 层面 | 选型 | 理由 |
|------|------|------|
| **主存储** | **JSON文件**（Git仓库内） | ① 无需数据库服务，零成本；② Git版本控制，数据变更有历史记录；③ 静态托管可直接访问；④ 结构简单，便于手动审查和编辑 |
| **文件结构** | `data/cases.json`（精简字段主文件）+ `data/countries.json`（国家汇总，自动生成） | 主文件仅保留地图展示与侧边栏所需字段，详情字段按需加载（详见"八、前端数据加载策略"） |

### 2.3 部署方案

| 层面 | 选型 | 理由 |
|------|------|------|
| **托管平台** | **GitHub Pages**（主方案） | ① 免费额度充足（1GB存储/100GB月流量）；② 支持自定义域名和HTTPS；③ 与GitHub Actions同生态，CI/CD无缝集成 |
| **备选方案** | CloudStudio（WorkBuddy内置） | 国内访问速度更快，但自动化集成需额外配置 |

### 2.4 自动化调度（半自动化方案）

#### 2.4.1 调度引擎

| 层面 | 选型 | 理由 |
|------|------|------|
| **调度引擎** | **GitHub Actions** Cron | ① 公开仓库免费2000分钟/月，月度任务远在额度内；② 原生支持Cron表达式（`0 0 1 * *`每月1号执行）；③ 与代码仓库和Pages部署一体化 |

#### 2.4.2 初期支持的自动源清单

> **重要范围定义**：本项目仅收录各国**数据保护机构（DPA）**针对航空业开出的行政决定，以及涉及航空数据隐私/数据泄露的**法院判决**。航空安全、消费者延误赔偿、噪音、环境等非数据类处罚不在收录范围。详见 `docs/data-source-catalog.md` 第一章。

以下为经任务2（数据源调研）验证后的可用来源，按评估等级分类。每个A级和B级来源编写专用采集脚本。

**A级（全自动采集）：**

| # | 国家 | 来源名称 | 类型 | URL | 采集方式 |
|---|------|----------|------|-----|----------|
| 1 | 欧盟 | GDPR Enforcement Tracker | 行政 | `https://www.enforcementtracker.com/` | HTML页面抓取（3,194条GDPR执法记录，按Sector筛选Transport） |
| 2 | 美国 | FTC — Cases and Proceedings | 行政 | `https://www.ftc.gov/enforcement/cases-proceedings` | HTML分页抓取（6,086条，Industry筛选Transportation） |
| 3 | 美国 | CourtListener (Free Law Project) | 法院 | `https://www.courtlistener.com/api/rest/v4/search/` | REST API（免费Token，125次/天） |
| 4 | 法国 | CNIL — Sanctions | 行政 | `https://www.cnil.fr/en/investigation-powers-cnil/sanctions-issued-cnil` | HTML页面抓取（~252条制裁，按年份分组表格） |
| 5 | 英国 | ICO — Enforcement Action | 行政 | `https://ico.org.uk/action-weve-taken/enforcement/` | JS动态加载（Sector筛选Transport and leisure，需发现后端API） |
| 6 | 西班牙 | AEPD — Resoluciones | 行政 | `https://www.aepd.es/publicaciones-y-resoluciones` | HTML页面抓取（概念筛选器：制裁决议） |

**B级（半自动，需额外解析或后处理）：**

| # | 国家 | 来源名称 | 类型 | URL | 采集方式 |
|---|------|----------|------|-----|----------|
| 7 | 欧盟 | CURIA — Court of Justice of the EU | 法院 | `https://juris.curia.europa.eu/jrecherche.jsf?language=en` | HTML搜索结果页抓取 |
| 8 | 加拿大 | OPC — Actions and Decisions | 行政 | `https://www.priv.gc.ca/en/opc-actions-and-decisions/` | HTML页面抓取（需导航至Investigations子页面） |
| 9 | 澳大利亚 | OAIC — Privacy Decisions | 行政 | `https://www.oaic.gov.au/privacy/privacy-assessments-and-decisions/privacy-decisions` | HTML页面抓取（3个子分类导航） |
| 10 | 新加坡 | PDPC — Enforcement Decisions | 行政 | `https://www.pdpc.gov.sg/organisations/regulations-decisions/enforcement-decisions` | JS动态加载（Type+Year筛选） |
| 11 | 英国 | BAILII — British and Irish Legal Information Institute | 法院 | `https://www.bailii.org/` | HTML搜索结果页抓取（有Anubis反爬PoW，需Selenium） |

> **重要修正（相比旧版目录）**：
> - 数据源从"航空管理机构"（DOT/FAA/CASA/CTA/CAAC/CAA/LBA/DGAC/CAAS/DGCA/JCAB/MOLIT/ANAC/GCAA）**全面转为"数据保护机构"**（DPA）。
> - 航空业仅作为被执法的行业过滤器（关键词筛选），而非执法主体。
> - 完整数据源目录详见 `docs/data-source-catalog.md`。

#### 2.4.2.1 采集关键词过滤规则

每个采集脚本**必须**使用以下关键词组合筛选航空数据相关案例：

**航空实体关键词（OR 组合）：**
```
aviation OR airline OR aircraft OR airport OR passenger OR flight OR
carrier OR airway OR aeronautic OR GDS OR "booking system"
```

**数据/隐私关键词（OR 组合）：**
```
"data protection" OR "data privacy" OR "personal data" OR "personal information" OR
"data breach" OR GDPR OR PNR OR "passenger name record"
```

**组合逻辑**：`航空实体关键词 AND 数据隐私关键词`。对于无法程序化组合关键词的源，需在采集后人工过滤。

#### 2.4.3 增量更新机制

- 每个采集脚本维护一个 `scripts/state/{source_abbr}_state.json` 文件，记录：
  - `last_fetch_time`：上次成功抓取的UTC时间戳
  - `latest_case_id`：该源最新案例的ID（若有API支持）
  - `fetch_count`：累计抓取次数
- 每月运行时，脚本仅拉取 `last_fetch_time` 之后发布的新案例，追加至 `cases.json`
- 新案例的 `id` 由 `aggregate.py` 根据现有最大序号自动递增生成

#### 2.4.4 无法自动化的来源

以下情况的来源**不强制自动化**，改用人工录入工作流：

- 无统一检索入口（仅有散落PDF或新闻稿）
- 需登录/注册才能访问
- 反爬策略严格（验证码、IP封锁、JS渲染等）
- 内容非结构化（扫描件PDF、图片格式的裁决书）

**人工录入工作流**：

1. 维护者从官方来源手动获取案例信息
2. 填写 `data/manual_entries.csv`（与 `cases.json` 字段一一对应）
3. 运行 `scripts/merge_manual.py` 将CSV内容转换并合并至 `cases.json`
4. 提交PR，经审核后合并

#### 2.4.5 月度空结果检测

- GitHub Actions 工作流在采集脚本运行后检测：若某月所有自动源均未发现新案例，自动创建一个 GitHub Issue，标题格式：`[Monthly Check] {YYYY-MM} No new cases found — manual review needed`
- Issue 内容包含：各源的运行状态、上次成功抓取时间、建议人工检查的方向
- 维护者收到通知后手动检查，补充数据或确认当月无新案例后关闭Issue

#### 2.4.6 采集脚本错误处理

- 每个采集脚本独立运行，通过 `try/except` 捕获网络异常（超时、DNS失败、HTTP错误码）和解析失败（DOM结构变更、字段缺失）
- 单个脚本失败**不中断**整体任务，其余脚本继续执行
- 失败时：
  - 输出详细日志至 `scripts/logs/{source_abbr}_{date}.log`
  - 在仓库根目录生成/追加 `manual_review_needed.md`，格式如下：
    ```markdown
    ## 需人工审核的数据源

    | 来源 | 失败时间 | 错误类型 | 错误详情 | 建议操作 |
    |------|----------|----------|----------|----------|
    | US-DOT-Enforcement | 2026-07-01T00:05:32Z | HTTP 503 | Service Unavailable | 检查源站是否正常，必要时手动补充 |
    ```
  - 同步创建 GitHub Issue 通知维护者

---

## 三、项目目录结构

```
aviation-data-penalty-map/
├── index.html                 # 主页面
├── css/
│   └── style.css              # 自定义样式
├── js/
│   ├── main.js                # 入口脚本
│   ├── map.js                 # 地图渲染模块（D3.js）
│   ├── sidebar.js             # 侧边栏交互模块
│   └── data-loader.js         # 数据加载与缓存模块
├── data/
│   ├── cases.json             # 案例主数据
│   ├── countries.json         # 国家汇总数据（自动生成）
│   ├── world-110m.json        # TopoJSON世界地图
│   ├── case_details/          # 案例详情（案例数>2000时启用）
│   └── manual_entries.csv     # 人工录入暂存
├── scripts/
│   ├── collectors/            # 各源专用采集脚本
│   │   ├── collect_eu_gdpr_tracker.py   # A级：GDPR执法追踪器
│   │   ├── collect_us_ftc.py            # A级：FTC执法案件
│   │   ├── collect_us_courtlistener.py  # A级：CourtListener API
│   │   ├── collect_fr_cnil.py           # A级：CNIL制裁
│   │   ├── collect_gb_ico.py            # A级：ICO执法行动
│   │   ├── collect_es_aepd.py           # A级：AEPD决议
│   │   ├── collect_eu_curia.py          # B级：欧盟法院
│   │   ├── collect_ca_opc.py            # B级：加拿大OPC
│   │   ├── collect_au_oaic.py           # B级：澳大利亚OAIC
│   │   ├── collect_sg_pdpc.py           # B级：新加坡PDPC
│   │   └── collect_gb_bailii.py          # B级：英国BAILII法院
│   ├── state/                 # 各源采集状态
│   │   ├── us_dot_state.json
│   │   └── ...
│   ├── logs/                  # 采集日志
│   ├── aggregate.py           # 数据聚合脚本（生成countries.json）
│   ├── validate.py            # 数据校验脚本
│   ├── merge_manual.py        # 人工CSV录入合并脚本
│   └── run_all_collectors.py  # 采集调度入口脚本
├── .github/
│   └── workflows/
│       └── monthly-update.yml # GitHub Actions月度更新工作流
├── manual_review_needed.md    # 采集失败人工审核清单
└── README.md
```

---

## 四、交互设计规范

### 4.1 地图主区域
- 各国按案例总数分5档着色（0: 浅灰, 1-3: 浅蓝, 4-10: 蓝, 11-25: 深蓝, 26+: 深色）
- 鼠标悬停显示Tooltip：国家名称 + 数据保护案例总数
- 点击国家 → 侧边栏更新为该国详情

### 4.2 侧边栏
- 默认：全球统计概览（总案例数、总国家数、法院/行政比例）
- 选中某国后：
  - 国旗 + 国名
  - 法院案例数 → 下方列出法院名称及各法院案例数
  - 行政案例数 → 下方列出机构名称及各机构案例数
  - 点击法院/机构名称 → 展开该机构下的案例列表
  - 每个案例名称为超链接，点击新窗口打开来源URL

### 4.3 响应式
- 桌面端：地图占左侧70%，侧边栏占右侧30%
- 移动端：地图全宽，侧边栏底部抽屉式展开

---

## 五、免费方案验证

| 组件 | 方案 | 免费额度 | 是否满足需求 |
|------|------|----------|-------------|
| 地图库 | D3.js (MIT) | 完全免费 | ✅ |
| GeoJSON | Natural Earth (PD) | 公共领域 | ✅ |
| CSS框架 | Tailwind CDN | 免费 | ✅ |
| 代码托管 | GitHub | 公开仓库免费无限 | ✅ |
| 网站托管 | GitHub Pages | 1GB存储/100GB流量 | ✅ |
| CI/CD | GitHub Actions | 2000分钟/月 | ✅ (月度任务<30分钟) |
| 采集脚本 | Python + requests | 无需服务费 | ✅ |
| 数据存储 | JSON in Git | Git仓库内 | ✅ |

**全链路零成本，无需任何付费服务。**

---

## 六、风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| 部分数据源需翻墙访问 | 采集脚本在GitHub Actions中可能无法访问 | 标记该源为"需手动补充"，在本地采集后提交PR |
| 来源URL失效（404） | 案例链接不可达 | 前端标注"链接已失效"并显示案例名称和日期 |
| 某国无公开案例数据 | 地图上该国为空 | 显示为灰色"暂无数据"，不隐藏国家 |
| GitHub Pages国内访问慢 | 国内用户体验差 | 备选CloudStudio部署国内镜像 |

---

## 七、数据去重与验证

### 7.1 去重规则

新增案例写入 `cases.json` 前，执行以下去重检查：

1. **sourceUrl 去重**：比较新增案例的 `sourceUrl` 与已有记录。若完全匹配，跳过录入并记录至 `scripts/logs/dedup_{date}.log`，日志格式：
   ```
   [DEDUP] Source URL already exists: {sourceUrl} → existing case ID: {existing_id}
   ```
2. **caseName 模糊去重**：将 `caseName`（及 `caseNameEn`，若有）统一转为小写并去除首尾空格后比较。若与已有记录完全匹配且 `country` + `caseType` 一致，跳过并记录日志。
3. **去重判定优先级**：`sourceUrl` 精确匹配 > `caseName` 归一化匹配。两者任一命中即判定为重复。

### 7.2 校验强化

`validate.py` 脚本在每次数据更新后自动运行，检查项如下：

| 检查项 | 级别 | 规则 | 处理方式 |
|--------|------|------|----------|
| 必填字段非空 | **错误** | `id`, `caseName`, `country`, `date`, `sourceUrl` 不可为空/null/缺失 | 中断提交，输出错误报告 |
| ID格式唯一 | **错误** | 符合 `{ISO2}-{C\|A}-{数字}` 格式且全局唯一 | 中断提交，列出冲突ID |
| 日期有效性 | **错误** | 为有效 ISO 8601 日期（`YYYY-MM-DD`），且不晚于当前日期 | 中断提交，列出无效日期 |
| sourceUrl可访问性 | **警告** | HTTP GET 返回 2xx 状态码 | 不阻断，输出警告列表至 `scripts/logs/url_check_{date}.log` |
| country合法性 | **错误** | 为有效 ISO 3166-1 alpha-2 代码 | 中断提交，列出无效代码 |
| caseType合法性 | **错误** | 仅允许 `court` 或 `admin` | 中断提交，列出非法值 |

校验脚本退出码规则：
- 存在**错误**级问题 → 退出码 1（CI流程中断）
- 仅有**警告**级问题 → 退出码 0（CI流程继续，但日志需人工复查）
- 无问题 → 退出码 0

---

## 八、前端数据加载策略

### 8.1 精简主数据文件

`data/cases.json` 仅存储地图展示和侧边栏列表所需的字段：

```json
[
  {
    "id": "US-C-001",
    "caseName": "FTC v. Delta Air Lines, Inc.",
    "country": "US",
    "caseType": "court",
    "authority": "Federal Trade Commission",
    "date": "2014-01-15",
    "sourceUrl": "https://www.ftc.gov/legal-library/browse/cases-proceedings/..."
  }
]
```

以下字段移至 `data/case_details/` 目录下按ID存储的独立文件（如 `data/case_details/US-C-001.json`）：

- `caseNameEn`、`summary`、`tags`、`lastVerified`、`authorityShort`

> **当前阶段（案例数 < 2000）**：为简化首版实现，`case_details/` 目录暂不创建，所有字段保留在 `cases.json` 中。前端按需展示时直接从主文件过滤，不做额外网络请求。

### 8.2 按需加载案例详情

- 侧边栏点击某机构展开案例列表时，前端从 `cases.json` 中按 `country` + `authority` 过滤，直接展示案例名称和链接，**无需额外请求**
- 当案例总数超过 **2000 条**时，启动分机构存储方案：
  - `aggregate.py` 自动将 `cases.json` 拆分为 `data/cases_by_authority/{authority_id}.json`
  - 前端点击机构时异步加载对应JSON文件
  - 拆分触发条件：`cases.json` 文件体积 > 500KB

### 8.3 前端缓存策略

| 数据 | 缓存方式 | 过期策略 | 说明 |
|------|----------|----------|------|
| `countries.json` | `localStorage` | 每次加载时比对版本号（文件内含 `version` 字段） | 避免每次打开页面重复请求聚合数据 |
| `world-110m.json` | `localStorage` | 版本号比对（文件内含 `version` 字段） | 地图GeoJSON数据变更极少，长期缓存 |
| `cases.json` | 不缓存 | 每次从服务端获取 | 确保案例数据为最新 |

缓存失效逻辑：
1. 页面加载时，读取 `localStorage` 中的 `version` 字段
2. Fetch `countries.json`（或地图数据）的 `version` 字段（仅请求头部或比对ETag）
3. 若版本号不同，重新拉取全量数据并更新缓存
4. 若版本号相同，使用缓存数据，跳过网络请求
