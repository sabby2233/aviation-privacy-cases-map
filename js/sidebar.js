/**
 * sidebar.js — 侧边栏交互模块
 *
 * 职责：
 * 1. 全球统计概览（默认视图）
 * 2. 国家详情视图（点击国家后）
 * 3. 机构展开 → 案例列表
 * 4. 案例名称超链接至来源URL
 */

const Sidebar = (() => {
  'use strict';

  let casesData = [];
  let countriesData = null;

  /**
   * Initialize sidebar with data
   * @param {Array} cases
   * @param {Object} countries
   */
  function init(cases, countries) {
    casesData = cases;
    countriesData = countries;

    document.getElementById('back-to-global').addEventListener('click', () => {
      showGlobalOverview();
      MapRenderer.resetHighlight();
    });
  }

  /**
   * Show global overview (default state)
   */
  function showGlobalOverview() {
    document.getElementById('sidebar-global').classList.remove('hidden');
    document.getElementById('sidebar-country').classList.add('hidden');

    if (!countriesData) return;

    const { totalCountries, totalCases, countries } = countriesData;

    // Calculate totals
    let totalCourt = 0;
    let totalAdmin = 0;
    let totalLowAltitude = 0;
    let totalAviation = 0;
    for (const info of Object.values(countries)) {
      totalCourt += (info.courtCount || info.courtCases || 0);
      totalAdmin += (info.adminCount || info.adminCases || 0);
      totalLowAltitude += (info.lowAltitudeCount || info.lowAltitudeCases || 0);
      totalAviation += (info.aviationCount || info.aviationCases || 0);
    }

    // Render stats
    const statsEl = document.getElementById('global-stats');
    statsEl.innerHTML = `
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-gray-800/50 rounded-lg p-3 text-center">
          <div class="text-2xl font-bold text-sky-400">${totalCases}</div>
          <div class="text-xs text-gray-500 mt-1">案例总数</div>
        </div>
        <div class="bg-gray-800/50 rounded-lg p-3 text-center">
          <div class="text-2xl font-bold text-gray-200">${totalCountries}</div>
          <div class="text-xs text-gray-500 mt-1">涉及国家/地区</div>
        </div>
      </div>
      <div class="grid grid-cols-3 gap-3">
        <div class="bg-gray-800/50 rounded-lg p-3 text-center">
          <div class="text-2xl font-bold text-amber-400">${totalCourt}</div>
          <div class="text-xs text-gray-500 mt-1">法院判决</div>
        </div>
        <div class="bg-gray-800/50 rounded-lg p-3 text-center">
          <div class="text-2xl font-bold text-emerald-400">${totalAdmin}</div>
          <div class="text-xs text-gray-500 mt-1">行政决定</div>
        </div>
        <div class="bg-gray-800/50 rounded-lg p-3 text-center">
          <div class="text-2xl font-bold text-violet-400">${totalLowAltitude}</div>
          <div class="text-xs text-gray-500 mt-1">低空类</div>
        </div>
      </div>
    `;

    // Country list — sorted by totalCases desc
    const sorted = Object.entries(countries)
      .sort((a, b) => b[1].totalCases - a[1].totalCases);

    const listEl = document.getElementById('country-list');
    listEl.innerHTML = sorted.map(([code, info]) => `
      <button class="w-full flex items-center justify-between px-3 py-2 rounded-md hover:bg-gray-800/70 transition-colors text-left group"
              data-country="${code}">
        <div class="flex items-center gap-2">
          <span class="text-xs font-mono text-gray-500">${code}</span>
          <span class="text-sm text-gray-300 group-hover:text-gray-100">${info.name || info.countryName || code}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center gap-1 text-xs">
            <span class="text-amber-400">${info.courtCount || info.courtCases || 0}</span>
            <span class="text-gray-600">/</span>
            <span class="text-emerald-400">${info.adminCount || info.adminCases || 0}</span>
            ${(info.lowAltitudeCount || info.lowAltitudeCases || 0) > 0 ? `<span class="text-gray-600">/</span><span class="text-violet-400">${info.lowAltitudeCount || info.lowAltitudeCases || 0}低</span>` : ''}
          </span>
          <span class="text-sm font-semibold text-sky-400">${info.totalCases}</span>
        </div>
      </button>
    `).join('');

    // Bind click handlers
    listEl.querySelectorAll('button[data-country]').forEach(btn => {
      btn.addEventListener('click', () => {
        const code = btn.dataset.country;
        showCountryDetail(code);
        MapRenderer.highlightCountry(code);
      });
    });
  }

  /**
   * Show country detail view
   * @param {string} alpha2 - ISO 3166-1 alpha-2 code
   */
  function showCountryDetail(alpha2) {
    document.getElementById('sidebar-global').classList.add('hidden');
    document.getElementById('sidebar-country').classList.remove('hidden');

    // Get all codes in the same map group (e.g. CN + HK + MO)
    const codes = DataLoader.getMapGroup(alpha2);

    // Collect info for all codes in the group
    let totalCases = 0, courtCases = 0, adminCases = 0;
    let aviationCases = 0, lowAltitudeCases = 0;
    const groupInfos = [];
    for (const code of codes) {
      const info = countriesData?.countries?.[code];
      if (info) {
        totalCases += info.totalCases;
        courtCases += (info.courtCount || info.courtCases || 0);
        adminCases += (info.adminCount || info.adminCases || 0);
        aviationCases += (info.aviationCount || info.aviationCases || 0);
        lowAltitudeCases += (info.lowAltitudeCount || info.lowAltitudeCases || 0);
        groupInfos.push(info);
      }
    }
    if (groupInfos.length === 0) return;

    // Header — show primary country name, mention territories if grouped
    const primaryInfo = countriesData?.countries?.[alpha2];
    const territoryNames = groupInfos
      .filter(i => i.code !== alpha2)
      .map(i => i.name || i.countryName);

    const headerEl = document.getElementById('country-header');
    headerEl.innerHTML = `
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-sky-900/40 flex items-center justify-center text-lg font-bold text-sky-400">
          ${alpha2}
        </div>
        <div>
          <h2 class="text-lg font-semibold text-gray-100">${primaryInfo ? (primaryInfo.name || primaryInfo.countryName || alpha2) : alpha2}</h2>
          <div class="text-xs text-gray-500 mt-0.5">
            共 ${totalCases} 个案例 —
            <span class="text-emerald-400">${aviationCases} 一般航空</span>
            ${lowAltitudeCases > 0 ? ` / <span class="text-violet-400">${lowAltitudeCases} 低空类</span>` : ''}
            <span class="text-amber-400">${courtCases} 法院</span> /
            <span class="text-emerald-400">${adminCases} 行政</span>
            ${territoryNames.length > 0 ? `<br><span class="text-gray-600">含：${territoryNames.join('、')}</span>` : ''}
          </div>
        </div>
      </div>
    `;

    // Cases for this country and its territories (e.g. CN + HK + MO)
    const countryCases = casesData.filter(c => codes.includes(c.country));

    // Group by isLowAltitude first, then by authority
    const aviationCasesList = countryCases.filter(c => !c.isLowAltitude);
    const lowAltitudeCasesList = countryCases.filter(c => c.isLowAltitude);

    const detailEl = document.getElementById('country-detail');
    detailEl.innerHTML = '';

    // Low-altitude section (shown first if any)
    if (lowAltitudeCasesList.length > 0) {
      detailEl.appendChild(createClassificationSection('低空类数据执法案例', lowAltitudeCasesList, 'violet'));
    }

    // General aviation section
    if (aviationCasesList.length > 0) {
      detailEl.appendChild(createClassificationSection('一般航空数据执法案例', aviationCasesList, 'sky'));
    }
  }

  /**
   * Create a classification section with authorities grouped within
   */
  function createClassificationSection(title, casesList, accentColor) {
    const section = document.createElement('div');
    section.className = 'mb-4';

    const titleColorClass = accentColor === 'violet' ? 'text-violet-400' : 'text-sky-400';
    const icon = accentColor === 'violet'
      ? '<path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>'
      : '<path d="M12 2L2 22h20L12 2z"/><path d="M12 18v-4"/><path d="M12 10h.01"/>';

    section.innerHTML = `
      <h3 class="text-xs font-semibold ${titleColorClass} uppercase tracking-wider mb-2 flex items-center gap-1.5">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          ${icon}
        </svg>
        ${title}
        <span class="text-gray-500 normal-case">(${casesList.length})</span>
      </h3>
    `;

    // Group by authority within this classification
    const authorityGroups = {};
    for (const c of casesList) {
      const key = c.authority;
      if (!authorityGroups[key]) {
        authorityGroups[key] = {
          name: key,
          short: c.authorityShort || key,
          type: c.caseType,
          cases: []
        };
      }
      authorityGroups[key].cases.push(c);
    }

    // Admin sub-section
    const adminAuthorities = Object.values(authorityGroups).filter(g => g.type === 'admin');
    if (adminAuthorities.length > 0) {
      section.appendChild(createAuthoritySection('行政决定', adminAuthorities, 'admin'));
    }

    // Court sub-section
    const courtAuthorities = Object.values(authorityGroups).filter(g => g.type === 'court');
    if (courtAuthorities.length > 0) {
      section.appendChild(createAuthoritySection('法院判决', courtAuthorities, 'court'));
    }

    return section;
  }

  /**
   * Create an authority section with expandable cases
   */
  function createAuthoritySection(title, authorities, type) {
    const section = document.createElement('div');
    const icon = type === 'admin' ? 'shield' : 'gavel';
    // Use explicit class names (Tailwind CDN can't detect dynamic interpolation)
    const titleColorClass = type === 'admin' ? 'text-emerald-400' : 'text-amber-400';

    section.innerHTML = `
      <h3 class="text-xs font-semibold ${titleColorClass} uppercase tracking-wider mb-2 flex items-center gap-1.5">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          ${type === 'admin'
            ? '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
            : '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>'
          }
        </svg>
        ${title}
      </h3>
    `;

    for (const auth of authorities) {
      const authDiv = document.createElement('div');
      authDiv.className = 'mb-2';

      const authBtn = document.createElement('button');
      authBtn.className = `w-full flex items-center justify-between px-3 py-2 rounded-md bg-gray-800/50 hover:bg-gray-800/80 transition-colors text-left`;
      authBtn.innerHTML = `
        <span class="text-sm text-gray-300">${auth.short}</span>
        <span class="flex items-center gap-1">
          <span class="text-xs text-gray-500">${auth.cases.length} 案例</span>
          <svg class="w-3 h-3 text-gray-500 transition-transform auth-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 9l-7 7-7-7"/></svg>
        </span>
      `;

      const casesList = document.createElement('div');
      casesList.className = 'hidden mt-1 ml-2 space-y-1 border-l-2 border-gray-800 pl-3';
      casesList.innerHTML = auth.cases
        .sort((a, b) => (b.date || '').localeCompare(a.date || ''))
        .map(c => `
          <a href="${c.sourceUrl}" target="_blank" rel="noopener noreferrer"
             class="flex items-start gap-2 px-2 py-1.5 rounded hover:bg-gray-800/50 transition-colors group/case">
            <span class="text-xs text-gray-600 mt-0.5 shrink-0">${(c.date || '').slice(0, 4)}</span>
            <span class="text-sm text-gray-300 group-hover/case:text-sky-400 transition-colors leading-snug">${c.caseNameEn || c.caseName}</span>
            <svg class="w-3 h-3 text-gray-600 group-hover/case:text-sky-400 shrink-0 mt-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3"/></svg>
          </a>
        `).join('');

      // Toggle expand
      authBtn.addEventListener('click', () => {
        const isHidden = casesList.classList.contains('hidden');
        casesList.classList.toggle('hidden');
        const chevron = authBtn.querySelector('.auth-chevron');
        if (isHidden) {
          chevron.style.transform = 'rotate(180deg)';
        } else {
          chevron.style.transform = 'rotate(0deg)';
        }
      });

      authDiv.appendChild(authBtn);
      authDiv.appendChild(casesList);
      section.appendChild(authDiv);
    }

    return section;
  }

  return {
    init,
    showGlobalOverview,
    showCountryDetail
  };
})();
