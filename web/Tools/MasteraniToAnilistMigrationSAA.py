from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive'
          }

CHROMEDRIVER_PATH = "/"  # This file's location
options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-gpu')
options.add_argument("--window-size=1920,1080")
browser = webdriver.Chrome(options=options)  # Replace with .Firefox(), or with the browser of your choice
logFile = open("logFile.txt", "w+")
newURLs = open("newURLs.txt", "w+")

DOCUMENT = "SAA.txt"
# Get all urls in SAA.txt
# Grab every url with 'http' in it and extract anime name from the url
file = open(DOCUMENT, "r")
print("INFO: Compiling URLs...")
animeToMigrateArray = []
lines = file.readlines()
file.close()
for line in lines:
    for word in line.split(" "):
        if word.startswith("http"):
            # save anime url
            animeToMigrateArray.append(word)

for animeName in animeToMigrateArray:
    # if there is a newline character at the end, remove it
    if "\n" == animeName[-1]:
        animeName = animeName[:-2]
    browser.get("https://anilist.co/search/anime")
    logFile.write(animeName + " -> ")
    time.sleep(1)
    searchBar = browser.find_element_by_xpath("//*[@id=\"app\"]/div[3]/div/div[1]/div[1]/input")
    searchBar.clear()
    time.sleep(1)
    searchBar.send_keys(animeName)
    time.sleep(2)

    #animeToMigrateArray = next(os.walk('./anime'))[1]
    animePageButtonInSearch = browser.find_element_by_xpath("//*[@id='app']/div[3]/div/div[2]/div[1]/a").click()

    logFile.write(browser.current_url + "\n")
    newURLs.write(browser.current_url + "\n")

logFile.close()
newURLs.close()
browser.close()



