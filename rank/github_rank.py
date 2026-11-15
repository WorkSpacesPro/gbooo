#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests

API = "https://api.github.com"
SESSION = requests.Session()
SESSION.headers.update({
    "Accept": "application/vnd.github+json",
    "User-Agent": "github-star-rank"
})
if os.getenv("GITHUB_TOKEN"):
    SESSION.headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"

def get_base_categories():
    last_year = datetime.now().year - 1
    return {
        "总榜 Top": {"query": "stars:>50000", "limit": 50, "file": "top", "en": "Top Overall"},
        f"明日之星(>{last_year})": {"query": f"created:>{last_year}-01-01 stars:>2000", "limit": 30, "file": "rising", "en": "Rising Stars"},
        "Fork 最多": {"query": "stars:>10000 forks:>5000", "limit": 30, "file": "forks", "en": "Most Forked"},
        "AI 智能体": {"query": "topic:ai-agent stars:>1000", "limit": 30, "file": "agent", "en": "AI Agent"},
        "本地大模型": {"query": "topic:local-llm stars:>1000", "limit": 30, "file": "local_llm", "en": "Local LLM"},
        "AIGC": {"query": "topic:stable-diffusion stars:>3000", "limit": 30, "file": "aigc", "en": "AIGC Tools"},
        "自托管/隐私": {"query": "topic:self-hosted stars:>10000", "limit": 30, "file": "self_hosted", "en": "Self-Hosted"},
        "开发者工具": {"query": "topic:cli-tool stars:>5000", "limit": 30, "file": "dev_tools", "en": "Dev Tools"},
        "Awesome/学习": {"query": "topic:awesome stars:>30000", "limit": 30, "file": "awesome", "en": "Awesome Lists"},
        "独立开发/SaaS": {"query": "topic:saas-boilerplate stars:>2000", "limit": 30, "file": "saas", "en": "SaaS Boilerplate"},
        "CF 图床/相册": {"query": "cloudflare image stars:>100", "limit": 30, "file": "cf_image", "en": "CF Image Host"},
        "CF 博客建站": {"query": "cloudflare blog stars:>100", "limit": 30, "file": "cf_blog", "en": "CF Blog Builders"},
        "CF 短链接": {"query": "cloudflare short url stars:>50", "limit": 30, "file": "cf_shorturl", "en": "CF URL Shortener"},
        "CF 建站周边": {"query": "cloudflare waline OR cloudflare analytics stars:>50", "limit": 30, "file": "cf_tools", "en": "CF Site Tools"},
        "CF 全能工具": {"query": "topic:cloudflare-workers stars:>1000", "limit": 30, "file": "cf_workers", "en": "CF Workers"},
        "CF 网络/代理": {"query": "cloudflare vless OR cloudflare trojan stars:>500", "limit": 30, "file": "cf_proxy", "en": "CF Proxy Tools"},
        "Python": {"query": "language:Python stars:>20000", "limit": 30, "file": "python", "en": "Python"},
        "JavaScript": {"query": "language:JavaScript stars:>20000", "limit": 30, "file": "javascript", "en": "JavaScript"},
        "TypeScript": {"query": "language:TypeScript stars:>15000", "limit": 30, "file": "typescript", "en": "TypeScript"},
        "Rust": {"query": "language:Rust stars:>10000", "limit": 30, "file": "rust", "en": "Rust"},
        "Go": {"query": "language:Go stars:>10000", "limit": 30, "file": "go", "en": "Go"},
        "Java": {"query": "language:Java stars:>15000", "limit": 30, "file": "java", "en": "Java"},
        "前端": {"query": "topic:frontend stars:>10000", "limit": 30, "file": "frontend", "en": "Frontend"},
    }

def sleep_for_rate_limit(resp):
    if int(resp.headers.get("X-RateLimit-Remaining", "1")) > 0: return
    reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
    wait = max(1, reset - int(time.time()) + 1)
    print(f"[rate-limit] 等待 {wait}s", file=sys.stderr)
    time.sleep(wait)

def api_get(url, params=None, retries=4):
    last_err = None
    for i in range(retries):
        try:
            resp = SESSION.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                sleep_for_rate_limit(resp)
                return resp.json()
            if resp.status_code in (403, 429):
                sleep_for_rate_limit(resp)
                time.sleep(2 ** i)
                continue
            if resp.status_code == 422:
                raise ValueError(f"查询语法错误: {resp.text[:300]}")
            resp.raise_for_status()
        except requests.RequestException as e:
            last_err = e
            time.sleep(2 ** i)
    raise RuntimeError(f"请求失败: {url} ({last_err})")

def search_repos(query, limit):
    out, page = [], 1
    while len(out) < limit and page <= 10:
        per_page = min(100, limit - len(out))
        data = api_get(f"{API}/search/repositories", {
            "q": query, "sort": "stars", "order": "desc", "per_page": per_page, "page": page
        })
        items = data.get("items") or []
        out.extend(items)
        if len(items) < per_page: break
        page += 1
    return out[:limit]

