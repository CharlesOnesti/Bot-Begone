import csv
import time
import pickle
import requests
import smtplib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def twitter_harvester_init(username="", password=""):
    # Heroku environment configuration information for remote selenium found here: https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c
    # https://www.youtube.com/watch?v=Ven-pqwk3ec
    # https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-chromedriver
    # Define routes so that Selenium can run on Heroku
    GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google-chrome'
    CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

    # Setup Chrome to be able to run on a server environment
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = GOOGLE_CHROME_PATH
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
    # Login to Twitter
    driver.get("https://twitter.com/login")
    time.sleep(0.5)
    element = driver.find_element_by_xpath("//*[@id=\"page-container\"]/div/div[1]/form/fieldset/div[1]/input")
    element.send_keys(username)
    element = driver.find_element_by_xpath("//*[@id=\"page-container\"]/div/div[1]/form/fieldset/div[2]/input")
    element.send_keys(password)
    element = driver.find_element_by_xpath("//*[@id=\"page-container\"]/div/div[1]/form/div[2]/button")
    element.click()
    return driver

# Strip the data out of an xpath
def xpath_to_count(xpath, driver, take_off_word=False):
    # Selenium text only: https://stackoverflow.com/questions/12325454/how-to-get-text-of-an-element-in-selenium-webdriver-without-including-child-ele
    # Find the data, convert what is inside to text
    element = driver.find_element_by_xpath(xpath)
    num_to_process = element.text
    # Remove comma
    num_to_process = num_to_process.split(",")
    num_to_process = "".join(num_to_process)
    # Remove words
    if take_off_word:
        num_to_process = num_to_process.split(" Tweets")
        num_to_process = "".join(num_to_process)
        num_to_process = num_to_process.split(" Tweet")
        num_to_process = "".join(num_to_process)
        num_to_process = num_to_process.split(" Likes")
        num_to_process = "".join(num_to_process)
        num_to_process = num_to_process.split(" Like")
        num_to_process = "".join(num_to_process)
    # Convert thousands adjustment
    if "K" in num_to_process:
        num_to_process = num_to_process[:-1]
        if "." in num_to_process:
            num_to_process = num_to_process.split(".")
            num_to_process = (int(num_to_process[0]) * 1000) + (int(num_to_process[1]) * 100)
        else:
            num_to_process = (int(num_to_process) * 1000)
    # Convert millions adjustment
    elif "M" in num_to_process:
        num_to_process = num_to_process[:-1]
        if "." in num_to_process:
            num_to_process = num_to_process.split(".")
            num_to_process = (int(num_to_process[0]) * 1000000) + (int(num_to_process[1]) * 100000)
        else:
            num_to_process = (int(num_to_process) * 1000000)
    # Return value
    return int(num_to_process)

# Ease figuring out how the Twitter account is formatted by easily returning relevand xpaths
def xpath_cylcotron(attempt, type):
    if type == "following":
        paths = ["//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[5]/div[1]/a/span[1]/span", "//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/div[4]/div[1]/a/span[1]/span", '//*[@id="react-root"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[4]/div[1]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[1]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[1]/a/span[1]/span']
        return paths[attempt]
    elif type == "follower":
        paths = ["//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[5]/div[2]/a/span[1]/span", '//*[@id="react-root"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/div[4]/div[2]/a/span[1]/span', '//*[@id="react-root"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[4]/div[2]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[2]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[2]/a/span[1]/span']
        return paths[attempt]
    else:
        raise "invalid type"

