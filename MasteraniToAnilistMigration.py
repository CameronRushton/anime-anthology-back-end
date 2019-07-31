from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import os
import sys
import time

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")



HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive'
          }

CHROMEDRIVER_PATH = "/"  # This file's location
animeNames = []
options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-gpu')
browser = webdriver.Chrome(options=options)  # Replace with .Firefox(), or with the browser of your choice
animeURLs = open("animeURLs.txt", "w+")
animeToMigrateArray = next(os.walk('./anime'))[1]

for animeName in animeToMigrateArray:
    browser.get("https://anilist.co/search/anime")
    time.sleep(1)
    searchBar = browser.find_element_by_xpath("//*[@id=\"app\"]/div[3]/div/div[1]/div[1]/input")
    searchBar.clear()
    time.sleep(1)
    searchBar.send_keys(animeName)
    time.sleep(2)

    animeToMigrateArray = next(os.walk('./anime'))[1]
    animePageButtonInSearch = browser.find_element_by_xpath("//*[@id=\"app\"]/div[3]/div/div[2]/div[1]/a").click()

    result = query_yes_no("Does this anime look correct for " + animeName + "?")
    if not result:
        continue

    animeURLs.write(animeName + "\n")
    # if there is a newline character at the end, remove it
    if "\n" == animeName[-1]:
        animeName = animeName[:-2]
    # if there is a slash at the end of the url, remove it
    if (animeName[len(animeName) - 1] == '/'):
        animeName = animeName[:-1]
    k = animeName.rfind("/")
    animeName = animeName[k + 1:]
    # Assumes you are already on the anime page
    resourceCount = 0
    resourcePath = "anime/" + animeName + "/"
    try:
        os.makedirs(resourcePath + "images/")
    except FileExistsError:
        print("WARNING: " + resourcePath + " already exists; overwriting files..")

    # Get the box image source
    element = browser.find_element_by_xpath('//*[@id="app"]/div[3]/div/div[1]/div[2]/div/div[1]/div/img')
    boxArtUrl = element.get_attribute('src')

    try:
        # Download the image
        # urlretrieve(boxArtUrl, resourcePath + "images/" + animeNames[i] + "-box-art.png") This is no good for websites protecting against DDoS attacks using things like cloudflare
        # https://stackoverflow.com/questions/49530566/download-an-image-using-selenium-webdriver-in-python
        # Use selenium to download the image by passing the cookies to a requests session, bypassing logins and DDoS protection systems
        session = requests.session()
        session.headers.update(HEADER)
        for cookie in browser.get_cookies():
            c = {cookie['name']: cookie['value']}
            session.cookies.update(c)
        resource = session.get(boxArtUrl, allow_redirects=True)
        open(resourcePath + "images/" + animeName + "-anilist-box-art.jpg", 'wb').write(resource.content)

        resourceCount += 1
    except ValueError:
        # Failed to download image (may not exist)
        print("No box image found...")

    # Get the background/cover image source
    element = browser.find_element_by_xpath('//*[@id="app"]/div[3]/div/div[1]/div[1]')
    rawCoverImageUrl = element.get_attribute('style')
    startIndex = rawCoverImageUrl.find("http")
    ending = rawCoverImageUrl.rfind(".jpg")
    if ending < 0:
        ending = rawCoverImageUrl.rfind(".png")
    endIndex = len(rawCoverImageUrl) - ending - 4
    coverImageUrl = rawCoverImageUrl[startIndex:-endIndex]
    try:
        # Download the image
        # urlretrieve(coverImageUrl, resourcePath + "images/" + animeNames[i] + "-cover.jpg")
        session = requests.session()
        session.headers.update(HEADER)
        for cookie in browser.get_cookies():
            c = {cookie['name']: cookie['value']}
            session.cookies.update(c)
        resource = session.get(coverImageUrl, allow_redirects=True)
        open(resourcePath + "images/" + animeName + "-anilist-cover.jpg", 'wb').write(resource.content)
        resourceCount += 1
    except ValueError:
        # Failed to download image (may not exist)
        print("No background found...")

    dataFile = open(resourcePath + "data.txt", "w+")
    rankingsList = []
    rankings = browser.find_elements_by_xpath("//*[@class='rank-text']")
    for item in rankings:
        rankingsList.append(item.text)
        try:
            dataFile.write(item.text + "\n")
        except UnicodeEncodeError:
            print()  # Ignore - Probably encountered Japanese text

    listData = []
    data = browser.find_elements_by_xpath("//*[@class='data-set']")
    for item in data:
        listData.append(item.text)
        try:
            dataFile.write(item.text + "\n")
        except UnicodeEncodeError:
            print()  # Ignore - Probably encountered Japanese text

    lstData = []
    data = browser.find_elements_by_xpath("//*[@class='data-set data-list']")
    for item in data:
        lstData.append(item.text)
        try:
            dataFile.write(item.text + "\n")
        except UnicodeEncodeError:
            print()  # Ignore - Probably encountered Japanese text

    tagsList = []
    tags = browser.find_elements_by_xpath("//*[@class='tag']")
    for item in tags:
        tagsList.append(item.text)
        try:
            dataFile.write(item.text + "\n")
        except UnicodeEncodeError:
            print()  # Ignore - Probably encountered Japanese text
    dataFile.close()
    resourceCount += 1

    if resourceCount == 3:
        print("Successfully downloaded all resources for " + animeName)

animeURLs.close()
browser.close()