def slim(item):
    desc = (item.get("description") or "").replace("\n", " ").replace("|", "\\|")
    return {
        "full_name": item["full_name"], "html_url": item["html_url"], "description": desc.strip(),
        "stars": item["stargazers_count"], "forks": item["forks_count"], "language": item.get("language") or "-",
    }

def manage_history_and_growth(today_stars, today_str):
    history_dir = Path("data/history")
    history_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 保存今天的极简账本
    today_file = history_dir / f"{today_str}.json"
    today_file.write_text(json.dumps(today_stars, ensure_ascii=False), encoding="utf-8")
    
    # 2. 自动清理超过 365 天的老账本
    one_year_ago = datetime.now() - timedelta(days=365)
    for f in history_dir.glob("*.json"):
        try:
            file_date = datetime.strptime(f.stem, "%Y-%m-%d")
            if file_date < one_year_ago:
                f.unlink()
                print(f"🗑️ 已清理过期账本: {f.stem}.json", file=sys.stderr)
        except ValueError:
            pass

    # 3. 计算不同时间维度的涨星
    intervals = {"weekly": 7, "monthly": 30, "yearly": 365}
    growth_results = {}
    date_ranges = {}
    
    for period, days in intervals.items():
        target_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        target_file = history_dir / f"{target_date}.json"
        
        if target_file.exists():
            old_stars = json.loads(target_file.read_text(encoding="utf-8"))
            growth_dict = {}
            for repo, stars in today_stars.items():
                if repo in old_stars:
                    diff = stars - old_stars[repo]
                    if diff > 0:
                        growth_dict[repo] = diff
            growth_results[period] = growth_dict
            date_ranges[period] = f"{target_date} — {today_str}"
            print(f"✅ 成功计算 [{period}] 涨幅数据", file=sys.stderr)
        else:
            growth_results[period] = {}
            date_ranges[period] = ""
            print(f"⚠️ 缺少 {target_date} 的账本，跳过 [{period}] 计算", file=sys.stderr)

    return growth_results, date_ranges

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sort", default="stars", choices=["stars", "forks"])
    args = ap.parse_args()

    base_categories = get_base_categories()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    all_data = {}
    today_stars_snapshot = {}

    # 1. 抓取常规分类数据
    for cat, cfg in base_categories.items():
        print(f"抓取 [{cat}] ...", file=sys.stderr)
        rows = []
        for raw in search_repos(cfg["query"], cfg.get("limit", 30)):
            r = slim(raw)
            rows.append(r)
            today_stars_snapshot[r["full_name"]] = r["stars"]
        all_data[cat] = sorted(rows, key=lambda r: r["stars"], reverse=True)

    # 2. 自动生成账本并计算时间维度
    growth_data, date_ranges = manage_history_and_growth(today_stars_snapshot, today_str)
    
    all_repos_info = {}
    for cat_rows in all_data.values():
        for r in cat_rows:
            all_repos_info[r["full_name"]] = r

    time_categories = {
        "weekly": {"zh": "📈 本周黑马", "en": "📈 This Week", "file": "weekly_top"},
        "monthly": {"zh": "🏆 本月霸主", "en": "🏆 This Month", "file": "monthly_top"},
        "yearly": {"zh": "👑 年度神作", "en": "👑 This Year", "file": "yearly_top"},
    }
    
    final_categories_list = []
    
    # 处理时间榜单（插入到最前面）
    for period, cat_info in time_categories.items():
        if growth_data.get(period):
            sorted_growth = sorted(growth_data[period].items(), key=lambda x: x[1], reverse=True)[:50]
            rows = []
            for repo, diff in sorted_growth:
                if repo in all_repos_info:
                    row = all_repos_info[repo].copy()
                    row["growth"] = diff
                    rows.append(row)
            if rows:
                all_data[cat_info["zh"]] = rows
                # 把时间段信息也写进 json 方便前端读取（可选，这里前端自己算更简单）
                final_categories_list.append(cat_info)

    # 再放基础分类
    for cat, cfg in base_categories.items():
        final_categories_list.append({"zh": cat, "en": cfg["en"], "file": cfg["file"]})

    # 3. 输出拆分 JSON
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    (data_dir / "categories.json").write_text(json.dumps(final_categories_list, ensure_ascii=False), encoding="utf-8")

    for cat, items in all_data.items():
        file_name = None
        for fc in final_categories_list:
            if fc["zh"] == cat:
                file_name = fc["file"]
                break
        if file_name:
            (data_dir / f"{file_name}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
            
    print(f"✅ 数据生成完毕，前端文件已就绪", file=sys.stderr)

if __name__ == "__main__":
    main()
