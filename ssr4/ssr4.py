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


def run(playwright: Playwright, max_pages=10):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    base_url = "https://ssr4.scrape.center"
    page.goto(base_url)
    all_movies = []
    current_page = 1

    while True:
        movies = page.query_selector_all('.name')
        movie_urls = [movie.get_attribute('href') for movie in movies]
        for url in movie_urls:
            try:
                page.goto(base_url + url)
                all_movies.extend(scrape_movie_from_page(page))
                print(f'Fetched movie: {url}')
            except TimeoutError:
                print(f'Timed out:{base_url + url}')
            page.go_back()

        next_button = page.query_selector('.btn-next')
        if not next_button or 'disabled' in next_button.get_attribute('class'):
            break
        current_page += 1
        if current_page > max_pages:
            break

        next_button.click()
        time.sleep(1)  # 给页面一点时间加载下一个页面

    browser.close()
    save_movies_into_json(all_movies, 'ssr4_movies.json')


def save_movies_into_json(movies, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=4)


with sync_playwright() as playwright:
    run(playwright)
