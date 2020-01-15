# Takes data found in ./anime and creates a JSON payload for the website to use based on the format of ./SAA.txt

# The payload for a single anime looks like this:
# Notes: startDate and endDate could be replaced with releaseDate for movies
# episodes and episodeDuration could be replaced with duration for movies
#
# {
#     id: "hunter-x-hunter-2011",
#     name: "Hunter X Hunter (2011)",
#     boxArt: "assets/anime/hunter-x-hunter-2011/images/hunter-x-hunter-2011-anilist-box-art.jpg",
#     background: "assets/anime/hunter-x-hunter-2011/images/hunter-x-hunter-2011-anilist-cover.jpg",
#     rank: "3",
#     popularity: "25",
#     format: "TV",
#     startDate: "Oct 2, 2011",
#     endDate: "Sep 24, 2014",
#     status: "Finished",
#     episodeDuration: "23 mins",
#     episodes: "148",
#     season: "Fall 2011",
#     score: "90",
#     source: "manga",
#     studios: ["MADHOUSE"],
#     producers: ["VAP"],
#     synonyms: ["HxH (2011)"],
#     genres: ["Action", "Adventure", "Fantasy", "Fantasy", "Fantasy", "Fantasy", "Fantasy", "Fantasy", "Fantasy",
#              "Fantasy", "Fantasy", "Fantasy", "Fantasy"],
#     customTags: [{name: "Cultivation", percent: "91"}, {name: "Shounen", percent: "90"}],
#     description: "This anime is good.",
#     watch: {netflix: "urlToNetflix"}
# }
import pathlib
import os
import re
from PIL import Image
import json


