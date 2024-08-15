import re
from playwright.sync_api import Playwright, expect, sync_playwright
import json


# inner_text：获取用户在浏览器中实际看到的文本。
# text_content：获取元素内的所有文本内容，包括不可见的部分和原始文本结构。

def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://ssr1.scrape.center/")
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
    json_data = json.dumps(movie_list, ensure_ascii=False, indent=4)
    # ensure_ascii = False: 这个参数指定了在编码时是否确保输出是ASCII码
    # indent = 4: 这个参数指定了JSON字符串的缩进级别，用于美化输出

    # 将数据写入文件
    with open('./ssr1_movies.json', 'w', encoding='utf-8') as f:
        f.write(json_data)

    browser.close()


with sync_playwright() as playwright:
    run(playwright)
