#NOTE: See scraping_helpers.py for sourcing - the code in these two files is almost identical and this file is not used in production.

import csv
import time
import pickle
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def data_arc(dataframe):
    # Pickle documentation: https://docs.python.org/3/library/pickle.html
    try:
        arc_data = pickle.load(open("arc.pkl", "rb"))
        arc_data.append(dataframe)
    except:
        arc_data = [dataframe]
    pickle.dump(arc_data, open("arc.pkl", "wb"))

def data_arc_check(url):
    try:
        arc_data = pickle.load(open("arc.pkl", "rb"))
    except:
        return True
    for dataframe in arc_data:
        if dataframe['url'] ==  url:
            print("Pass on " + url)
            return False
    return True

def twitter_harvester_init(username="", password=""):
    #TODO: Heroku config dongxi goes here
    driver = webdriver.Chrome()
    # Login to Twitter
    driver.get("https://twitter.com/login")
    element = driver.find_element_by_xpath("//*[@id=\"page-container\"]/div/div[1]/form/fieldset/div[1]/input")
    element.send_keys(username)
    element = driver.find_element_by_xpath("//*[@id=\"page-container\"]/div/div[1]/form/fieldset/div[2]/input")
    element.send_keys(password)
    element = driver.find_element_by_xpath("//*[@id=\"page-container\"]/div/div[1]/form/div[2]/button")
    element.click()
    return driver

def xpath_to_count(xpath, take_off_word=False):
    element = driver.find_element_by_xpath(xpath)
    num_to_process = element.text
    num_to_process = num_to_process.split(",")
    num_to_process = "".join(num_to_process)
    if take_off_word:
        num_to_process = num_to_process.split(" Tweets")
        num_to_process = "".join(num_to_process)
        num_to_process = num_to_process.split(" Tweet")
        num_to_process = "".join(num_to_process)
        num_to_process = num_to_process.split(" Likes")
        num_to_process = "".join(num_to_process)
        num_to_process = num_to_process.split(" Like")
        num_to_process = "".join(num_to_process)
    if "K" in num_to_process:
        num_to_process = num_to_process[:-1]
        if "." in num_to_process:
            num_to_process = num_to_process.split(".")
            num_to_process = (int(num_to_process[0]) * 1000) + (int(num_to_process[1]) * 100)
        else:
            num_to_process = (int(num_to_process) * 1000)
    elif "M" in num_to_process:
        num_to_process = num_to_process[:-1]
        if "." in num_to_process:
            num_to_process = num_to_process.split(".")
            num_to_process = (int(num_to_process[0]) * 1000000) + (int(num_to_process[1]) * 100000)
        else:
            num_to_process = (int(num_to_process) * 1000000)
    return int(num_to_process)

def xpath_cylcotron(attempt, type):
    if type == "following":
        paths = ["//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[5]/div[1]/a/span[1]/span", "//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/div[4]/div[1]/a/span[1]/span", '//*[@id="react-root"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[4]/div[1]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[1]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[1]/a/span[1]/span']
        return paths[attempt]
    elif type == "follower":
        paths = ["//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[5]/div[2]/a/span[1]/span", '//*[@id="react-root"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/div[4]/div[2]/a/span[1]/span', '//*[@id="react-root"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[4]/div[2]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[2]/a/span[1]/span', '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/div[1]/div[2]/div[5]/div[2]/a/span[1]/span']
        return paths[attempt]
    else:
        raise "invalid type"

