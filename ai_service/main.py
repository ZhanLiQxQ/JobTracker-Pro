import time
import random
import os
import requests
from playwright.sync_api import sync_playwright

# --- Configuration ---
TARGET_URL = "https://weworkremotely.com/remote-jobs/search?sort=Any+Time"

# User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# API Keys and URLs
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "internal_secret_key_change_this_to_random_string")
DEFAULT_BACKEND_URL = "http://localhost:8080/api/internal/jobs/batch-intake"
BACKEND_INTAKE_URL = os.environ.get("JAVA_BACKEND_INTAKE_URL", DEFAULT_BACKEND_URL)
AI_SERVICE_URL = "http://localhost:5001/rag/ingest_jobs"


def save_jobs_batch_to_backend(jobs_data):
    """Batch call Spring Boot backend internal API to save job data using internal API key"""
    if not jobs_data:
        print("No job data to save")
        return []

    try:
        headers = {
            'Content-Type': 'application/json',
            'X-Internal-API-Key': INTERNAL_API_KEY
        }
        print(f"📡 Sending {len(jobs_data)} jobs to Java Backend...")
        response = requests.post(BACKEND_INTAKE_URL, json=jobs_data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            # --- 修复 1: 先获取 json 结果 ---
            result = response.json()

            # 你的 Java 代码返回的是 Map.of("jobs", savedJobs, ...)
            if isinstance(result, dict) and 'jobs' in result:
                saved_jobs = result['jobs']
            elif isinstance(result, list):
                saved_jobs = result
            else:
                print(f"⚠️ Unexpected response format from Java: {result.keys() if isinstance(result, dict) else result}")
                return []

            print(f"✅ Java Backend saved successfully. Received {len(saved_jobs)} IDs.")
            return saved_jobs
        else:
            print(f"❌ Java Batch save failed: {response.status_code}, {response.text}")
            return []

    except Exception as e:
        print(f"❌ Error sending to Java Backend: {e}")
        return []

def sync_jobs_to_vector_db(saved_jobs_from_java):
    """Sync jobs to Python Vector DB (Missing in your snippet, added back)"""
    if not saved_jobs_from_java:
        return

    print(f"🔄 Syncing {len(saved_jobs_from_java)} jobs to Vector DB...")

    vector_payload = {"jobs": []}
    for job in saved_jobs_from_java:
        if 'id' not in job: continue
        vector_payload["jobs"].append({
            "id": job['id'],
            "title": job['title'],
            "description": job['description'],
            "url": job.get('url', ''),
            "source": job.get('source', 'Crawler')
        })

    try:
        response = requests.post(AI_SERVICE_URL, json=vector_payload)
        if response.status_code == 200:
            print(f"✅ Vector DB sync successful!")
        else:
            print(f"❌ Vector DB sync failed: {response.text}")
    except Exception as e:
        print(f"❌ Error syncing to Vector DB: {e}")

import feedparser
import time
from bs4 import BeautifulSoup # 用来清理 description 里的 HTML 标签

RSS_URL = "https://weworkremotely.com/remote-jobs.rss"

def scrape_jobs():
    print("🚀 Starting RSS Scraper (Smart Mode)...")
    all_jobs_data = []

    # 1. 直接请求 RSS XML 数据
    feed = feedparser.parse(RSS_URL)
    print(f"✅ Found {len(feed.entries)} jobs in RSS feed.")

    # 2. 遍历数据
    for entry in feed.entries[:20]: # 演示用，取前20个
        try:
            print(f"Parsing: {entry.title}")

            # 清洗 Description (RSS 里的 description 通常带有 HTML)
            raw_desc = entry.get('summary', '') or entry.get('description', '')
            clean_desc = BeautifulSoup(raw_desc, "html.parser").get_text(separator="\n").strip()

            job_data = {
                "title": entry.title,
                "company": entry.get('author', 'Unknown Company'), # RSS 里 author 字段通常是公司名
                "location": "Remote", # WWR 主要是 Remote，RSS 可能不含具体 location，可设为默认
                "description": clean_desc,
                "url": entry.link,
                "source": "We Work Remotely (RSS)"
            }
            all_jobs_data.append(job_data)

        except Exception as e:
            print(f"Error parsing entry: {e}")

    # 3. 批量保存
    if all_jobs_data:
        print(f"\n📦 Batch saving {len(all_jobs_data)} jobs to backend...")
        save_jobs_batch_to_backend(all_jobs_data)
    else:
        print("No jobs found.")

# def scrape_jobs():
#     """Main scraper function"""
#     print(f"Java URL: {BACKEND_INTAKE_URL}")
#     print("Starting scraper task...")
#     all_jobs_data = []
#
#     with sync_playwright() as p:
#         # --- 修复 2: 改为 headless=False (有头模式) ---
#         # 在本地运行时，这是绕过 Cloudflare 最稳妥的方法
#         browser = p.chromium.launch(
#             headless=True,
#             # headless=False,  # <--- 关键修改：弹出浏览器窗口
#             args=[
#                 "--disable-blink-features=AutomationControlled",
#                 "--no-sandbox",
#             ]
#         )
#
#         user_agent = random.choice(USER_AGENTS)
#         context = browser.new_context(
#             user_agent=user_agent,
#             viewport={'width': 1280, 'height': 800} # 设置一个常见的窗口大小
#         )
#
#         context.add_init_script("""
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined
#             });
#         """)
#
#         page = context.new_page()
#
#         try:
#             print(f"Visiting list page: {TARGET_URL}")
#             # 有头模式下，Cloudflare 验证通常会自动通过
#             page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
#             time.sleep(random.uniform(3, 5))
#
#             job_listings = page.query_selector_all(".new-listing-container")
#             print(f"Found {len(job_listings)} jobs on this page.")
#
#             # 为了调试，只爬前 3 个，避免刷太快被封 IP
#             # job_listings = job_listings[:3]
#
#             base_url = "https://weworkremotely.com"
#
#             for i, listing in enumerate(job_listings[:20], 1):
#                 try:
#                     print(f"--- Parsing job {i} ---")
#
#                     title_el = listing.query_selector(".new-listing__header__title")
#                     title = title_el.inner_text() if title_el else "N/A"
#
#                     company_el = listing.query_selector(".new-listing__company-name")
#                     company = company_el.inner_text() if company_el else "N/A"
#
#                     location_el = listing.query_selector(".new-listing__company-headquarters")
#                     location = location_el.inner_text() if location_el else "N/A"
#
#                     link_el = listing.query_selector('a[href*="/remote-jobs/"]')
#                     job_url_path = link_el.get_attribute("href") if link_el else None
#
#                     if not job_url_path:
#                         print(f"Warning: Job {i} no link, skipping.")
#                         continue
#
#                     job_detail_url = base_url + job_url_path
#                     print(f"Visiting: {job_detail_url}")
#
#                     detail_page = context.new_page()
#
#                     # 加载详情页
#                     detail_page.goto(job_detail_url, wait_until="domcontentloaded", timeout=60000)
#
#                     # 智能等待：如果有 Cloudflare，有头模式下通常会自动跳转
#                     # 我们只需要检查最终的元素是否出现
#                     possible_selectors = [
#                         ".lis-container__job__content__description",
#                         "#job-listing-show-container",
#                         ".listing-container",
#                         "div.content"
#                     ]
#
#                     full_description = ""
#                     for selector in possible_selectors:
#                         try:
#                             # 增加等待时间到 5 秒
#                             element = detail_page.wait_for_selector(selector, timeout=5000, state="attached")
#                             if element:
#                                 full_description = element.inner_text().strip()
#                                 if full_description:
#                                     break
#                         except:
#                             continue
#
#                     if not full_description:
#                         # 如果还是拿不到，说明可能是需要登录或者被强制拦截了
#                         print(f"Warning: Empty description. Title: {detail_page.title()}")
#
#                     detail_page.close()
#
#                     if full_description:
#                         job_data = {
#                             "title": title.strip(),
#                             "company": company.strip(),
#                             "location": location.strip(),
#                             "description": full_description,
#                             "url": job_detail_url,
#                             "source": "We Work Remotely"
#                         }
#                         all_jobs_data.append(job_data)
#                     else:
#                         print(f"Skipping job {i} due to empty description.")
#
#                     # 模拟人类阅读时间
#                     time.sleep(random.uniform(2, 4))
#
#                 except Exception as e:
#                     print(f"Error parsing job {i}: {e}")
#                     # 确保出错时关闭页面
#                     if 'detail_page' in locals():
#                         try: detail_page.close()
#                         except: pass
#
#         except Exception as e:
#             print(f"Serious error: {e}")
#         finally:
#             browser.close()
#
#     # --- Batch save ---
#     if all_jobs_data:
#         print(f"\nStarting batch save of {len(all_jobs_data)} jobs...")
#         saved_jobs_with_ids = save_jobs_batch_to_backend(all_jobs_data)
#
#         if saved_jobs_with_ids:
#             sync_jobs_to_vector_db(saved_jobs_with_ids)
#     else:
#         print("\nNo job data was scraped")
#
#     print("\nScraper task completed.")

if __name__ == "__main__":
    scrape_jobs()