''' Script To Read Keywords of a specific application ON Play Store/App Store '''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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
        keywords += get_keywords_from_string(str(row))
    return keywords

def get_keywords_from_string(app_keyword:str):
    temp_keywords = ast.literal_eval(app_keyword)
    return [item.strip() for item in temp_keywords]

def frequency_count_dictionary(keyword_list:list):
    freq = {} 
    for item in keyword_list: 
        if (item in freq): 
            freq[item] += 1
        else: 
            freq[item] = 1
    return freq

def get_comma_seperated_string(keyword_list:list):
    key_string = str(keyword_list)
    table =key_string.maketrans("","","[]'")
    key_string = key_string.translate(table)
    return key_string

class elements_value_has_changed(object):
    def __init__(self,browser,args:list):
        self.arguments = args
        self.prev_val = [ browser.find_element_by_xpath(item).text for item in args]

    def __call__(self, browser):
        cur_val = [browser.find_element_by_xpath(item).text for item in self.arguments]
        for old,new in zip(self.prev_val,cur_val):
            if old != new:
                self.prev_val = cur_val
                return True
        return False

class Platform(enum.Enum):
    android = 'android'
    ios = 'ios'

class KeywordCollector:
    def __init__(self, platform:Platform):
        self.platform = platform

    def open_browser(self,web_driver_path:str,headless=False):
        # Creating an instance webdriver
        if headless :
            options = Options()
            options.headless = True
            self.browser = webdriver.Chrome(executable_path=web_driver_path,chrome_options=options)
        else :
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
                print(item)
                app_details_df = app_details_df.append(item, ignore_index=True)
        return app_details_df

class KeywordResearch:
    
    def open_browser(self,web_driver_path:str,headless=False):
        # Creating an instance webdriver
        if headless :
            options = Options()
            options.headless = True
            self.browser = webdriver.Chrome(executable_path=web_driver_path,chrome_options=options)
        else :
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
    
    def goto_keyword_ranking(self):
        self.browser.get('https://sensortower.com/aso/keyword-rankings')

        # wait for close button in free tier
        WebDriverWait(self.browser,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="country-limitation-upgrade-modal"]/a')))
        close = self.browser.find_element_by_xpath('//*[@id="country-limitation-upgrade-modal"]/a')
        close.click()

    def clear_keyword_ranking(self):
        # edit keyword
        self.edit_keyword = self.browser.find_element_by_xpath('/html/body/div[3]/section/div[2]/div/div/button[1]')
        self.edit_keyword.click()

        #select all
        self.select_all = self.browser.find_element_by_xpath('/html/body/div[3]/section/div[2]/div/div/div[2]/button[1]')
        self.select_all.click()

        #delete keywords
        self.delete_selected = self.browser.find_element_by_xpath('/html/body/div[3]/section/div[2]/div/div/div[2]/button[3]')
        self.delete_selected.click()

        WebDriverWait(self.browser,10).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[13]/div[2]')))
        #confirm delete
        self.confirm_delete = self.browser.find_element_by_xpath('/html/body/div[13]/div[2]/div/div[3]/div/button')
        self.confirm_delete.click()

    def read_traffic_and_difficulty(self,keyword_list:list):
        keyword_details_df = pd.DataFrame(columns=['KEYWORD','TRAFFIC','DIFFICULTY'])

        if not EC.presence_of_element_located((By.CLASS_NAME,'add-keyword-input')):
            self.clear_keyword_ranking()
        #input box
        # self.input_box = self.browser.find_element_by_xpath('/html/body/div[3]/section/div[2]/div/div[2]/div[1]/div/input')
        for i in range(0,len(keyword_list),8):
            WebDriverWait(self.browser,5).until(EC.presence_of_element_located((By.CLASS_NAME,'add-keyword-input')))
            self.input_box = self.browser.find_element_by_class_name('add-keyword-input')

            #convert list into 8 batch string 
            input_string = get_comma_seperated_string(keyword_list[i:min(i+8,len(keyword_list))])
            
            #input string
            self.input_box.clear()
            self.input_box.send_keys(input_string)
            self.track_button = self.browser.find_element_by_xpath('/html/body/div[3]/section/div[2]/div/div[2]/div[3]/div/button')
            self.track_button.click()

            # wait for data
            WebDriverWait(self.browser,10).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[3]/section/div[2]/div/table')))

            # get keyword data for each row
            keywords_data = self.browser.find_elements_by_class_name('keyword-overview-table-body-row')
            
            for i in range(1,len(keywords_data)+1) :
                # /html/body/div[3]/section/div[2]/div/table/tbody/tr[1]/td[1]/span[2]
                # /html/body/div[3]/section/div[2]/div/table/tbody/tr[1]/td[2]
                # /html/body/div[3]/section/div[2]/div/table/tbody/tr[1]/td[3]
                path = "/html/body/div[3]/section/div[2]/div/table/tbody/tr[{}]".format(i)
                keyword = self.browser.find_element_by_xpath(path + '/td[1]/span[2]').text
                traffic =  self.browser.find_element_by_xpath(path + '/td[2]').text
                difficulty = self.browser.find_element_by_xpath(path + '/td[3]').text
                item = {'KEYWORD':keyword,'TRAFFIC':traffic,'DIFFICULTY':difficulty}
                print(item)
                keyword_details_df = keyword_details_df.append(item,ignore_index=True)
            self.clear_keyword_ranking()
        return keyword_details_df


