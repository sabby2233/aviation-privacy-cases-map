/**
 * main.js — 入口脚本
 *
 * 1. 调用 DataLoader.loadAll() 并行加载全部数据
 * 2. 初始化 Sidebar 和 MapRenderer
 * 3. 绑定国家点击 → 侧边栏切换
 * 4. 设置最后更新日期
 */

(async function main() {
  'use strict';

  try {
    // Load all data in parallel
    const { cases, countries, world } = await DataLoader.loadAll();

    // Get country name map for tooltips
    const countryNameMap = DataLoader.getCountryNameMap(countries);

    // Initialize sidebar first (so it can render stats)
    Sidebar.init(cases, countries);

    // Render global overview by default
    Sidebar.showGlobalOverview();

    // Initialize map
    MapRenderer.init(world, countries, countryNameMap, (alpha2) => {
      // onCountryClick
      Sidebar.showCountryDetail(alpha2);
    }, (alpha2) => {
      // onCountryHover (optional)
    });

    // Set last updated date
    const lastUpdatedEl = document.getElementById('last-updated');
    if (lastUpdatedEl && countries) {
      lastUpdatedEl.textContent = countries.version || countries.generatedAt || '-';
    }

  } catch (err) {
    console.error('Failed to initialize app:', err);
    const loadingEl = document.getElementById('map-loading');
    if (loadingEl) {
      loadingEl.innerHTML = `
        <div class="text-red-400 text-sm text-center p-4">
          <p class="font-semibold">数据加载失败</p>
          <p class="text-xs text-gray-500 mt-1">${err.message}</p>
        </div>
      `;
      loadingEl.classList.remove('hidden');
    }
  }
})();
