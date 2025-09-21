# # scraper/scraper.py
#
import time
import random
import os
import requests
from playwright.sync_api import sync_playwright
# --- 配置 ---
# TARGET_URL = "https://weworkremotely.com/remote-software-developer-jobs"
TARGET_URL = "https://weworkremotely.com/remote-jobs/search?sort=Any+Time"

# 你的 Spring Boot 后端的 API 地址
# API_ENDPOINT = "http://localhost:8080/api/jobs"
# 模拟不同浏览器的 User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    # ... 你可以添加更多
]

# ai_service/scraper.py
import requests

# --- 配置区 ---
# Java后端的内部API地址
# BACKEND_INTAKE_URL = "http://localhost:8080/api/internal/jobs/batch-intake"
BACKEND_INTAKE_URL = os.environ.get("JAVA_BACKEND_INTAKE_URL", "http://localhost:8080/api/internal/jobs/batch-intake")
# BACKEND_INTAKE_URL = "http://backend:8080/api/internal/jobs/batch-intake"
# 必须和Java application.yml中的完全一样
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "thisisaramdomandVeryLongStringtoMakeItASecretKey155423asc5assajci,w,YAJCB")


# def get_auth_token():
#     """登录并获取 JWT Token"""
#     print("正在尝试登录以获取认证 Token...")
#     try:
#         login_payload = {
#             "email": SCRAPER_USERNAME,
#             "password": SCRAPER_PASSWORD
#         }
#         print(f"使用的用户名: {SCRAPER_USERNAME}")
#         print(f"使用的密码: {SCRAPER_PASSWORD}")
#         response = requests.post(LOGIN_API_ENDPOINT, json=login_payload)
#
#         if response.status_code == 200:
#             token = response.json().get("token")
#             if token:
#                 print("登录成功，已获取 Token！")
#                 return token
#             else:
#                 print("登录成功，但响应中未找到 Token。")
#                 return None
#         else:
#             print(f"登录失败！状态码: {response.status_code}, 响应: {response.text}")
#             return None
#     except Exception as e:
#         print(f"调用登录 API 时发生错误: {e}")
#         return None


def save_jobs_batch_to_backend(jobs_data):
    """批量调用 Spring Boot 后端内部API保存职位数据 使用内部API密钥"""
    if not jobs_data:
        print("没有职位数据需要保存")
        return
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-Internal-API-Key': INTERNAL_API_KEY  # 使用内部API密钥
        }
        response = requests.post(BACKEND_INTAKE_URL, json=jobs_data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"成功批量保存 {result.get('count', len(jobs_data))} 个职位")
        else:
            print(f"批量保存失败, 状态码: {response.status_code}, 响应: {response.text}")
    except Exception as e:
        print(f"调用批量保存 API 时发生错误: {e}")



