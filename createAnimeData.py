import os
import json
from shutil import copy


DEBUG = True

def logger(log):
    if DEBUG:
        print(log)


def get_data_from_file(dataFile):
    lines = dataFile.readlines()
    newLines = []
    for line in lines:
        newLines.append(line.replace("\n", ""))

    return newLines


# animeJSON = open("anime_JSON.txt", "r")
with open('anime_JSON.txt') as json_file:
    data = json.load(json_file)

# JSON should be the same structure as the current anime/ directory
boxArtPaths = []
coverArtPaths = []
names = []
for level in data:
    for anime in level:
        boxArtPaths.append(anime['boxArt'][7:])  # remove 'assets' from assets/anime/path...
        coverArtPaths.append(anime['background'][7:])
        names.append(anime['id'])

for path, dirs, files in os.walk("anime\\"):
    for name in files:
        source = path + "\\" + name
        source = source.replace("\\", "/")
        for i, boxArtPath in enumerate(boxArtPaths):
            print("Copying " + source + " -> " + boxArtPath)
            if source == boxArtPath:
                # os.makedirs("uploadToWebsite/" + names[] +"/images")
                print("Copying " + source + " -> " + boxArtPath)
                os.makedirs("uploadToWebsite/" + names[i] + "/images/")
                copy(boxArtPath, "uploadToWebsite/" + names[i] + "/images/")
        for i, coverArtPath in enumerate(coverArtPaths):
            if source == coverArtPath:
                print("Copying " + source + " -> " + coverArtPath)
                copy(coverArtPath, "uploadToWebsite/" + names[i] + "/images/")
