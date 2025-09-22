# # scraper/scraper.py
#
import time
import random
import os
import requests
from playwright.sync_api import sync_playwright
# --- Configuration ---
# TARGET_URL = "https://weworkremotely.com/remote-software-developer-jobs"
TARGET_URL = "https://weworkremotely.com/remote-jobs/search?sort=Any+Time"

# Your Spring Boot backend API address
# API_ENDPOINT = "http://localhost:8080/api/jobs"
# Simulate different browser User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    # ... you can add more
]

# ai_service/scraper.py
import requests

# --- Configuration Area ---
BACKEND_INTAKE_URL = os.environ.get("JAVA_BACKEND_INTAKE_URL", "http://localhost:8080/api/internal/jobs/batch-intake")

INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "thisisaramdomandVeryLongStringtoMakeItASecretKey155423asc5assajci,w,YAJCB")


def save_jobs_batch_to_backend(jobs_data):
    """Batch call Spring Boot backend internal API to save job data using internal API key"""
    if not jobs_data:
        print("No job data to save")
        return
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-Internal-API-Key': INTERNAL_API_KEY  # Use internal API key
        }
        response = requests.post(BACKEND_INTAKE_URL, json=jobs_data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"Successfully batch saved {result.get('count', len(jobs_data))} jobs")
        else:
            print(f"Batch save failed, status code: {response.status_code}, response: {response.text}")
    except Exception as e:
        print(f"Error occurred when calling batch save API: {e}")



def scrape_jobs():
    """Main scraper function"""

    print(BACKEND_INTAKE_URL)
    print("Starting scraper task...")

    # Create a list to store all scraped job information
    all_jobs_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        user_agent = random.choice(USER_AGENTS)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            print(f"Page opened: {page.title()}")
            time.sleep(random.uniform(3, 7))

            job_listings = page.query_selector_all(".new-listing-container")
            print(f"Found {len(job_listings)} jobs on this page.")

            base_url = "https://weworkremotely.com"

            for i, listing in enumerate(job_listings, 1):  # Use enumerate to track which job number
                try:
                    print(f"--- Parsing job {i} ---")  # Debug info, convenient for problem location

                    # --- Extract information (added safety checks) ---

                    # Find title element
                    title_element = listing.query_selector(".new-listing__header__title")
                    # Check if found, if found extract text, otherwise set to "N/A"
                    title = title_element.inner_text() if title_element else "N/A"

                    # Find company element
                    company_element = listing.query_selector(".new-listing__company-name")
                    company = company_element.inner_text() if company_element else "N/A"

                    # Find location element
                    location_element = listing.query_selector(".new-listing__company-headquarters")
                    location = location_element.inner_text() if location_element else "N/A"

                    # Find job link element
                    link_element = listing.query_selector('a[href*="/remote-jobs/"]')
                    job_url_path = link_element.get_attribute("href") if link_element else None

                    # If even the most important link cannot be found, skip this entry
                    if not job_url_path:
                        print(f"Warning: Job {i} could not find key link, skipping.")
                        continue

                    # --- Core modification: visit detail page to get complete description ---
                    job_detail_url = base_url + job_url_path
                    print(f"Visiting detail page: {job_detail_url}")

                    # Open a new tab in the same browser context
                    detail_page = context.new_page()
                    detail_page.goto(job_detail_url, wait_until="domcontentloaded")

                    # Use the detail page selector you found to extract description
                    description_element = detail_page.query_selector(".lis-container__job__content__description")

                    full_description = ""
                    if description_element:
                        full_description = description_element.inner_text()
                    else:
                        print(f"Warning: Could not find description section on detail page.")

                    # After completing the task, close this detail page tab to release resources
                    detail_page.close()
                    # -------------------------------------------
                    job_data = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": location.strip(),
                        "description": full_description.strip(),  # Use our newly obtained complete description
                        "url": job_detail_url,
                        "source": "We Work Remotely"
                    }

                    # Store data in list (no longer save individually)
                    all_jobs_data.append(job_data)

                    # Random delay
                    time.sleep(random.uniform(2, 5))  # Access secondary pages, can appropriately increase delay

                except Exception as e:
                    print(f"Error parsing individual job: {e}")
                    if 'detail_page' in locals() and not detail_page.is_closed():
                        detail_page.close()  # If error occurs, also ensure tab is closed

                except Exception as e:
                    # This except will now only catch unexpected serious errors
                    print(f"Unknown error occurred when parsing job {i}: {e}")


        # When encountering an error with one piece of information, the try error is caught and the except block is executed immediately, then enters the next loop. It will not crash entirely.
        except Exception as e:
            print(f"Serious error occurred during scraping: {e}")
        finally:
            browser.close()

    # --- Batch save all job data ---
    if all_jobs_data:
        print(f"\nStarting batch save of {len(all_jobs_data)} jobs...")
        save_jobs_batch_to_backend(all_jobs_data)
    else:
        print("\nNo job data was scraped")

    # --- After all scraping is complete, print results uniformly ---
    print("\n" + "=" * 50)
    print("Scraper debug output results:")
    print(f"Total scraped {len(all_jobs_data)} jobs.")
    print("=" * 50)

    # Print information for each job one by one
    for i, job in enumerate(all_jobs_data, 1):
        print(f"\n--- Job {i} ---")
        print(f"  Title: {job['title']}")
        print(f"  Company: {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  Description: {job['description'][:100]}..." if job['description'] else "  Description: None")
        print(f"  Link: {job['url']}")

    print("\nScraper task completed.")