def scrape_jobs():
    """主爬虫函数"""

    print(BACKEND_INTAKE_URL)
    print("开始执行爬虫任务...")

    # 创建一个列表，用来存储所有抓取到的职位信息
    all_jobs_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        user_agent = random.choice(USER_AGENTS)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            print(f"已打开页面: {page.title()}")
            time.sleep(random.uniform(3, 7))

            job_listings = page.query_selector_all(".new-listing-container")
            print(f"在本页找到 {len(job_listings)} 个职位。")

            base_url = "https://weworkremotely.com"

            for i, listing in enumerate(job_listings[:2], 1):  # 使用 enumerate 来跟踪是第几个职位
                try:
                    print(f"--- 正在解析第 {i} 个职位 ---")  # 调试信息，方便定位问题

                    # --- 提取信息（添加了安全检查） ---

                    # 查找 title 元素
                    title_element = listing.query_selector(".new-listing__header__title")
                    # 检查是否找到，如果找到则提取文本，否则设为 "N/A"
                    title = title_element.inner_text() if title_element else "N/A"

                    # 查找 company 元素
                    company_element = listing.query_selector(".new-listing__company-name")
                    company = company_element.inner_text() if company_element else "N/A"

                    # 查找 location 元素
                    location_element = listing.query_selector(".new-listing__company-headquarters")
                    location = location_element.inner_text() if location_element else "N/A"

                    # 查找职位链接元素
                    link_element = listing.query_selector('a[href*="/remote-jobs/"]')
                    job_url_path = link_element.get_attribute("href") if link_element else None

                    # 如果连最重要的链接都找不到，就跳过这个条目
                    if not job_url_path:
                        print(f"警告: 第 {i} 个职位未能找到关键的链接，跳过。")
                        continue

                    # --- 核心修改：访问详情页以获取完整描述 ---
                    job_detail_url = base_url + job_url_path
                    print(f"正在访问详情页: {job_detail_url}")

                    # 在同一个浏览器上下文中打开一个新标签页
                    detail_page = context.new_page()
                    detail_page.goto(job_detail_url, wait_until="domcontentloaded")

                    # 使用您找到的详情页选择器来提取描述
                    description_element = detail_page.query_selector(".lis-container__job__content__description")

                    full_description = ""
                    if description_element:
                        full_description = description_element.inner_text()
                    else:
                        print(f"警告: 在详情页未能找到描述部分。")

                    # 完成任务后，关闭这个详情页标签，释放资源
                    detail_page.close()
                    # -------------------------------------------
                    job_data = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": location.strip(),
                        "description": full_description.strip(),  # 使用我们新获取的完整描述
                        "url": job_detail_url,
                        "source": "We Work Remotely"
                    }

                    # 将数据存入列表（不再逐个保存）
                    all_jobs_data.append(job_data)

                    # 随机延迟
                    time.sleep(random.uniform(2, 5))  # 访问二级页面，可以适当增加延迟

                except Exception as e:
                    print(f"解析单个职位时出错: {e}")
                    if 'detail_page' in locals() and not detail_page.is_closed():
                        detail_page.close()  # 如果出错，也确保关闭标签页

                except Exception as e:
                    # 这里的 except 现在只会捕获意料之外的严重错误
                    print(f"解析第 {i} 个职位时发生未知错误: {e}")


        # 当遇到一条信息的错误时，try错误被接住并立即执行except块，并进入下一次循环。而并不会整个崩溃。
        except Exception as e:
            print(f"爬取过程中发生严重错误: {e}")
        finally:
            browser.close()

    # --- 批量保存所有职位数据 ---
    if all_jobs_data:
        print(f"\n开始批量保存 {len(all_jobs_data)} 个职位...")
        save_jobs_batch_to_backend(all_jobs_data)
    else:
        print("\n没有爬取到任何职位数据")

    # --- 在所有爬取结束后，统一打印结果 ---
    print("\n" + "=" * 50)
    print("爬虫调试输出结果:")
    print(f"总共爬取到 {len(all_jobs_data)} 个职位。")
    print("=" * 50)

    # 逐条打印每个职位的信息
    for i, job in enumerate(all_jobs_data, 1):
        print(f"\n--- 职位 {i} ---")
        print(f"  标题: {job['title']}")
        print(f"  公司: {job['company']}")
        print(f"  地点: {job['location']}")
        print(f"  描述: {job['description'][:100]}..." if job['description'] else "  描述: 无")
        print(f"  链接: {job['url']}")

    print("\n爬虫任务执行完毕。")


# --- 为了方便直接运行此文件进行调试 ---
if __name__ == "__main__":
    # 运行主函数
    scrape_jobs()














#
#
# def scrape_jobs():
#     """主爬虫函数"""
#     print("开始执行爬虫任务...")
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
#             print(f"已打开页面: {page.title()}")
#
#             # --- 反爬虫策略 1: 随机延迟 ---
#             time.sleep(random.uniform(3, 7))
#
#             # --- 定位职位列表 ---
#             job_listings = page.query_selector_all(".new-listing-container")
#             print(f"在本页找到 {len(job_listings)} 个职位。")
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
#                     # 查找职位链接元素
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
#                     print(f"解析单个职位时出错: {e}")
#
#             # 此处可以添加翻页逻辑
#
#         except Exception as e:
#             print(f"爬取过程中发生严重错误: {e}")
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