class JsonBuilder:

    def __init__(self):
        self.DEBUG = True

    def get_data_from_file(self, dataFile):
        lines = dataFile.readlines()
        newLines = []
        for line in lines:
            newLines.append(line.replace("\n", ""))

        return newLines

    def parse_anime_folder(self, anime_folder):
        # Things that get populated
        dataFilePaths = []
        boxArtPaths = []
        backgroundPaths = []
        animeNames = []
        if not anime_folder:
            anime_folder = "anime\\"
        result = [animeNames, boxArtPaths, backgroundPaths, dataFilePaths]

        # Control variables
        newAnimeName = ""
        data = False
        box_art = False
        cover = False
        cover_width = 0
        cover_height = 0
        box_art_width = 0
        box_art_height = 0

        for path, dirs, files in os.walk(anime_folder):
            for name in files:
                animeName = pathlib.PurePath(path, name).parts[1]  # Finds .txt, .png (box) then .jpg (cover)
                fileType = str(pathlib.PurePath(path, name))[-3:]
                fileName = name[:-4]
                if newAnimeName != animeName and newAnimeName != "":
                    # We have moved to another anime
                    data = False
                    box_art = False
                    cover = False
                    cover_width = 0
                    cover_height = 0
                    box_art_width = 0
                    box_art_height = 0
                    animeNames.append(str(newAnimeName))
                    # skip over any array elems to keep all data in same column (self balance)
                    if len(boxArtPaths) < len(backgroundPaths) or len(boxArtPaths) < len(dataFilePaths):
                        boxArtPaths.append("")
                        print("Missing box art for ", newAnimeName)
                    if len(backgroundPaths) < len(boxArtPaths) or len(backgroundPaths) < len(dataFilePaths):
                        backgroundPaths.append("") # TODO: Put default cover and box art path here and above
                        print("Missing cover art for ", newAnimeName)
                    if len(dataFilePaths) < len(boxArtPaths) or len(dataFilePaths) < len(backgroundPaths):
                        dataFilePaths.append("")
                        print("Missing data for ", newAnimeName)
                newAnimeName = animeName

                if "txt" in fileType and not data:
                    dataFilePaths.append(pathlib.PurePath(path, name))
                    data = True
                elif fileType == "jpg" or fileType == "png":
                    img = Image.open(str(pathlib.PurePath(path, name)))
                    width, height = img.size
                    if "cover" in fileName:
                        if width * height > cover_width * cover_height:
                            if cover:  # If a cover has already been added, remove the previous cover
                                backgroundPaths.pop()
                            backgroundPaths.append(pathlib.PurePath(path, name))
                            cover_width = width
                            cover_height = height
                        cover = True
                    else:
                        if "box-art" in fileName:
                            if width * height > box_art_width * box_art_height:
                                if box_art:  # If a box art has already been added, remove the previous box art
                                    boxArtPaths.pop()
                                boxArtPaths.append(pathlib.PurePath(path, name))
                                box_art_width = width
                                box_art_height = height
                            box_art = True
        animeNames.append(str(newAnimeName))
        return result


    def findDataItem(self, key, data):
        for line in data:
            if line.lower() == key.lower():
                return data[data.index(line) + 1]  # return the next line
        # Didnt find it
        return ""


    def findAllItems(self, key, stoppingKeys, data):
        items = []
        start = False
        for line in data:
            for stopKey in stoppingKeys:
                if line.lower() == stopKey.lower():
                    start = False
            if start:
                items.append(line)
            if line.lower() == key.lower():
                start = True

        return items


    def findAllCustomTags(self, data):
        # Work my way backwards from the bottom of the data file and pick out every other line that has a % sign until it doesn't have one
        tags = []
        index = len(data) - 1  # subtracting 1 because arrays start at 0
        while '%' in data[index]:
            customTag = {}
            if '%' in data[index]:
                customTag["name"] = data[index - 1]
                customTag["percent"] = data[index][:-1]
                tags.append(customTag)
            index -= 2
        return tags


    def isInt(self, item):
        try:
            int(item)
        except ValueError:
            return False
        return True


    def determine_popularity_and_rank(self, data):
        return_data = []

        for i in range(0, 2):
            value = data[i].split(' ')
            correct_format = re.match(r'.*([1-3][0-9]{3})', data[i])

            if data[i] == '' or (data[i].find("All Time") == -1 and correct_format is None):
                return_data.append('')
            else:
                return_data.append(value[0][1:])

        if data[1].find("All Time") != -1:
            return_data.append("All Time")
        else:
            pieces = data[1].split(' ')
            return_data.append(pieces[len(pieces)-1])

        return return_data


    def checkBackgroundPath(self, path):
        if path == '':
            return path
        else:
            return "assets/" + str(path).replace("\\", "/").lower()

    # Creates a JSON object containing all the necessary data of an anime given the necessary resource paths.
    def create_single_anime_json(self, data_file_path, box_art_path, background_path, anime_name, custom_description):
        data_file = open(data_file_path, "r")
        data = self.get_data_from_file(data_file)
        data_file.close()
        pop_values = self.determine_popularity_and_rank(data)
        anime_json = {
            "id": anime_name.lower(),
            "name": self.findDataItem("Romaji", data),
            "boxArt": "assets/" + str(box_art_path).replace("\\", "/").lower(),
            "background": self.checkBackgroundPath(background_path),
            "rank": pop_values[0],
            "popularity": pop_values[1],
            "popTime": pop_values[2],
            "format": self.findDataItem("Format", data),
            "status": self.findDataItem("Status", data),
            "season": self.findDataItem("Season", data),
            "score": self.findDataItem("Mean Score", data)[:-1],
            "source": self.findDataItem("Source", data),
            "studios": self.findAllItems("Studios", ["Producers", "Genres"], data),
            "producers": self.findAllItems("Producers", ["Genres"], data),
            "synonyms": [self.findDataItem("English", data), self.findDataItem("Synonyms", data)],
            # TODO: Should be multiple synonyms but idk what the stopping key would be since next up is custom tags
            "genres": self.findDataItem("Genres", data).split(", "),
            "customTags": self.findAllCustomTags(data),
            "description": custom_description,
            "watch": {}  # JSON used for appending netflix attributes
        }
        is_tv_or_movie = self.findDataItem("Format", data)
        if is_tv_or_movie == "TV":
            anime_json["startDate"] = self.findDataItem("Start Date", data)
            anime_json["endDate"] = self.findDataItem("End Date", data)
            anime_json["episodes"] = self.findDataItem("Episodes", data)
            anime_json["episodeDuration"] = self.findDataItem("Episode Duration", data)
        elif is_tv_or_movie == "Movie":
            anime_json["releaseDate"] = self.findDataItem("Release Date", data)
            anime_json["duration"] = self.findDataItem("Duration", data)

        # Consult the netflix table for possible viewing on netflix
        with open('netflix_table.json', 'r') as f:
            anime_links_dict = json.load(f)
        for show in anime_links_dict:
            if anime_name.lower() == show['name']:
                watch_json = anime_json['watch']
                watch_json['netflix'] = show['netflix']
        return anime_json


    def createJSON(self, index, levelNumber, arrayToAppendTo, dataFilePaths, boxArtPaths, backgroundPaths, animeNames, descriptions):
        data_file = dataFilePaths[index]
        box_art_path = boxArtPaths[index]
        background_path = backgroundPaths[index]
        anime_name = animeNames[index]
        custom_description = descriptions[index]

        anime_json = self.create_single_anime_json(data_file, box_art_path, background_path, anime_name, custom_description)

        arrayToAppendTo[int(levelNumber) - 1].append(anime_json)

    def create_anime_json_from_file(self, file_path_with_urls_and_descriptions):
        anthology = open(file_path_with_urls_and_descriptions, "r")
        anime_data = self.parse_anime_folder(anthology)
        animeNames = anime_data[0]
        boxArtPaths = anime_data[1]
        backgroundPaths = anime_data[2]
        dataFilePaths = anime_data[3]

        animeDLFile = open("../Step1/animeToDownload.txt", "a")  # Place to put anime URLs found in SAA.txt when no data was found (scraper runs off this file)
        lines = self.get_data_from_file(anthology)
        anthology.close()
        descriptions = {}
        start = False
        levelNumber = ""
        JSONLevels = []
        for line in lines:
            if re.match("[0-9]+ {", line):
                levelNumber = line[:-2]  # Strip off ' {' when line = '1 {' or '20 {'
                start = True
                JSONLevels.append([])
                print("Starting to collect anime for level ", levelNumber)
                continue
            elif line == "}" and start:
                print("Finished collecting anime for level ", levelNumber)
                start = False
            if start:
                # The goal of the following is to grab the anime name and the description, then look for an anime called <found anime name> in animeNames
                # and add the description to the same index in the descriptions map. Once the description is acquired, create the JSON.
                for word in line.split(" "):
                    if word.startswith("http"):
                        url = word
                        # url must match regex
                        pattern = "https://anilist.co/anime/[\\S]"  # Don't need to re.compile(pattern) because I'm only using it here
                        if not re.match(pattern, url):
                            print("ERROR: Invalid URL " + url)
                            continue
                        # save anime name
                        if word[len(word) - 1] == '/':  # If last char is a '/', then remove it
                            word = word[:-1]
                        k = word.rfind("/")
                        word = word[k + 1:]  # Strip left half of url, leaving the name
                        print("Looking for '", word, "'.")
                        # Scroll through each of the anime names until we find the one we're looking for. Use this index for all the data.
                        for i in range(0, len(animeNames)):
                            if animeNames[i].lower() == word.lower():  # TODO: Replace me with a more robust string pattern matching system dragon-maid should still equal dragonMaid for instance.
                                # print("DEBUG: Found at index " + str(i))
                                # find first space in line to remove the url (Assuming that the description is all on the same line)
                                startPoint = line.find(" ") + 1
                                descriptions[i] = line[startPoint:]

                                self.createJSON(i, levelNumber, JSONLevels, dataFilePaths, boxArtPaths, backgroundPaths, animeNames, descriptions)
                                print(word, " found and description added.")
                                break
                            elif i == len(animeNames) - 1:
                                print("WARN: Failed to find resources for " + word + "\nRun the scraper to download the missing anime.")
                                # add the url to the list to download
                                animeDLFile.write(url + " \n")
        print("Finished")
        json_string = json.dumps(JSONLevels, indent=4)
        result_file = open("anime_JSON.txt", "w")
        result_file.write(json_string)
        result_file.close()
        animeDLFile.close()
        return 0

