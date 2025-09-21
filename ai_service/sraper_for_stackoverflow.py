# # scraper/scraper.py
#
import time
import random
import requests
from playwright.sync_api import sync_playwright
import requests
import os  # 导入 os 库来读取环境变量
from dotenv import load_dotenv
# --- 配置 ---
# TARGET_URL = "https://weworkremotely.com/remote-software-developer-jobs"
# TARGET_URL = "https://weworkremotely.com/remote-jobs/search?sort=Any+Time"

TARGET_URL = "https://stackoverflow.com/jobs/companies?tl=java"
# 你的 Spring Boot 后端的 API 地址
API_ENDPOINT = "http://localhost:8080/api/jobs"
# 模拟不同浏览器的 User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    # ... 你可以添加更多
]

load_dotenv()
SCRAPER_USERNAME = os.getenv("SCRAPER_USER", "default_user")
SCRAPER_PASSWORD = os.getenv("SCRAPER_PASSWORD", "default_pass")

LOGIN_API_ENDPOINT = "http://localhost:8080/api/auth/signin"
API_ENDPOINT = "http://localhost:8080/api/jobs"


def get_auth_token():
    """登录并获取 JWT Token"""
    print("正在尝试登录以获取认证 Token...")
    try:
        login_payload = {
            "email": SCRAPER_USERNAME,
            "password": SCRAPER_PASSWORD
        }
        print(f"使用的用户名: {SCRAPER_USERNAME}")
        print(f"使用的密码: {SCRAPER_PASSWORD}")
        response = requests.post(LOGIN_API_ENDPOINT, json=login_payload)

        if response.status_code == 200:
            token = response.json().get("token")
            if token:
                print("登录成功，已获取 Token！")
                return token
            else:
                print("登录成功，但响应中未找到 Token。")
                return None
        else:
            print(f"登录失败！状态码: {response.status_code}, 响应: {response.text}")
            return None
    except Exception as e:
        print(f"调用登录 API 时发生错误: {e}")
        return None


def save_job_to_backend(job_data, token):
    """调用 Spring Boot 后端 API 保存职位数据 (现在需要传入 token)"""
    if not token:
        print(f"没有有效的 Token，无法保存职位: {job_data['title']}")
        return

    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(API_ENDPOINT, json=job_data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            print(f"成功保存职位: {job_data['title']}")
        else:
            print(f"保存失败: {job_data['title']}, 状态码: {response.status_code}, 响应: {response.text}")
    except Exception as e:
        print(f"调用 API 时发生错误: {e}")


def scrape_jobs():
    """主爬虫函数"""

    print("开始执行爬虫任务...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        user_agent = random.choice(USER_AGENTS)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            print(f"已打开页面: {page.title()}")
            time.sleep(random.uniform(3, 7))
            # debug
            job_listings = page.query_selector_all(".dismissable-company")
            print(f"在本页找到 {len(job_listings)} 个职位。")

            for i, listing in enumerate(job_listings, 1):  # 使用 enumerate 来跟踪是第几个职位
                # 假设 listing 是 for 循环中的一个 .dismissable-company 元素

                try:
                    company_element = listing.query_selector("h2 > a.s-link")
                    company = company_element.inner_text().strip()
                    url_path = company_element.get_attribute("href")
                    url = "https://stackoverflow.com" + url_path if url_path else "N/A"

                    location_element = listing.query_selector("div:has(svg.iconLocation)")
                    location = location_element.text_content().strip() if location_element else "N/A"

                    description_element = listing.query_selector("p.v-truncate2")
                    description = description_element.inner_text().strip() if description_element else "N/A"

                    tag_elements = listing.query_selector_all("a.s-tag")
                    tags = [tag.inner_text() for tag in tag_elements]

                    job_data = {
                        "company": company,
                        "url": url,
                        "location": location,
                        "description": description,
                        "tags": tags  # 还可以把标签列表也存起来
                    }

                    print(job_data)  # 调试输出

                except Exception as e:
                    print(f"解析时出错: {e}")


        # 当遇到一条信息的错误时，try错误被接住并立即执行except块，并进入下一次循环。而并不会整个崩溃。
        except Exception as e:
            print(f"爬取过程中发生严重错误: {e}")
        finally:
            browser.close()


# --- 为了方便直接运行此文件进行调试 ---
if __name__ == "__main__":
    # 运行主函数
    scrape_jobs()

