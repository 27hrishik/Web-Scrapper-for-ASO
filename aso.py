''' Script To Read Keywords of a specific application ON Play Store/App Store '''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
import enum
import ast

# Preprocessing Methods

def get_keywords_list(app_keyword_list: list):
    keywords = []
    for row in app_keyword_list :
        temp_keywords = ast.literal_eval(row)
        temp_keywords = [item.strip() for item in temp_keywords]
        keywords += temp_keywords
    return keywords

class elements_value_has_changed(object):
    def __init__(self,*args):
        self.arguments = args

    def __call__(self, browser):
        elements = [(browser.find_element_by_xpath(item),value) for item, value in self.arguments]
        for element in elements:
            if element[0].text != element[1]:
                return True
        return False

class Platform(enum.Enum):
    android = 'android'
    ios = 'ios'

class KeywordCollector:
    def __init__(self, platform:Platform):
        self.platform = platform

    def open_browser(self,web_driver_path:str):
        # Creating an instance webdriver
        self.browser = webdriver.Chrome(executable_path=web_driver_path)
        # Opening Sensor Tower
        self.browser.get('https://www.sensortower.com')

    def get_keywords_from_app_name(self, app_name_list:list):
        #create a Empty Data Frame
        app_details_df = pd.DataFrame(columns=['APP_NAME', 'SENSOR_SCORE', 'VISIBILITY', 'INTERNATIONALIZATION', 'KEYWORDS'])

        for app_name in app_name_list:
            search = self.browser.find_element_by_id('app-search-input')
            search.clear()
            search.send_keys(app_name)
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'autocomplete-dropdown')))
            auto_complete_candidate = self.browser.find_elements_by_class_name('autocomplete-list-item')
            # auto_complete_list = [item for item in auto_complete_candidate if
            #                      EC.presence_of_element_located((By.CLASS_NAME,platform_class_name))]
            auto_complete_list = []
            for auto_complete in auto_complete_candidate:
                try:
                    flag = auto_complete.find_element_by_class_name(self.platform.value)
                    auto_complete_list.append(auto_complete)
                except NoSuchElementException:
                    continue
            if len(auto_complete_list) > 0:
                auto_complete_list[0].click()
                WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'app-name')))
                item = dict()
                item['APP_NAME'] = self.browser.find_element_by_class_name('app-name').text  # //*[@id="app"]/div/span[1]
                grades = self.browser.find_elements_by_class_name('grade')
                item['SENSOR_SCORE'] = grades[0].text
                item['VISIBILITY'] = grades[1].text
                item['INTERNATIONALIZATION'] = grades[2].text
                item['KEYWORDS'] = [keyword.text for keyword in self.browser.find_elements_by_class_name('keyword')]
                app_details_df = app_details_df.append(item, ignore_index=True)
        return app_details_df

