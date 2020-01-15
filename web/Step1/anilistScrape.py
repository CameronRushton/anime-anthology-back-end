import os
import re
import requests
# import stat
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdrivermanager import ChromeDriverManager
# from subprocess import check_output


class AnilistScraper:

    # static vars go here

    def __init__(self):
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                  'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                  'Accept-Encoding': 'none',
                  'Accept-Language': 'en-US,en;q=0.8',
                  'Connection': 'keep-alive'
                  }
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument("--window-size=1920,1080")
        bit32, bit64 = ChromeDriverManager().download_and_install()
        # st = os.stat(bit64)
        # os.chmod(bit64, st.st_mode | stat.S_IEXEC)  # Windows only does readonly stuff using os.chmod
        # # For windows
        # print(check_output("icacls " + str(bit64) + " /grant Everyone:F", shell=True).decode())
        # # end for windows
        self.browser = webdriver.Chrome(executable_path=bit64, options=options)  # Replace with .Firefox(), or with the browser of your choice
        self.browser.implicitly_wait(1)  # IMPORTANT: Keep this at least one second to not get flagged as a bot - it's also a hack to let the page JS load

    @staticmethod
    def __create_resource_path__(self, anime_name):
        anime_name = anime_name.lower()
        try:
            sub_dirs = [d for d in os.listdir('../anime') if os.path.isdir(os.path.join('../anime', d))]
        except FileNotFoundError:
            print(f'WARNING: directory \'anime\' does not exist in root folder; creating directory.')
            return f'../anime/{anime_name}/'
        query = anime_name.replace('-', '').lower()
        for directory in sub_dirs:
            dir_name = directory.replace('-', '').lower()
            if dir_name.find(query) != -1:
                return f'../anime/{directory}/'
        return f'../anime/{anime_name}/'

    @staticmethod
    def __get_urls_from_file__(self, file_path):
        urls = []
        # Grab every url with 'http' in it and extract anime name from the url
        file = open(file_path, "r")
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
                    urls.append(word)
        return urls

    @staticmethod
    def __trim_anime_name_from_url__(url):
        # if there is a newline character at the end, remove it
        if "\n" == url[-1]:
            url = url[:-2]
        # if there is a slash at the end of the url, remove it
        if url[len(url) - 1] == '/':
            url = url[:-1]
        k = url.rfind("/")
        return url[k + 1:].lower()

    # anime_name is the name of the anime - used to create a file name
    # resource_path is the root path that the anime is stored in
    # Returns 0 on success; 1 on failure to download, though it may not be an error
    def __download_box_art__(self, anime_name, resource_path):
        # Get the box image source
        try:
            element = self.browser.find_element_by_xpath('//*[@id="app"]/div[3]/div/div[1]/div[2]/div/div[1]/div/img')
        except NoSuchElementException:
            element = self.browser.find_element_by_xpath('//*[@id="app"]/div[3]/div/div[1]/div[2]/div[2]/div[1]/div/img')
        box_art_url = element.get_attribute('src')
        try:
            # Download the image - The following line is no good for websites protecting against DDoS attacks using things like cloudflare
            # urlretrieve(boxArtUrl, resourcePath + "images/" + animeNames[i] + "-box-art.png")
            # Instead, use selenium to download the image by passing the cookies to a requests session, bypassing logins and DDoS protection systems
            # SOURCE: https://stackoverflow.com/questions/49530566/download-an-image-using-selenium-webdriver-in-python
            session = requests.session()
            session.headers.update(self.header)
            for cookie in self.browser.get_cookies():
                c = {cookie['name']: cookie['value']}
                session.cookies.update(c)
            resource = session.get(box_art_url, allow_redirects=True)
            open(resource_path + "images/" + anime_name + "-anilist-box-art.jpg", 'wb').write(resource.content)
            return 0
        except ValueError:
            # Failed to download image (may not exist)
            print("No box image found...")
            return 1

    def __download_cover_art__(self, anime_name, resource_path):
        # Get the background/cover image source
        element = self.browser.find_element_by_xpath('//*[@id="app"]/div[3]/div/div[1]/div[1]')
        raw_cover_image_url = element.get_attribute('style')
        start_index = raw_cover_image_url.find("http")
        ending = raw_cover_image_url.rfind(".jpg")
        if ending < 0:
            ending = raw_cover_image_url.rfind(".png")
        end_index = len(raw_cover_image_url) - ending - 4
        cover_image_url = raw_cover_image_url[start_index:-end_index]
        try:
            # Download the image
            # urlretrieve(coverImageUrl, resourcePath + "images/" + animeNames[i] + "-cover.jpg")
            session = requests.session()
            session.headers.update(self.header)
            for cookie in self.browser.get_cookies():
                c = {cookie['name']: cookie['value']}
                session.cookies.update(c)
            resource = session.get(cover_image_url, allow_redirects=True)
            open(resource_path + "images/" + anime_name + "-anilist-cover.jpg", 'wb').write(resource.content)
            return 0
        except ValueError:
            # Failed to download image (may not exist)
            print("No background found...")
            return 1

    def __download_data__(self, resource_path):
        data_file = open(resource_path + "data.txt", "w+")
        rankings_list = []
        rankings = self.browser.find_elements_by_xpath("//*[@class='rank-text']")
        for item in rankings:
            rankings_list.append(item.text)
            try:
                data_file.write(item.text + "\n")
            except UnicodeEncodeError:
                print()  # Ignore - Probably encountered Japanese text

        data_list = []
        data = self.browser.find_elements_by_xpath("//*[@class='data-set']")
        for item in data:
            data_list.append(item.text)
            try:
                data_file.write(item.text + "\n")
            except UnicodeEncodeError:
                print()  # Ignore - Probably encountered Japanese text

        data_list = []
        data = self.browser.find_elements_by_xpath("//*[@class='data-set data-list']")
        for item in data:
            data_list.append(item.text)
            try:
                data_file.write(item.text + "\n")
            except UnicodeEncodeError:
                print()  # Ignore - Probably encountered Japanese text

        tags_list = []
        tags = self.browser.find_elements_by_xpath("//*[@class='tag']")
        for item in tags:
            tags_list.append(item.text)
            try:
                data_file.write(item.text + "\n")
            except UnicodeEncodeError:
                print()  # Ignore - Probably encountered Japanese text
        data_file.close()
        return 0

    def update_anime_data_in_file(self, file_path):
        self.download_anime(file_path, update_data=True, update_box=False, update_cover=False)

    # file_path is a file with a list of URLs to anilist.co like so:
    # https://anilist.co/anime/5114/Fullmetal-Alchemist/
    # https://anilist.co/anime/105333/Dr-STONE/
    def download_anime(self, file_path, **keyword_params):
        do_download_box_art = True
        do_download_cover_art = True
        do_download_data = True
        update_box_art = False
        update_cover_art = False
        update_data = True

        if 'update_data' in keyword_params:
            update_data = keyword_params['update_data']
        if 'update_box' in keyword_params:
            update_box_art = keyword_params['update_box']
        if 'update_cover' in keyword_params:
            update_cover_art = keyword_params['update_cover']

        urls = self.__get_urls_from_file__(file_path)

        i = 0
        for url in urls:
            anime_name = self.__trim_anime_name_from_url__(url)
            print("Found ", anime_name)
            resource_count = 0
            print("INFO: Downloading image and page data for ", anime_name, "...")
            resource_path = self.__create_resource_path__(anime_name)
            self.browser.get(url)  # Navigate to the page
            try:
                os.makedirs(resource_path + "images/")
            except FileExistsError:
                do_download_data = False
                do_download_cover_art = False
                do_download_box_art = False

            if do_download_box_art or update_box_art:
                result = self.__download_box_art__(anime_name, resource_path)
                if result == 0:
                    resource_count += 1

            if do_download_cover_art or update_cover_art:
                result = self.__download_cover_art__(anime_name, resource_path)
                if result == 0:
                    resource_count += 1

            if do_download_data or update_data:
                result = self.__download_data__(resource_path)
                if result == 0:
                    resource_count += 1

            if resource_count == 3:
                print("Successfully downloaded all resources for ", anime_name)

            print("\n")
            # Cycle to next anime name
            i += 1
        self.browser.close()
