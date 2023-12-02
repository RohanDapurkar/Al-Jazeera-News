from robocorp.tasks import task
from aljazeera import AlJazeeraScraper


def main():
    url = "https://www.aljazeera.com/"

    scraper = AlJazeeraScraper(url)
    scraper.open_the_website()
    scraper.open_the_search_option()
    scraper.search_phrase()
    scraper.click_the_drop_down()
    scraper.click_the_element()
    scraper.extract_data_and_save_to_excel()

    
@task
def minimal_task():
    main()

if __name__ == '__main__':
    minimal_task()