# --- For convenience of directly running this file for debugging ---
if __name__ == "__main__":
    # Run main function
    scrape_jobs()














#
#
# def scrape_jobs():
#     """Main scraper function"""
#     print("Starting scraper task...")
#
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)  # headless=False 会打开浏览器界面，方便调试，这是一个非常重要的参数，headless 的意思是**“无头模式”**。
#
# # True (默认): 浏览器会在后台静默运行，你看不到任何浏览器窗口。这在服务器上运行爬虫时是必须的，因为它效率高、不占用图形界面资源。
# #
# # False: 程序会弹出一个真实的、可见的浏览器窗口，并且你会看到你的代码正在一步步地自动化操作它。这在你编写和调试爬虫代码时非常有用，可以直观地看到哪里出了问题。
#
#         # 随机选择一个 User-Agent
#         user_agent = random.choice(USER_AGENTS)
#         context = browser.new_context(user_agent=user_agent)
#         page = context.new_page()
#
#         try:
#             page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
#             print(f"Page opened: {page.title()}")
#
#             # --- 反爬虫策略 1: 随机延迟 ---
#             time.sleep(random.uniform(3, 7))
#
#             # --- 定位职位列表 ---
#             job_listings = page.query_selector_all(".new-listing-container")
#             print(f"Found {len(job_listings)} jobs on this page.")
#
#             base_url = "https://weworkremotely.com"
#
#             for listing in job_listings:
#                 try:
#                     # --- 提取信息 ---
#                     title = listing.query_selector(".new-listing__header__title").inner_text()
#                     company = listing.query_selector(".new-listing__company-name").inner_text()
#                     location = listing.query_selector(".new-listing__company-headquarters").inner_text()
#
#                     # Find job link element
#                     link_element = listing.query_selector('a[href*="/remote-jobs/"]')
#                     job_url_path = link_element.get_attribute("href") if link_element else None
#
#                     if not job_url_path:
#                         print("警告: 未能找到职位链接，跳过此条目。")
#                         continue
#
#                     job_data = {
#                         "title": title.strip(),
#                         "company": company.strip(),
#                         "location": location.strip(),
#                         "description": "",  # 列表页没有详细描述，可以留空或后续进入详情页抓取
#                         "url": base_url + job_url_path
#                     }
#
#                     save_job_to_backend(job_data)
#                     time.sleep(random.uniform(1, 4))
#
#                 except Exception as e:
#                     print(f"Error parsing individual job: {e}")
#
#             # 此处可以添加翻页逻辑
#
#         except Exception as e:
#             print(f"Serious error occurred during scraping: {e}")
#         finally:
#             browser.close()
#
#     print("爬虫任务执行完毕。")
#
#
# # 测试运行
# if __name__ == "__main__":
#     scrape_jobs()


# ... (import 和常量定义部分保持不变)
