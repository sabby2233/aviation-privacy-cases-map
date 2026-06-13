/**
 * map.js — D3.js 世界地图渲染模块
 *
 * 职责：
 * 1. 渲染 Natural Earth 投影的 SVG 世界地图
 * 2. Choropleth 着色（5档案例数量）
 * 3. 鼠标悬停 Tooltip
 * 4. 点击国家 → 触发侧边栏更新
 * 5. 图例
 */

const MapRenderer = (() => {
  'use strict';

  let svg, g, projection, pathGenerator;
  let countryPaths;
  let onCountryClick = null;
  let onCountryHover = null;
  let caseDataMap = {}; // alpha2 → { totalCases, courtCases, adminCases }

  // Color scale — 5 tiers
  const COLOR_NONE  = '#1e293b'; // slate-800
  const COLOR_TIERS = ['#38bdf8', '#0ea5e9', '#0284c7', '#075985']; // sky-400 → sky-700
  const COLOR_NO_DATA = '#111827'; // gray-900

  /**
   * Determine fill color based on case count
   */
  function getColor(totalCases) {
    if (totalCases === 0 || totalCases == null) return COLOR_NONE;
    if (totalCases >= 1 && totalCases <= 2) return COLOR_TIERS[0];
    if (totalCases >= 3 && totalCases <= 5) return COLOR_TIERS[1];
    if (totalCases >= 6 && totalCases <= 10) return COLOR_TIERS[2];
    return COLOR_TIERS[3]; // 11+
  }

  const LEGEND_ITEMS = [
    { label: '0', color: COLOR_NONE },
    { label: '1-2', color: COLOR_TIERS[0] },
    { label: '3-5', color: COLOR_TIERS[1] },
    { label: '6-10', color: COLOR_TIERS[2] },
    { label: '11+', color: COLOR_TIERS[3] }
  ];

  /**
   * Initialize the map
   * @param {Object} worldTopoJSON - TopoJSON world data
   * @param {Object} countriesData - countries.json data
   * @param {Object} countryNameMap - alpha2 → country name (Chinese)
   * @param {Function} onClick - callback(alpha2) when a country is clicked
   * @param {Function} onHover - callback(alpha2 | null) on hover
   */
  function init(worldTopoJSON, countriesData, countryNameMap, onClick, onHover) {
    onCountryClick = onClick;
    onCountryHover = onHover;

    // Build case data map from countriesData
    // Merge aliased territories (e.g. HK → CN) into parent for map display
    caseDataMap = {};
    if (countriesData && countriesData.countries) {
      for (const [code, info] of Object.entries(countriesData.countries)) {
        const mapCode = DataLoader.resolveMapAlias(code);
        if (!caseDataMap[mapCode]) {
          caseDataMap[mapCode] = { totalCases: 0, courtCases: 0, adminCases: 0 };
        }
        caseDataMap[mapCode].totalCases += (info.totalCount || info.totalCases || 0);
        caseDataMap[mapCode].courtCases += (info.courtCount || info.courtCases || 0);
        caseDataMap[mapCode].adminCases += (info.adminCount || info.adminCases || 0);
      }
    }

    const container = document.getElementById('map-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Projection — EqualEarth (D3 v7 built-in, excellent for world maps)
    // Fallback chain: EqualEarth → NaturalEarth1 → Mercator
    let projFn;
    if (typeof d3.geoEqualEarth === 'function') {
      projFn = d3.geoEqualEarth();
    } else if (typeof d3.geoNaturalEarth1 === 'function') {
      projFn = d3.geoNaturalEarth1();
    } else {
      projFn = d3.geoMercator();
    }
    projection = projFn
      .scale(width / 5.4)
      .translate([width / 2, height / 2]);

    pathGenerator = d3.geoPath().projection(projection);

    // Create SVG
    svg = d3.select('#world-map')
      .attr('width', width)
      .attr('height', height);

    // Clear previous
    svg.selectAll('*').remove();

    // Water background
    svg.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', '#030712'); // gray-950

    g = svg.append('g');

    // Sphere outline (graticule border)
    g.append('path')
      .datum({ type: 'Sphere' })
      .attr('d', pathGenerator)
      .attr('fill', 'none')
      .attr('stroke', '#1e293b')
      .attr('stroke-width', 0.5);

    // Graticule (D3v7 API)
    const graticule = d3.geoGraticule().step([10, 10]);
    g.append('path')
      .datum(graticule())
      .attr('d', pathGenerator)
      .attr('fill', 'none')
      .attr('stroke', '#1e293b')
      .attr('stroke-width', 0.2);

    // Convert TopoJSON → GeoJSON features
    const features = topojson.feature(worldTopoJSON, worldTopoJSON.objects.countries).features;

    // Draw countries
    countryPaths = g.selectAll('path.country')
      .data(features)
      .enter()
      .append('path')
      .attr('class', 'country')
      .attr('d', pathGenerator)
      .attr('fill', d => {
        const alpha2 = DataLoader.numericToAlpha2(d.id);
        const mapCode = DataLoader.resolveMapAlias(alpha2);
        const info = caseDataMap[mapCode];
        if (!info || info.totalCases === 0) return COLOR_NONE;
        return getColor(info.totalCases);
      })
      .attr('stroke', '#334155') // slate-700
      .attr('stroke-width', 0.3)
      .on('mouseenter', function(event, d) {
        const alpha2 = DataLoader.numericToAlpha2(d.id);
        const mapCode = DataLoader.resolveMapAlias(alpha2);
        const name = countryNameMap[alpha2] || countryNameMap[mapCode] || d.properties?.name || alpha2 || 'Unknown';
        const info = caseDataMap[mapCode] || caseDataMap[alpha2];
        const count = info ? (info.totalCases || info.totalCount || 0) : 0;
        const adminCount = info ? (info.adminCases || info.adminCount || 0) : 0;
        const courtCount = info ? (info.courtCases || info.courtCount || 0) : 0;

        // Highlight
        d3.select(this)
          .attr('stroke', '#38bdf8')
          .attr('stroke-width', 1.5)
          .raise();

        // Show tooltip
        const tooltip = document.getElementById('tooltip');
        const tooltipCountry = document.getElementById('tooltip-country');
        const tooltipCount = document.getElementById('tooltip-count');

        tooltipCountry.textContent = name;
        tooltipCount.textContent = count > 0
          ? `${count} 个数据保护案例 (行政 ${adminCount} / 法院 ${courtCount})`
          : '暂无案例数据';

        tooltip.classList.remove('hidden');

        // Position tooltip
        const [mx, my] = d3.pointer(event, container);
        tooltip.style.left = (mx + 15) + 'px';
        tooltip.style.top = (my - 10) + 'px';

        if (onCountryHover) onCountryHover(alpha2);
      })
      .on('mousemove', function(event) {
        const tooltip = document.getElementById('tooltip');
        const [mx, my] = d3.pointer(event, container);
        tooltip.style.left = (mx + 15) + 'px';
        tooltip.style.top = (my - 10) + 'px';
      })
      .on('mouseleave', function() {
        d3.select(this)
          .attr('stroke', '#334155')
          .attr('stroke-width', 0.3);

        document.getElementById('tooltip').classList.add('hidden');
        if (onCountryHover) onCountryHover(null);
      })
      .on('click', function(event, d) {
        const alpha2 = DataLoader.numericToAlpha2(d.id);
        const mapCode = DataLoader.resolveMapAlias(alpha2);
        // Check if this country (or its parent) has cases
        const hasCases = caseDataMap[alpha2]?.totalCases > 0 || caseDataMap[mapCode]?.totalCases > 0;
        if (hasCases && onCountryClick) {
          // Prefer clicking on the actual code (not alias) if it has data
          const codeToShow = caseDataMap[alpha2]?.totalCases > 0 ? alpha2 : mapCode;
          onCountryClick(codeToShow);
        }
      });

    // Hide loading
    document.getElementById('map-loading').classList.add('hidden');

    // Render legend
    renderLegend();

    // Handle resize
    window.addEventListener('resize', debounce(() => {
      resizeMap(worldTopoJSON, countryNameMap);
    }, 300));
  }

  /**
   * Render the color legend
   */
  function renderLegend() {
    const container = document.getElementById('legend-items');
    container.innerHTML = '';
    LEGEND_ITEMS.forEach(item => {
      const row = document.createElement('div');
      row.className = 'flex items-center gap-2';
      row.innerHTML = `
        <span class="inline-block w-3 h-3 rounded-sm shrink-0" style="background:${item.color}"></span>
        <span class="text-gray-400">${item.label}</span>
      `;
      container.appendChild(row);
    });
  }

  /**
   * Highlight a country on the map
   */
  function highlightCountry(alpha2) {
    if (!countryPaths) return;
    countryPaths
      .attr('stroke', d => {
        const id = DataLoader.numericToAlpha2(d.id);
        return id === alpha2 ? '#38bdf8' : '#334155';
      })
      .attr('stroke-width', d => {
        const id = DataLoader.numericToAlpha2(d.id);
        return id === alpha2 ? 1.5 : 0.3;
      });
  }

  /**
   * Reset highlights
   */
  function resetHighlight() {
    if (!countryPaths) return;
    countryPaths
      .attr('stroke', '#334155')
      .attr('stroke-width', 0.3);
  }

  /**
   * Resize map on window resize
   */
  function resizeMap(worldTopoJSON, countryNameMap) {
    const container = document.getElementById('map-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    projection
      .scale(width / 5.4)
      .translate([width / 2, height / 2]);

    svg.attr('width', width).attr('height', height);
    svg.select('rect').attr('width', width).attr('height', height);
    g.selectAll('path').attr('d', pathGenerator);
  }

  /**
   * Simple debounce
   */
  function debounce(fn, delay) {
    let timer;
    return function(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  return {
    init,
    highlightCountry,
    resetHighlight
  };
})();
