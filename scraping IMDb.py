import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class IMDBBot:
    def __init__(self):
        self.bot = None # driver object
        self.data = {} # to store scraped data for each page
        self.open_chrome() # initializing chrome
        self.imdb() # start scraping IMDB website

#----------------------Opening chrome driver----------------------
    def open_chrome(self):
        option = Options()
        service = Service(ChromeDriverManager().install())

        self.bot = webdriver.Chrome(options=option, service=service)

#----------------------Start scraping IMDB website----------------------
    def imdb(self):
        movie_links = self.get_movie_links() # web crawling all movie links in this page

        total_links = len(movie_links)
        for index, link in enumerate(movie_links): # Visiting all links by iteration
            print(f"started scraping link {index + 1} of {total_links}")

            self.open_new_tab(link) # Opening the link in new tab

            try:
                self.get_movie_info() # Scraping movie information
                self.add_to_csv() # Adding to csv file

            except Exception as e:
                print(f'Something went wrong\n{e}')

            self.close_tab() # Closing the scraped tab and return to main tab
            self.data = self.data.fromkeys(self.data, '') # Resetting all values in dictionary

#----------------------Web crawling all movies from the site----------------------
    def get_movie_links(self):
        self.bot.get(r'https://www.imdb.com/india/top-rated-indian-movies/') # Entering this link

        table = wait(self.bot, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table[class="chart full-width"]'))
        )
        time.sleep(4)

        return table.find_elements(By.CSS_SELECTOR, 'td[class="titleColumn"]') # returning all links in a list

#----------------------Opening the given link in a new tab----------------------
    def open_new_tab(self, td):
        td.find_element(By.TAG_NAME, 'a').send_keys(Keys.CONTROL + Keys.ENTER) # Opening new tab
        self.bot.switch_to.window(self.bot.window_handles[1]) # Switching the web driver to the new tab

        wait(self.bot, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-testid="hero-title-block__title"]'))
        )
        time.sleep(3)

#----------------------Scraping all movie info and adding it to data dictionary----------------------
    def get_movie_info(self):
        soup = self.get_page_source() # Get page source using BeautifulSoup

        title = soup.find('h1', {'data-testid': "hero-title-block__title"}).text
        self.data['title'] = title

        meta_data = soup.find('ul', {'data-testid': "hero-title-block__metadata"}).find_all(
            'li', {'class': "ipc-inline-list__item"})
        release_year = meta_data[0].find('a', {'role': "button"}).text
        self.data['released year'] = release_year

        duration = meta_data[-1].text.strip()
        self.data['duration'] = duration

        rating = soup.find('span', {'class': "sc-7ab21ed2-1 eUYAaq"}).text
        self.data['rating'] = rating

        story_line = soup.find('span', {'class': "sc-b5a9e5a3-1 iVsSMD"}).text
        self.data['story line'] = story_line

        # where to watch details may not be available in some movies, so I'm using the try statement
        try:
            watch_details = soup.find('div', {'class': "sc-3b14d2c8-5 kYRgUX"})
            watch_link = watch_details.find('a', {'data-testid': "tm-box-pwo-btn"}).get('href')
            watch_on = watch_details.find('div', {'class': "sc-3b14d2c8-1 aOXVA"}).text.split('on')[-1].strip()
        except:
            watch_link = 'N/A'
            watch_on = 'N/A'

        self.data['watch on'] = watch_on
        self.data['watch link'] = watch_link

#----------------------Get page content in BeautifulSoup----------------------
    def get_page_source(self):
        page_source = self.bot.page_source
        soup = BeautifulSoup(page_source, 'lxml')

        return soup

#----------------------adding data to CSV file----------------------
    def add_to_csv(self):
        file_name = 'Top rated Indian movies.csv'
        files = os.listdir() # Getting list of files in the directory

        # Setting field names for csv to add the data
        fieldnames = ['title', 'released year', 'duration', 'rating', 'story line', 'watch on', 'watch link']

        # checking if file exist or not
        if file_name in files:
            with open(file_name, 'a', newline='', encoding='utf-8') as f:
                csv_dict_writer = csv.DictWriter(f, fieldnames=fieldnames)

                csv_dict_writer.writerow(self.data) # writing the data

        else:
            with open(file_name, 'w', newline='', encoding='utf-8') as f:
                csv_dict_writer = csv.DictWriter(f, fieldnames=fieldnames)

                csv_dict_writer.writeheader() # writing header
                csv_dict_writer.writerow(self.data)

        print("data successfully added to csv\n\n")

#----------------------Closing the new tab and switch to main tab----------------------
    def close_tab(self):
        self.bot.close() # Closing the tab
        self.bot.switch_to.window(self.bot.window_handles[0]) # Switching to main tab
        time.sleep(0.5)


if __name__ == '__main__':
    scrape_imdb = IMDBBot
    scrape_imdb()
    print('Completed Scraping')
