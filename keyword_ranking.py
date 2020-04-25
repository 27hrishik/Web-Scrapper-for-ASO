''' Using Sensor tower find the traffic and difficulty of each keywords'''
from aso import *

# sensortower account email and password for free account
login_username = input("Enter your Sensor tower email :")
login_password = input("Enter your password :")

# Keywords list unprocessed
keyword_list = pd.read_csv('android/app_name_and_keywords.csv',index_col=[0])['KEYWORDS'].tolist()

# read the app details file for keywords
keyword_list = get_keywords_list(keyword_list)
keyword_list = set(keyword_list)

# Creating an instance webdriver
browser = webdriver.Chrome(executable_path='/Users/appking/Desktop/chromedriver')

# Opening Sensor Tower
browser.get('https://sensortower.com/users/sign_in')

# Wait for browser to load login page
WebDriverWait(browser,10).until(EC.presence_of_element_located((By.NAME,'user[email]')))
email = browser.find_element_by_name('user[email]')
email.clear()
email.send_keys(login_username)
password = browser.find_element_by_name('user[password]')
password.clear()
password.send_keys(login_password)
submit = browser.find_element_by_name('commit')
submit.click()

# wait for browser to load
WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[2]/div/div[2]/ul[3]/li[3]/div/ul[4]/li[2]/ul/li[5]/a')))
keyword_research = browser.find_element_by_xpath('/html/body/div[2]/div/div[2]/ul[3]/li[3]/div/ul[4]/li[2]/ul/li[5]/a')
keyword_research.click()

# wait for close button
WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="country-limitation-upgrade-modal"]/a')))
close = browser.find_element_by_xpath('//*[@id="country-limitation-upgrade-modal"]/a')
close.click()

# entering keyword
keyword_input = browser.find_element_by_xpath('//*[@id="research-keywords-input"]')

# research button
research_button = browser.find_element_by_xpath('/html/body/div[3]/section/div[1]/div/div[2]/div/button[2]')

# xpath value for traffic and difficulty
xpath_traffic = '/html/body/div[3]/section/div[2]/table/tbody/tr[1]/td[1]/span'
xpath_difficulty = '/html/body/div[3]/section/div[2]/table/tbody/tr[1]/td[2]/span'

# traffic and difficulty
WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,xpath_traffic)))
traffic = browser.find_element_by_xpath(xpath_traffic)
difficulty = browser.find_element_by_xpath(xpath_difficulty)

keywords_data_df = pd.DataFrame(columns=['KEYWORD', 'TRAFFIC', 'DIFFICULTY'])

for keyword in keyword_list:
    # entering keyword and wait for updation
    keyword_input.clear()
    keyword_input.send_keys(keyword)
    research_button.click()
    try:
        WebDriverWait(browser, 10).until(
            elements_value_has_changed((xpath_traffic, traffic.text), (xpath_difficulty, difficulty.text)))
        print((keyword, traffic.text, difficulty.text))
        item = {'KEYWORD': keyword, 'TRAFFIC': float(traffic.text), 'DIFFICULTY': float(difficulty.text)}
        keywords_data_df = keywords_data_df.append(item);
    except TimeoutException:
        continue
keywords_data_df.to_csv('Data/traffic_and_difficulty.csv')
