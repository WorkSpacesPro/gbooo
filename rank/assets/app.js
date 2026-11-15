// ======= 1. 初始化主题 =======
(function(){
  var t = localStorage.getItem("theme");
  if(t === "dark" || t === "light") { document.documentElement.setAttribute("data-theme", t); }
  else { document.documentElement.setAttribute("data-theme", window.matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light"); }
})();

// ======= 2. 多语言字典 =======
const I18N = {
  zh: {
    pageTitle: "GitHub 开源排行榜", searchPlaceholder: "搜索项目名、语言或简介...",
    thProject: "项目", thGrowth: "涨星", thLang: "语言", thDesc: "简介",
    navTitle: "开源排行榜", navCategory: "目录导航",
    footerText: "© 2026 GitHub 开源排行榜 | 数据来源于 GitHub Actions 自动抓取",
    loading: "正在获取数据...", noData: "没有找到匹配的数据",
    catCount: (n) => `共 ${n} 个分类 | 点击标签秒级加载`,
    allCats: "全部分类", allCatsTitle: "全部分类",
    groupHot: "综合热榜", groupAI: "AI 前沿", groupCF: "Cloudflare 生态", groupLang: "编程语言", groupDev: "开发者场景",
    dateRange: "数据范围"
  },
  en: {
    pageTitle: "GitHub Open Source Rankings", searchPlaceholder: "Search projects...",
    thProject: "Project", thGrowth: "Growth", thLang: "Language", thDesc: "Description",
    navTitle: "Open Source Rank", navCategory: "Navigation",
    footerText: "© 2026 GitHub Rankings | Data by GitHub Actions",
    loading: "Fetching data...", noData: "No matching data",
    catCount: (n) => `${n} categories | Click tabs to load instantly`,
    allCats: "All Categories", allCatsTitle: "All Categories",
    groupHot: "Hot & Trending", groupAI: "AI Frontier", groupCF: "Cloudflare Eco", groupLang: "Languages", groupDev: "Dev Scenarios",
    dateRange: "Date Range"
  }
};

// ======= 3. 核心配置 =======
const CATEGORY_GROUPS = {
  hot: { color: "red", icon: "🔥", files: ["top", "rising", "forks", "weekly_top", "monthly_top", "yearly_top"] }, // 时间榜单也放这里
  ai: { color: "purple", icon: "🤖", files: ["agent", "local_llm", "aigc"] },
  cf: { color: "orange", icon: "☁️", files: ["cf_image", "cf_blog", "cf_shorturl", "cf_tools", "cf_workers", "cf_proxy"] },
  lang: { color: "blue", icon: "💻", files: ["python", "javascript", "typescript", "rust", "go", "java", "frontend"] },
  dev: { color: "green", icon: "🛠️", files: ["self_hosted", "dev_tools", "awesome", "saas"] }
};

// 顶部只保留最核心的标签（把时间榜单也加进去）
const DEFAULT_TABS = ["top", "weekly_top", "monthly_top"];

let currentLang = localStorage.getItem('lang') || 'zh';
let currentCategory = ""; 
let currentData = [];     
let filteredData = [];    
let sortKey = "stars";    
let sortOrder = "desc";   
let categoriesData = []; 

function getSafeFilename(catName) { return catName.replace(/ /g, "_").replace(/\//g, "_").replace(/\+/g, ""); }

// 获取几天前的日期字符串 (YYYY-MM-DD)
function getDateString(daysAgo) {
  const d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return d.toISOString().split('T')[0];
}

// ======= 4. 公共组件渲染 =======
async function renderLayout() {
  const path = window.location.pathname;
  const dict = I18N[currentLang];
  
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = dict[el.dataset.i18n]; });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => { el.placeholder = dict[el.dataset.i18nPlaceholder]; });
  if (!currentCategory) document.title = dict.pageTitle;

  document.getElementById('app-header').innerHTML = `
    <button class='nav-toggle' type='button'>
      <svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M4 12h16'/><path d='M4 6h16'/><path d='M4 18h16'/></svg>
    </button>
    <div class='nav-backdrop'></div>
    <div class="header-actions">
      <button id="lang-toggle" class="action-btn">${currentLang === 'zh' ? 'EN' : '中'}</button>
      <button class="theme-toggle action-btn" type="button">
        <svg class="icon-sun" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        <svg class="icon-moon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
      </button>
    </div>
    <button class="back-to-top" id="back-to-top">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>
    </button>
  `;

  document.getElementById('app-footer').innerHTML = `
    <footer class="footer">
      <p>${dict.footerText}</p>
      <p>Powered by <a href="https://github.com" target="_blank">GitHub</a> & <a href="https://pages.cloudflare.com" target="_blank">Cloudflare Pages</a></p>
    </footer>
  `;

  try {
    const res = await fetch('data/nav.json?t=' + Date.now());
    const navItems = await res.json();
    let navHtml = '';
    navItems.forEach(item => {
      if (item.link === 'divider') {
        navHtml += `<hr style="border:none; border-top:1px solid var(--border); margin:10px 0;">`;
        return;
      }
      const isActive = path.includes(item.link) || (