#TODO: Handel timeouts
def harvest_account(driver, url, round=0, loop_harvest=True):
    # Check if tweet or account URL, navigate accordingly, validate URL
    if requests.get(url).status_code // 100 != 2:
        raise Exception('Invalid URL')
    # We're just going to assume that the link is well formed and that we've been given an account URL for now
    # if "twitter.com/" in url: #check to make sure that it's a Twitter url
    #     if "/staus/" in url:
    #         driver.get(url)
            # get the account, make it the new url
    # make sure is not just twitter homepage
    #Navigate to reported URL
    data_package = {"url":url}
    driver.get(url)
    # Loading Test
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
            locations_index += 1
            while_ct += 1
            print("In the except, while count:", str(while_ct))
            if while_ct > 100:
                driver.get("https://twitter.com/home")
                time.sleep(0.5)
                driver.get(url)
                while_ct = 0
            if locations_index == loc_len:
                locations_index = 0
            #Fix rate limiting
            if "Sorry, you are rate limited. Please wait a few moments then try again." in driver.page_source:
                print("Twitter has rate limited us, waiting 3 minutes and then trying again.")
                time.sleep(180)
                driver.get(url)
            # Fix accounts with sensitive content
            if "Caution: This profile may include potentially sensitive content." in driver.page_source:
                driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div/main/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[3]/div').click()
            #
            if "Account suspended" in driver.page_source:
                return []

    # Following Count
    following_count = xpath_to_count(xpath_cylcotron(locations_index, "following"))
    data_package["following_count"] = following_count
    # Follower Count
    follower_count = xpath_to_count(xpath_cylcotron(locations_index, "follower"))
    data_package["follower_count"] = follower_count
    # Statuses Count: Number of tweets and retweets/ replies
    tweet_count = xpath_to_count("//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div[2]/div/div", take_off_word=True)
    data_package["tweet_count"] = tweet_count
    # Protected
    source = driver.page_source
    if "These Tweets are protected" in source and "Only approved followers can see" in source:
        protected = True
        data_package["protected"] = True
    else:
        protected = False
        data_package["protected"] = False
    # Profile Uses Background image: binary indicator (deprecated for the most part) -> False
    element = driver.find_element_by_xpath("//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[2]/div/div/div[1]/div[1]")
    if element.text != "":
        data_package["default_background"] = False
    else:
        data_package["default_background"] = True
    # Verified: binary indicator
    if "aria-label=\"Verified account\"" in source:
        data_package["verified"] = True
    else:
        data_package["verified"] = False
    # Liked tweet Count
    driver.get(url + "/likes")
    time.sleep(1) #TODO: Speed this up
    while True:
        print("In while loop.")
        try:
            like_count = xpath_to_count("//*[@id=\"react-root\"]/div/div/div/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div[2]/div/div", take_off_word=True)
            break
        except:
            try:
                like_count = xpath_to_count('//*[@id="react-root"]/div/div/div[2]/header/div[2]/div[1]/div/div/div/div/div/div[2]/div/div', take_off_word=True)
                break
            except:
                pass
    data_package["like_count"] = like_count
    # Default Profile picture: binary indicator (deprecated for the most part)
    if "<img alt=\"\" draggable=\"true\" src=\"https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png\" class=\"css-9pa8cd\">" in source:
        data_package["defaut_profile"] = True
    else:
        data_package["defaut_profile"] = False
    # List of people following the bot up to the second order
    """
    driver.get(url + "/followers")
    time.sleep(1) #TODO: Speed this up and check if the person has no followers
    for i in range(5):
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
    """
    print(str(data_package))
    data_package = [data_package]

    #Get other associated account data
    if loop_harvest:
        round += 1
        if round < 3:
            for follower in follower_urls:
                for info_packet in harvest_account(driver, "https://twitter.com" + follower, round):
                    data_package.append(info_packet)

    return data_package




# def listed_twitter_harvester(account_list, username="", password=""):
#     assert isinstance(username, str)
#     assert isinstance(password, str)
#     assert isinstance(account_list, list)
#     data_list = []
#     driver = twitter_harvester_init(username, password)
#     for account in account_list:
#         data_list.append(harvest_account(driver, account))

username = "begonebot2023@gmail.com"
password = "begonebot12" #should be stored as an environment variable
# url = "https://twitter.com/taylorswift13"
# url = "https://twitter.com/Jocelyn75950654"
# url = "https://twitter.com/WhatWouldBoydDo"
# url = "https://twitter.com/SwiftOnSecurity"
driver = twitter_harvester_init(username, password)
with open('fax.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(str(row))
        if data_arc_check("https://twitter.com/" + row["id"]):
            dataframe = harvest_account(driver, "https://twitter.com/" + row["id"], loop_harvest=False)
            if dataframe != []:
                dataframe[0]['bot_state'] = row["state"]
                data_arc(dataframe[0])
