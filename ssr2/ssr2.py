import re
from playwright.sync_api import Playwright, expect, sync_playwright, Page
import json


# inner_text：获取用户在浏览器中实际看到的文本。
# text_content：获取元素内的所有文本内容，包括不可见的部分和原始文本结构。

def scrape_movie_from_page(page: Page):
    nodes = page.query_selector_all('.el-card.item.m-t.is-hover-shadow')
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


def run(playwright: Playwright, max_pages=10):
    # 使用css选择器定位元素
    browser = playwright.chromium.launch(headless=False,  args=["--ignore-certificate-errors"])
    # --ignore-certificate-errors 忽略证书错误
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://ssr2.scrape.center/")
    all_movies = []
    current_page = 1
    while True:
        all_movies.extend(scrape_movie_from_page(page))
        next_button = page.query_selector('.btn-next')
        if not next_button or 'disabled' in next_button.get_attribute('class'):
            break
        current_page += 1
        if current_page > max_pages:
            break
        next_button.click()
    save_movies_into_json(all_movies, 'ssr2_movies.json')


def save_movies_into_json(movies, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=4)


with sync_playwright() as playwright:
    run(playwright)
