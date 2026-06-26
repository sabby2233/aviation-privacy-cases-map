/**
 * data-loader.js — 数据加载与缓存模块
 *
 * 职责：
 * 1. 加载 cases.json / countries.json / world-110m.json
 * 2. localStorage 缓存（countries.json + world-110m.json，版本号比对）
 * 3. ISO 3166-1 numeric → alpha-2 映射
 */

const DataLoader = (() => {
  'use strict';

  // ── ISO 3166-1 Numeric → Alpha-2 mapping ──
  // Full list covering all countries in Natural Earth 1:110m
  const ISO_NUMERIC_MAP = {
    4:"AF",8:"AL",12:"DZ",20:"AD",24:"AO",28:"AG",32:"AR",51:"AM",
    36:"AU",40:"AT",31:"AZ",44:"BS",48:"BH",50:"BD",52:"BB",112:"BY",
    56:"BE",84:"BZ",204:"BJ",64:"BT",68:"BO",70:"BA",72:"BW",76:"BR",
    96:"BN",100:"BG",854:"BF",108:"BI",116:"KH",120:"CM",124:"CA",140:"CF",
    148:"TD",152:"CL",156:"CN",170:"CO",174:"KM",178:"CG",180:"CD",188:"CR",
    384:"CI",191:"HR",192:"CU",196:"CY",203:"CZ",208:"DK",262:"DJ",212:"DM",
    214:"DO",218:"EC",818:"EG",222:"SV",226:"GQ",232:"ER",233:"EE",748:"SZ",
    231:"ET",242:"FJ",246:"FI",250:"FR",266:"GA",270:"GM",268:"GE",276:"DE",
    288:"GH",300:"GR",308:"GD",320:"GT",324:"GN",624:"GW",332:"HT",340:"HN",
    348:"HU",352:"IS",356:"IN",360:"ID",364:"IR",368:"IQ",372:"IE",376:"IL",
    380:"IT",388:"JM",392:"JP",400:"JO",398:"KZ",404:"KE",408:"KP",410:"KR",
    414:"KW",417:"KG",418:"LA",428:"LV",422:"LB",426:"LS",430:"LR",440:"LT",
    442:"LU",450:"MG",454:"MW",458:"MY",462:"MV",466:"ML",470:"MT",584:"MH",
    478:"MR",484:"MX",498:"MD",496:"MN",499:"ME",504:"MA",508:"MZ",104:"MM",
    516:"NA",524:"NP",528:"NL",554:"NZ",558:"NI",562:"NE",566:"NG",578:"NO",
    512:"OM",586:"PK",591:"PA",598:"PG",600:"PY",604:"PE",608:"PH",616:"PL",
    620:"PT",634:"QA",642:"RO",643:"RU",646:"RW",682:"SA",686:"SN",688:"RS",
    694:"SL",702:"SG",703:"SK",705:"SI",90:"SB",706:"SO",710:"ZA",728:"SS",
    724:"ES",144:"LK",729:"SD",740:"SR",752:"SE",756:"CH",760:"SY",158:"TW",
    762:"TJ",834:"TZ",764:"TH",626:"TL",768:"TG",780:"TT",788:"TN",792:"TR",
    795:"TM",800:"UG",804:"UA",784:"AE",826:"GB",840:"US",858:"UY",860:"UZ",
    548:"VU",862:"VE",704:"VN",887:"YE",894:"ZM",716:"ZW"
  };

  // Territories without independent map geometry → parent country for map display
  const MAP_ALIASES = {
    'HK': 'CN',  // 中国香港 → China
    'MO': 'CN',  // 中国澳门 → China
    'PR': 'US',  // 波多黎各 → US
    'GP': 'FR',  // 瓜德罗普 → France
    'GL': 'DK',  // 格陵兰 → Denmark
    'AW': 'NL',  // 阿鲁巴 → Netherlands
    'CW': 'NL',  // 库拉索 → Netherlands
  };

  // Cache keys
  const CACHE_KEY_COUNTRIES = 'avdp_countries';
  const CACHE_KEY_WORLD = 'avdp_world';
  const CACHE_VERSION_COUNTRIES = 'avdp_countries_version';
  const CACHE_VERSION_WORLD = 'avdp_world_version';

  /**
   * Generic fetch with localStorage cache
   * Supports both http(s) and file:// protocols
   */
  async function fetchWithCache(url, cacheKey, versionKey) {
    try {
      const data = await _fetchJSON(url);
      const version = data.version || data.generatedAt || Date.now().toString();

      // Try to cache
      try {
        localStorage.setItem(cacheKey, JSON.stringify(data));
        localStorage.setItem(versionKey, version);
      } catch (e) {
        console.warn('localStorage write failed:', e.message);
      }

      return data;
    } catch (err) {
      // Network failed — try cache fallback
      try {
        const cached = localStorage.getItem(cacheKey);
        if (cached) {
          console.warn(`Using cached data for ${url}`);
          return JSON.parse(cached);
        }
      } catch (e) { /* ignore */ }
      throw err;
    }
  }

  /**
   * Fetch JSON — works on both http(s) and file:// protocols
   * On file://, falls back to XMLHttpRequest
   */
  async function _fetchJSON(url) {
    // Normal HTTP(S) path
    if (!url.startsWith('file:')) {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    }

    // file:// protocol fallback — use XHR which works in some browsers
    // Also try to rewrite file:// URL to a relative path for XHR
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('GET', url, true);
      xhr.responseType = 'json';
      xhr.onload = () => {
        if (xhr.status === 0 || xhr.status === 200) {
          resolve(xhr.response);
        } else {
          reject(new Error(`XHR status ${xhr.status}`));
        }
      };
      xhr.onerror = () => reject(new Error('Failed to fetch (file:// protocol blocked). Use a local HTTP server instead.'));
      xhr.send();
    });
  }

  /**
   * Normalize countries.json field names for backward compatibility.
   * Handles both old (totalCount/countryName) and new (totalCases/name) field names.
   */
  function normalizeCountriesData(data) {
    if (!data || !data.countries) return data;
    for (const [code, info] of Object.entries(data.countries)) {
      // totalCount → totalCases
      if (info.totalCount !== undefined && info.totalCases === undefined) {
        info.totalCases = info.totalCount;
      }
      // adminCount → adminCases
      if (info.adminCount !== undefined && info.adminCases === undefined) {
        info.adminCases = info.adminCount;
      }
      // courtCount → courtCases
      if (info.courtCount !== undefined && info.courtCases === undefined) {
        info.courtCases = info.courtCount;
      }
      // aviationCount → aviationCases
      if (info.aviationCount !== undefined && info.aviationCases === undefined) {
        info.aviationCases = info.aviationCount;
      }
      // lowAltitudeCount → lowAltitudeCases
      if (info.lowAltitudeCount !== undefined && info.lowAltitudeCases === undefined) {
        info.lowAltitudeCases = info.lowAltitudeCount;
      }
      // countryName → name
      if (info.countryName !== undefined && info.name === undefined) {
        info.name = info.countryName;
      }
      // Ensure name fallback
      if (!info.name) info.name = code;
    }
    // Add totalCountries if missing
    if (data.totalCountries === undefined && data.countries) {
      data.totalCountries = Object.keys(data.countries).length;
    }
    return data;
  }

  /**
   * Load all required data in parallel
   */
  async function loadAll() {
    const [cases, countries, world] = await Promise.all([
      _fetchJSON('data/cases.json').catch(e => { throw new Error(`cases.json: ${e.message}`); }),
      fetchWithCache('data/countries.json', CACHE_KEY_COUNTRIES, CACHE_VERSION_COUNTRIES),
      fetchWithCache('data/world-110m.json', CACHE_KEY_WORLD, CACHE_VERSION_WORLD)
    ]);

    // Normalize field names for JS compatibility
    normalizeCountriesData(countries);

    return { cases, countries, world };
  }

  /**
   * Convert ISO numeric code to alpha-2
   * @param {string|number} numeric
   * @returns {string|null}
   */
  function numericToAlpha2(numeric) {
    return ISO_NUMERIC_MAP[Number(numeric)] || null;
  }

  /**
   * Resolve map alias — territories to parent country for map display
   * e.g. 'HK' → 'CN' (Hong Kong shows on China geometry)
   * @param {string} alpha2
   * @returns {string} alpha2 or aliased parent
   */
  function resolveMapAlias(alpha2) {
    return MAP_ALIASES[alpha2] || alpha2;
  }

  /**
   * Get all codes that map to the same map geometry (reverse alias)
   * e.g. 'CN' → ['CN', 'HK', 'MO'] (China + territories)
   * @param {string} alpha2
   * @returns {string[]}
   */
  function getMapGroup(alpha2) {
    const group = [alpha2];
    for (const [alias, parent] of Object.entries(MAP_ALIASES)) {
      if (parent === alpha2 && alias !== alpha2) {
        group.push(alias);
      }
    }
    return group;
  }

  /**
   * Get alpha-2 → country name mapping from countries.json
   * @param {Object} countriesData
   * @returns {Object}
   */
  function getCountryNameMap(countriesData) {
    const map = {};
    if (countriesData && countriesData.countries) {
      for (const [code, info] of Object.entries(countriesData.countries)) {
        map[code] = info.name || info.countryName || code;
      }
    }
    return map;
  }

  return {
    loadAll,
    numericToAlpha2,
    resolveMapAlias,
    getMapGroup,
    getCountryNameMap
  };
})();
