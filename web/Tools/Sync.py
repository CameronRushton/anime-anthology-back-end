# Sync the IDs of all anime using the submitted URL in the anime file (SAA.txt) as the correct ID. The sync is between a URl in the anime file,
# https://www.website.com/12345/this-is-my-anime-id
# the name of the folder in anime/
# anime/this-is-my-anime-id/
# and the resulting JSON generated after running JSON_builder.py
import os
import re
import pathlib
# Get all IDs in the anime file
animeNames = []
availableResourcesAnimeNames = []
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-gpu')
logFile = open("syncLogs.txt", "w+")

DOCUMENT = "SAA.txt"
# Get all urls in SAA.txt
# Grab every url with 'http' in it and extract anime name from the url
file = open(DOCUMENT, "r")
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
            # if there is a newline character at the end, remove it
            if "\n" == word[-1]:
                word = word[:-2]
            # if there is a slash at the end of the url, remove it
            if (word[len(word) - 1] == '/'):
                word = word[:-1]
            k = word.rfind("/")
            word = word[k + 1:]
            animeNames.append(word)

# Go through file names
newAnimeName = ""
isOK = False
logFile.write("Anime IDs not found in your anime folder: (please change the files to the correct name defined in your anthology; case doesn't matter or download them with the scraper).\n")
logFile.write("Please rebuild your JSON with the changes!\n\n")
for path, dirs, files in os.walk("anime\\"):
    for name in files:
        animeName = pathlib.PurePath(path, name).parts[1]  # Finds .txt, .png (box) then .jpg (cover)
        # fileName = name[:-4]
        if newAnimeName != animeName and newAnimeName != "":
            # We have moved to another anime
            availableResourcesAnimeNames.append(newAnimeName)
        newAnimeName = animeName

for animeIDfromFile in animeNames:
    for animeIDfromFolder in availableResourcesAnimeNames:
        if animeIDfromFolder.lower() == animeIDfromFile.lower():
            isOK = True
            break
    if not isOK:
        logFile.write(animeIDfromFile + "\n")
    isOK = False


logFile.close()