# Do the same thing as above but for currently watching
#     start = False
#     JSONcurrentlyWatching = [[]]
#     for line in lines:
#         # if line == str(levelNumber) + " {":
#         if line == "c {":
#             start = True
#             continue
#         elif line == "}" and start:
#             start = False
#         if start:
#             for word in line.split(" "):
#                 if word.startswith("http"):
#                     url = word
#                     # url must match regex
#                     pattern = "https://anilist.co/anime/[\\S]"  # Don't need to re.compile(pattern) because I'm only using it here
#                     if not re.match(pattern, url):
#                         print("ERROR: Invalid URL " + url)
#                         continue
#                     # save anime name
#                     if word[len(word) - 1] == '/':  # If last char is a '/', then remove it
#                         word = word[:-1]
#                     k = word.rfind("/")
#                     word = word[k + 1:]  # Strip left half of url, leaving the name
#                     print("Looking for '" + word + "'.")
#                     # Scroll through each of the anime names until we find the one we're looking for. Use this index for all the data.
#                     for i in range(0, len(animeNames)):
#                         if animeNames[i].lower() == word.lower(): # TODO: Replace me with a more robust string pattern matching system dragon-maid should still equal dragonMaid for instance.
#                             # print("DEBUG: Found at index " + str(i))
#                             # find first space in line to remove the url (Assuming that the description is all on the same line)
#                             startPoint = line.find(" ") + 1
#                             descriptions[i] = line[startPoint:]
#
#                             createJSON(i, 1, JSONcurrentlyWatching)
#                             logger(word + " found and description added.")
#                             break
#                         elif i == len(animeNames) - 1:
#                             print(
#                                 "WARN: Failed to find resources for " + word + "\nRun the scraper to download the missing anime.")
#                             # add the url to the list to download
#                             animeDLFile.write(url + " \n")


    # result_file = open("currently_watching_JSON.txt", "w")
    # json_string = json.dumps(JSONcurrentlyWatching, indent=4)
    # result_file.write(json_string)
