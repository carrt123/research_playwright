from playwright.sync_api import Playwright, sync_playwright, Page
import json


def scrape_movie_from_page(page: Page) -> [str]:
    nodes = page.query_selector_all('.el-card')
    movie_list = []
    for node in nodes:
        title = node.query_selector('.name').inner_text()
        # title = node.query_selector('.m-b-sm').text_content()
        categories = node.query_selector('.categories').inner_text()
        infos = node.query_selector_all('.m-v-sm')
        country, duration = infos[0].inner_text().split('/')
        release_date = infos[1].inner_text()
        score = node.query_selector('.score').inner_text()
        movie_list.append({
            "title": title,
            "categories": categories,
            "country": country,
            "duration": duration,
            "release_date": release_date,
            "score": score
        })
    return movie_list


def run(playwright: Playwright, max_pages=10) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        http_credentials={"username": "admin", "password": "admin"}
    )
    page = context.new_page()
    page.goto("https://ssr3.scrape.center/")
    all_movies = []
    current_page = 1
    while True:
        all_movies.extend(scrape_movie_from_page(page))
        next_button = page.query_selector('.btn-next')
        # if next_button.is_disabled():  # 如果没有下一页，则退出循环
        #     break
        current_page += 1
        if current_page > max_pages:
            break
        next_button.click()
    save_movies_into_json(all_movies, 'ssr3_movies.json')

    browser.close()


def save_movies_into_json(movies, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=4)


with sync_playwright() as playwright:
    run(playwright)

# ensure_ascii=False: 这个参数指定了在编码时是否确保输出是 ASCII 码。默认情况下，ensure_ascii 是 True，意味着所有非 ASCII 字符（例如中文、日文等）都会被转义。设置为 False
# 允许输出非 ASCII 字符，这样在 JSON 文件中可以直接显示这些字符，而不是它们的 Unicode 转义序列。
#
# indent=4: 这个参数指定了 JSON 字符串的缩进级别，用于美化输出，使其更易于阅读。
