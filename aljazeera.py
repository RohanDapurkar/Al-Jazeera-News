from datetime import datetime, timedelta
from dateutil import parser
import re
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Robocorp.WorkItems import WorkItems
import pandas as pd

class AlJazeeraScraper:
    def __init__(self, url, excel_file="aljazeera_news.xlsx"):
        self.browser = Selenium()
        self.http = HTTP()
        self.work_items = WorkItems()
        self.phrase = self.work_items["phrase"]
        self.topic = self.work_items["section"]
        self.month_no = self.work_items["months"]

        self.url = url
        self.excel_file = excel_file

    def open_the_website(self):
        self.browser.open_available_browser(self.url, maximized=True)

    def open_the_search_option(self):
        self.browser.wait_until_element_is_enabled("//div[@class='site-header__search-trigger']//button", 120)
        self.browser.click_element("//div[@class='site-header__search-trigger']//button")

    def search_phrase(self):
        
        input_field = "//input[@title='Type search term here']"
        term = self.phrase
        self.browser.wait_until_element_is_enabled(input_field, 30)
        self.browser.input_text(input_field, term)
        self.browser.press_keys(input_field, "ENTER")

    def click_the_drop_down(self):
        self.browser.wait_until_element_is_enabled("//select[@id='search-sort-option']", 120)
        self.browser.click_element("//select[@id='search-sort-option']")

    def click_the_element(self):
        self.browser.wait_until_element_is_enabled("//option[@value='date']", 120)
        self.browser.click_element("//option[@value='date']")

    def extract_data_and_save_to_excel(self):
        current_date = datetime.now()

        if self.month_no == 0 or self.month_no == 1:
            start_date = current_date.replace(day=1)
        elif self.month_no > 1:
            middle_date = current_date.replace(day=15)
            days_to_subtract = (self.month_no - 1) * 30
            new_date = middle_date - timedelta(days=days_to_subtract)
            start_date = new_date.replace(day=1)

        
        data = {
            "Title": [],
            "Date": [],
            "Description": [],
            "Title Count": [],
            "Description Count": [],
            "Money Present": [],
        }
        
        i = 1
        while True:
            try:
                self.browser.wait_until_element_is_enabled(f"(//a[@class='u-clickable-card__link'])[{i}]", 10)
                self.browser.scroll_element_into_view(f"(//a[@class='u-clickable-card__link'])[{i}]")
                paragraph = self.browser.get_text(f'(//div[@class="gc__excerpt"]//p)[{i}]')

                splitted = paragraph.split('...')
                date = splitted[0]

                if 'ago' in date:
                    current_time = datetime.now()
                    value, units, _ = date.split()
                    unit_mapping = {
                        'hour': 'hours',
                        'hours': 'hours',
                        'minute': 'minutes',
                        'minutes': 'minutes',
                        'min\xadutes': 'minutes',
                        'day': 'days',
                        'days': 'days',
                    }

                    delta = timedelta(**{unit_mapping[units]: int(value)})
                    date_obj = current_time - delta
                else:
                    date_obj = parser.parse(date)

                if start_date <= date_obj:
                    titles = self.browser.get_text(f"(//a[@class='u-clickable-card__link'])[{i}]")
                    data["Title"].append(titles)

                    description = splitted[1]
                    data["Description"].append(description)

                    data["Date"].append(date_obj)
                    count_title = titles.lower().count("india")
                    count_description = description.lower().count("india")
                    data["Title Count"].append(count_title)
                    data["Description Count"].append(count_description)

                    money_pattern = r'\$|\d+ dollars|\d+\s*USD'
                    money_in_title = re.search(money_pattern, titles, re.IGNORECASE)
                    money_in_description = re.search(money_pattern, description, re.IGNORECASE)

                    money_present = bool(money_in_title or money_in_description)
                    data["Money Present"].append(money_present)
                    i = i + 1
                else:
                    break
            except:
                print("All the News on the current page are fetched.")
                self.browser.click_element_if_visible('//button[text()="Allow all"]')
                self.browser.scroll_element_into_view('//button[text()="About"]')
                self.browser.click_element('//span[text()="Show more"]')

        df = pd.DataFrame(data)   
        df.to_excel(self.excel_file, index=False)