def harvest_account(driver, url, round=0, loop_harvest=True):
    # Beautiful soup documentation: https://www.dataquest.io/blog/web-scraping-tutorial-python/
    # Selenium documentation: https://selenium-python.readthedocs.io/index.html
    # Selenium page source: https://stackoverflow.com/questions/7861775/python-selenium-accessing-html-source
    #Pack in and fetch URL
    data_package = {"url":url}
    driver.get(url)
    # Make sure that the page is loaded before we try to scrape it
    not_yet_loaded = True
    locations_index = 0
    locations = ["//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[5]/div[1]/a/span[1]/span", "//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/div[4]/div[1]/a/span[1]/span", '//*[@id="react-root"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[4]/div[1]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[1]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[1]/a/span[1]/span']
    loc_len = len(locations)
    while_ct = 0
    while not_yet_loaded:
        try:
            element = driver.find_element_by_xpath(locations[locations_index])
            not_yet_loaded = False
        except:
            # Handel the case that it may also be a different type of page
            locations_index += 1
            while_ct += 1
            print("In the except, while count:", str(while_ct))
            # Try reloading the page to see if element failed to load and xpath impacted
            if while_ct > 100:
                driver.get("https://twitter.com/home")
                time.sleep(0.5)
                driver.get(url)
                while_ct = 0
            if locations_index == loc_len:
                locations_index = 0
            # Fix rate limiting issue
            if "Sorry, you are rate limited. Please wait a few moments then try again." in driver.page_source:
                print("Twitter has rate limited us, waiting 3 minutes and then trying again.")
                time.sleep(180)
                driver.get(url)
            # Fix accounts with sensitive content
            if "Caution: This profile may include potentially sensitive content." in driver.page_source:
                driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div/main/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[3]/div').click()
            # Fix accounts that are suspended
            if "Account suspended" in driver.page_source:
                return []

    # Get following Count
    following_count = xpath_to_count(xpath_cylcotron(locations_index, "following"), driver)
    data_package["following_count"] = following_count
    # Get follower Count
    follower_count = xpath_to_count(xpath_cylcotron(locations_index, "follower"), driver)
    data_package["follower_count"] = follower_count
    # Statuses Count: Number of tweets and retweets/replies
    tweet_count = xpath_to_count("//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div[2]/div/div", driver, take_off_word=True)
    data_package["tweet_count"] = tweet_count
    # See if account is protected
    source = driver.page_source
    if "These Tweets are protected" in source and "Only approved followers can see" in source:
        protected = True
        data_package["protected"] = True
    else:
        protected = False
        data_package["protected"] = False
    # See if the profile has a background image
    element = driver.find_element_by_xpath("//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div[1]")
    if element.text != "":
        data_package["default_background"] = False
    else:
        data_package["default_background"] = True
    # See if the profile is verified
    if "aria-label=\"Verified account\"" in source:
        data_package["verified"] = True
    else:
        data_package["verified"] = False
    # Get the liked tweet Count
    driver.get(url + "/likes")
    time.sleep(1)
    while True:
        print("In while loop.")
        try:
            like_count = xpath_to_count("//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div[2]/div/div", driver, take_off_word=True)
            break
        except:
            pass
    data_package["like_count"] = like_count
    # See if the user has the default Profile picture
    if "<img alt=\"\" draggable=\"true\" src=\"https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png\" class=\"css-9pa8cd\">" in source:
        data_package["defaut_profile"] = True
    else:
        data_package["defaut_profile"] = False
    # List of people following the bot up to the second order
    if round <= 1:
        driver.get(url + "/followers")
        time.sleep(1)
        for i in range(2):
            # Selenium scrolling: https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_divs = soup.find_all('div')
        follower_div = []
        follower_urls = []
        for div in all_divs:
            try:
                if div["data-testid"] == "UserCell":
                    follower_div.append(div)
                    print("Found a follower.")
            except:
                pass
        for div in follower_div:
            follower_urls.append(div.find('a')['href'])
        data_package['followers'] = follower_urls
    print(str(data_package))
    data_package = [data_package]

    #Get other associated account data
    if loop_harvest:
        round += 1
        if round < 3:
            fl_limiter = 0
            for follower in follower_urls:
                # Limiter to speed account checking in resource/time sensitive scenarios
                if fl_limiter < 1:
                    for info_packet in harvest_account(driver, "https://twitter.com" + follower, round):
                        data_package.append(info_packet)
                    fl_limiter += 1
                else:
                    break

    return data_package

def report_account(driver, url):
    #sources:
    # https://devanswers.co/allow-less-secure-apps-access-gmail-account/
    # https://www.geeksforgeeks.org/send-mail-gmail-account-using-python/
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login("begonebot2023", "begonebot12")
    # message to be sent
    message = "Hello, we think we have found a phishing, bot, or spam account and wanted to report it to you. The URL of the account is {}. This is an automated message. Thank you for your time.".format(url)
    message = message.split(":")
    message = " ".join(message)
    # sending the mail
    # Send to Twitter
    s.sendmail("begonebot2023@gmail.com", "phishing-report@us-cert.gov", message)
    # Send to researcher
    s.sendmail("begonebot2023@gmail.com", "support@twitter.com", message)
    # terminating the session
    s.quit()
