from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
from datetime import datetime, timedelta

load_dotenv()

class Scraper:

    def __init__(self) -> None:
        self.getenv()
        self.get_driver()
        self.login()
        self.open_horse_bets()

    def getenv(self):
        self.site = os.getenv("WEBSITE")
        self.horse_site = os.getenv("HORSESITE")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.driver_path = os.getenv("DRIVERPATH")

    def get_driver(self):
        self.service = Service(executable_path=self.driver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.get(self.site)
        self.driver.implicitly_wait(10000)

    def login(self):
        username_field = self.driver.find_element(By.ID, "ssc-liu")
        password_field = self.driver.find_element(By.ID, "ssc-lipw")
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        password_field.send_keys(Keys.RETURN)
        
    def open_horse_bets(self):
        self.driver.get(self.horse_site)
        time.sleep(5)
        race_list = self.get_race_list()
        race_times = []
        for race in race_list:
            name = race.get_text()
            race_time = name.split()[0]
            race_times.append(race_time)

        for i,race in enumerate(race_list):
            if i < len(race_list)-1:
                a = race.find("a")
                href = a.get("href")
                self.open_live_video(href, race_times[i], race_times[i+1])
        
        condition = True
        while condition:
            time.sleep(60)
            self.driver.get(self.horse_site)
            new_race_list = self.get_race_list()
            if new_race_list != race_list:
                condition = False
        
        self.open_horse_bets()

    def get_race_list(self):
        horse_racing_section = self.driver.find_element(By.TAG_NAME, "tree-section")
        soup = BeautifulSoup(horse_racing_section.get_attribute("innerHTML"), "html.parser")
        race_names = soup.find("tree-section", {"data": "data", "events": "events", "node": "node", "query": "query"})
        races = race_names.find("ul", class_="section active-section")
        race_list = races.find_all("li")
        race_list = [race for race in race_list if '(' not in race.get_text()]
        race_list = [race for race in race_list if race.get_text().strip()[0].isdigit()]
        return race_list

    def open_live_video(self, href, start_time, end_time):
        race_time = datetime.strptime(start_time, "%H:%M").time()
        close_time = datetime.strptime(end_time, "%H:%M").time()

        current_year = datetime.now().year
        date_element = self.driver.find_element(By.CLASS_NAME, "event-date")
        date_string = date_element.text.strip()
        date_object = datetime.strptime(f"{date_string} {current_year}", "%a %d %b %Y")
        event_date = date_object.strftime("%Y-%m-%d").date()
        
        if not self.event_ended(close_time, event_date):
            self.driver.get(self.site + href)
            print("race time: ", race_time)
            time_difference = self.time_difference(race_time, event_date, True)
            print("open time difference: ", time_difference)
            time.sleep(5)
            page_source = self.driver.page_source
            html_soup = BeautifulSoup(page_source, "html.parser")
            condition = html_soup.find("a", class_=["broadcase-icon" ,"icon-livevideo"])
            if condition is not None:
                time.sleep(max(0,time_difference))
                live_stream = self.driver.find_element(By.LINK_TEXT, "Live Stream")
                live_stream.click()
                self.driver.switch_to.window(self.driver.window_handles[-1])
                closing_time = self.time_difference(close_time, event_date, False)
                print("close time difference: ", closing_time)
                time.sleep(max(0,closing_time))
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

    def event_ended(self, event_date, given_time):
        current_time = datetime.now()
        target_datetime = datetime.combine(event_date, given_time)
        return (current_time > target_datetime)

    def time_difference(self, given_time, event_date, start):
        delay = 30 if start else 60
        current_time = datetime.now()
        target_datetime = datetime.combine(event_date, given_time)
        target_time = target_datetime - timedelta(seconds=delay)
        print("target_time: ", target_time.time())
        time_difference = (target_time - current_time).total_seconds()
        return time_difference

if __name__ == "__main__":
    scraper = Scraper()