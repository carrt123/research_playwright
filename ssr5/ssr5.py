from playwright.sync_api import Playwright, sync_playwright, Page, TimeoutError
import json
import time


def scrape_movie_from_page(page: Page):
    movie_list = []

    try:
        title = page.query_selector('.m-b-sm').inner_text()
        categories = page.query_selector('.categories').inner_text()
        infos = page.query_selector_all('.m-v-sm')
        country, duration = infos[0].inner_text().split('/')
        release_date = infos[1].inner_text()
        score = page.query_selector('.score').inner_text()
        drama = page.query_selector('.drama').inner_text()
        movie_list.append({
            "title": title,
            "categories": categories,
            "country": country,
            "duration": duration,
            "release_date": release_date,
            "score": score,
            "drama": drama
        })

    except TimeoutError:
        print('Timed out waiting for selector')
    return movie_list


def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    urls = [f"https://spa1.scrape.center/detail/{i}/" for i in range(1,41)]

    all_movies = []
    for url in urls:
        page.goto(url)
        page.wait_for_selector('.drama')
        all_movies.extend(scrape_movie_from_page(page))
        print(url)

    browser.close()
    save_movies_into_json(all_movies, 'ssr5_movies.json')


def save_movies_into_json(movies, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=4)


with sync_playwright() as playwright:
    run(playwright)