class KeywordResearch:
    
    def open_browser(self,web_driver_path:str):
        # Creating an instance webdriver
        self.browser = webdriver.Chrome(executable_path=web_driver_path)

        # Opening Sensor Tower
        self.browser.get('https://sensortower.com/users/sign_in')

    def login(self,username:str,password:str):
        # Wait for browser to load login page
        WebDriverWait(self.browser,10).until(EC.presence_of_element_located((By.NAME,'user[email]')))
        email = self.browser.find_element_by_name('user[email]')
        email.clear()
        email.send_keys(username)
        pwd = self.browser.find_element_by_name('user[password]')
        pwd.clear()
        pwd.send_keys(password)
        submit = self.browser.find_element_by_name('commit')
        submit.click()
    
    def goto_keyword_research(self):
        self.browser.get('https://sensortower.com/aso/keyword-research')

        # wait for close button in free tier
        WebDriverWait(self.browser,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="country-limitation-upgrade-modal"]/a')))
        close = self.browser.find_element_by_xpath('//*[@id="country-limitation-upgrade-modal"]/a')
        close.click()

    def intialize_keyword_research(self):
        # entering keyword
        self.keyword_input = self.browser.find_element_by_xpath('//*[@id="research-keywords-input"]')

        # research button
        self.research_button = self.browser.find_element_by_xpath('/html/body/div[3]/section/div[1]/div/div[2]/div/button[2]')

        # xpath value for traffic and difficulty
        self.xpath_traffic = '/html/body/div[3]/section/div[2]/table/tbody/tr[1]/td[1]/span'
        self.xpath_difficulty = '/html/body/div[3]/section/div[2]/table/tbody/tr[1]/td[2]/span'

        # try dummy value
        self.keyword_input.send_keys('space')
        self.research_button.click()

        # traffic and difficulty
        WebDriverWait(self.browser,10).until(EC.presence_of_element_located((By.XPATH,self.xpath_traffic)))
        self.traffic = self.browser.find_element_by_xpath(self.xpath_traffic)
        self.difficulty = self.browser.find_element_by_xpath(self.xpath_difficulty)

    def read_traffic_and_difficulty(self,keyword_list:list):
        #intialize data frame
        keywords_data_df = pd.DataFrame(columns=['KEYWORD', 'TRAFFIC', 'DIFFICULTY'])
        failed_keywords_df = pd.DataFrame(columns=['KEYWORD'])
        for keyword in keyword_list:
            # entering keyword and wait for updation
            self.keyword_input.clear()
            self.keyword_input.send_keys(keyword)
            self.research_button.click()
            try:
                WebDriverWait(self.browser, 10).until(
                    elements_value_has_changed((self.xpath_traffic, self.traffic.text), (self.xpath_difficulty, self.difficulty.text)))
                print((keyword, self.traffic.text, self.difficulty.text))
                item = {'KEYWORD': keyword, 'TRAFFIC': float(self.traffic.text), 'DIFFICULTY': float(self.difficulty.text)}
                keywords_data_df = keywords_data_df.append(item,ignore_index=True)
            except TimeoutException:
                failed_keywords_df = failed_keywords_df.append({'KEYWORD':keyword},ignore_index=True)
                continue
        return keywords_data_df,failed_keywords_df

    def read_app_names(self,keyword_list:list):
         #intialize data frame
        keywords_data_df = pd.DataFrame(columns=['KEYWORD', 'APP_NAMES'])
        failed_keywords_df = pd.DataFrame(columns=['KEYWORD'])
        for keyword in keyword_list:
            # entering keyword and wait for updation
            self.keyword_input.clear()
            self.keyword_input.send_keys(keyword)
            self.research_button.click()
            try:
                WebDriverWait(self.browser, 10).until(
                    elements_value_has_changed((self.xpath_traffic, self.traffic.text), (self.xpath_difficulty, self.difficulty.text)))
                app_names = self.browser.find_elements_by_class_name('app-name');
                app_names = [item.text for item in app_names]
                print((keyword, app_names))
                item = {'KEYWORD': keyword, 'APP_NAMES':app_names}
                keywords_data_df = keywords_data_df.append(item,ignore_index=True)
            except TimeoutException:
                failed_keywords_df = failed_keywords_df.append({'KEYWORD':keyword},ignore_index=True)
                continue
        return keywords_data_df,failed_keywords_df

class AppResearch:
    def __init__(self, platform:Platform):
        self.platform = platform

    def open_browser(self,web_driver_path:str):
        # Creating an instance webdriver
        self.browser = webdriver.Chrome(executable_path=web_driver_path)

        # Opening Sensor Tower
        self.browser.get('https://sensortower.com/users/sign_in')

    def login(self,username:str,password:str):
        # Wait for browser to load login page
        WebDriverWait(self.browser,10).until(EC.presence_of_element_located((By.NAME,'user[email]')))
        email = self.browser.find_element_by_name('user[email]')
        email.clear()
        email.send_keys(username)
        pwd = self.browser.find_element_by_name('user[password]')
        pwd.clear()
        pwd.send_keys(password)
        submit = self.browser.find_element_by_name('commit')
        submit.click()
    
    def get_app_categories(self, app_name_list:list):
        #create a Empty Data Frame
        app_categories_df = pd.DataFrame(columns=['APP_NAME', 'CATEGORIES'])

        xpath_app_name = '//*[@id="overview"]/div[1]/div/div[1]/div/section[2]/div[1]/div[2]/h1/span'

        for app_name in app_name_list:
            search = self.browser.find_element_by_xpath('//*[@id="primary-app-search-field"]')
            search.clear()
            search.send_keys(app_name)
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'autocomplete-dropdown')))
            auto_complete_candidate = self.browser.find_elements_by_class_name('autocomplete-list-item')
            # auto_complete_list = [item for item in auto_complete_candidate if
            #                      EC.presence_of_element_located((By.CLASS_NAME,platform_class_name))]
            auto_complete_list = []
            for auto_complete in auto_complete_candidate:
                try:
                    flag = auto_complete.find_element_by_class_name(self.platform.value)
                    auto_complete_list.append(auto_complete)
                except NoSuchElementException:
                    continue
            if len(auto_complete_list) > 0:
                auto_complete_list[0].click()
                try:
                    WebDriverWait(self.browser, 10).until(elements_value_has_changed((xpath_app_name,self.browser.find_element_by_xpath(xpath_app_name))))
                except TimeoutError:
                    continue
                item = dict()
                item['APP_NAME'] = self.browser.find_element_by_xpath(xpath_app_name).text 
                categories = self.browser.find_element_by_xpath('//*[@id="about-app"]/table/tbody/tr[2]/td[2]')
                category_tags = categories.find_elements_by_tag_name('a')
                item['CATEGORIES'] = [item.text for item in category_tags]
                print(item)
                app_categories_df = app_categories_df.append(item, ignore_index=True)
        return app_categories_df

