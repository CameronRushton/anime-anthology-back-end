# This file will link each show with it's seasons in a unique list, so the seasons will only be listed once. The list will look like the following:


# [
#     {"group-1": ["bakemonogatari", "kizumonogatari", "nekomonogatari"]},
#     {"group-2": ["boku-no-hero-academia", "boku-no-hero-academia-season-2", "boku-no-hero-academia-season-3"]}
# ]

# Navigate to the page, look for a card that says 'Prequel', if found, navigate to it. Repeat until theres no more prequel cards.
# Add ID to list, then navigate to the card that says 'Sequel' if it exists. Repeat until theres no more sequel cards.
# Look at the next anime URL (with ID) and check to see if it's already in the list. If not, go to the next anime page, else, skip.

# TODO: Support backtracking to multiple 'sequel' cards and potentially 'alternative' cards
# TODO: Wait until the element cards are loaded before trying to click on them
# TODO: Don't make groupings that contain one show
import re
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def create_resource_path(anime_name):
    anime_name = anime_name.lower()
    try:
        sub_dirs = [d for d in os.listdir('../anime') if os.path.isdir(os.path.join('../anime', d))]
    except FileNotFoundError:
        return f'../anime/{anime_name}/'

    query = anime_name.replace('-', '').lower()
    for directory in sub_dirs:
        dir_name = directory.replace('-', '').lower()
        # if dir_name.find(query) != -1:  # If query is found within dir_name
        if dir_name == query:  # If query is dir_name
            return f'../anime/{directory}/'

    return f'../anime/{anime_name}/'


HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive'
          }

DOCUMENT = "../SAA.txt"
CHROMEDRIVER_PATH = "/"  # Chromedriver's expected location
urls = []
animeNames = []

file = open(DOCUMENT, "r")
anime_download_file = open("../Step1/animeToDownload.txt", "a")
print("INFO: Compiling URLs...")
lines = file.readlines()
file.close()
for line in lines:
    for word in line.split(" "):
        if word.startswith("http"):
            # url must match regex
            pattern = "https://anilist[\\S]"  # Don't need to re.compile(pattern) because I'm only using it here
            if not re.match(pattern, word):
                print("ERROR: Invalid URL " + word)
                continue
            # save anime name
            urls.append(word)
            # if there is a newline character at the end, remove it
            if "\n" == word[-1]:
                word = word[:-2]
            # if there is a slash at the end of the url, remove it
            if word[len(word)-1] == '/':
                word = word[:-1]
            k = word.rfind("/")
            word = word[k + 1:].lower()

            animeNames.append(word)
            # print("Found anime " + word)
print("Found ", len(animeNames), " anime.")

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument("--window-size=1920,1080")
browser = webdriver.Chrome(options=options)  # Replace with .Firefox(), or with the browser of your choice
browser.implicitly_wait(1)  # IMPORTANT: Keep this at least one second to not get flagged as a bot - it's also a hack to let the page JS load
i = 0
j = 0
JSON_groups = []
master_anime_id_list = []

for url in urls:
    print("INFO: Looking for seasons of " + animeNames[j] + "...")
    browser.get(url)  # Navigate to the page
    group = {"group-" + str(i): []}
    skip_group = False

    do_quit = False
    while do_quit is False:
        curr_url = browser.current_url
        if curr_url[len(curr_url) - 1] == '/':
            curr_url = curr_url[:-1]
        k = curr_url.rfind("/")
        anime_id = curr_url[k + 1:].lower()
        if anime_id in master_anime_id_list:
            print("Anime already processed.")
            skip_group = True
            break
        try:
            element = browser.find_element_by_xpath('//*[contains(text(),"Prequel")]').click()  # TODO: May need to make this like how the sequel finder is written. Make this one method that takes in either 'Prequel' or 'Sequel' or 'Parent'?
            print("Found Prequel")
        except NoSuchElementException:
            print("Unable to find new prequel element.")
            do_quit = True
        except ElementNotInteractableException:
            element = browser.find_element_by_xpath('//*[contains(text(),"Prequel")]')
            parent_element = element.find_element_by_xpath('../../../a').click()
            print("Found Prequel")
    # time.sleep(1)
    do_quit = False
    while do_quit is False:
        url = browser.current_url
        if url[len(url) - 1] == '/':
            url = url[:-1]
        k = url.rfind("/")
        anime_id = url[k + 1:].lower()
        if anime_id not in master_anime_id_list:
            group["group-"+str(i)].append(anime_id)
            master_anime_id_list.append(anime_id)
            resource_path = create_resource_path(anime_id)
            if not os.path.exists(resource_path):
                print(resource_path, " doesn't exist")
                anime_download_file.write(url + " \n")
            else:
                print(resource_path, " exists")
        else:
            print("Freed self from infinite parent/sequel loop")
            break
        try:
            element = browser.find_element_by_xpath('//*[contains(text(),"Sequel")]')
            # element = WebDriverWait(browser, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[contains(text(),"Sequel")]')))
            # element = browser.find_element_by_xpath('//*[contains(text(),"Sequel")]').click()
            element.click()
        except NoSuchElementException:
            try:
                element = browser.find_element_by_xpath('//*[contains(text(),"Parent")]').click()
            except NoSuchElementException:
                print("Unable to find new Sequel or Parent element.")
                do_quit = True
            except ElementNotInteractableException:
                element = browser.find_element_by_xpath('//*[contains(text(),"Parent")]')
                parent_element = element.find_element_by_xpath('../../../a').click()
        except ElementNotInteractableException:
            element = browser.find_element_by_xpath('//*[contains(text(),"Sequel")]')
            parent_element = element.find_element_by_xpath('../../../a').click()
        # except:
        #     print("Unexpected error: ", sys.exc_info()[0])
        #     raise
        # time.sleep(1)  # IMPORTANT: Keep this at least one second to not get flagged as a bot - it's also a hack to let the page JS load
    if not skip_group:
        JSON_groups.append(group)
        print("Created group ", group)
        i += 1
    j += 1

browser.close()
json_string = json.dumps(JSON_groups, indent=4)
result_file = open("season_data.txt", "w")
result_file.write(json_string)
result_file.close()
anime_download_file.close()
