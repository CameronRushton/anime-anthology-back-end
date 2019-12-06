# anime-anthology-back-end

Usage: 

Prerequisites:
install and run mongodb https://docs.mongodb.com/v3.4/tutorial/install-mongodb-on-windows/
chromedriver.exe for your version of chrome
python 3.6+

1. Create a text file called anime.txt
2. Fill anime.txt with URLs to anilist.co's anime pages. Denote levels 1 to 5 using the following syntax:

1 {<br>
https://anilist.co/anime/21520/Koyomimonogatari/  My mandatory, custom description <br>
https://anilist.co/anime/21745/Owarimonogatari-Ge/ My mandatory, custom description <br>
} <br>
2 { <br>
https://anilist.co/anime/103572/5Toubun-no-Hanayome/ My mandatory, custom description <br>
}


3. Run anilistScrape.py and wait for all files to be created in the new anime/ directory

4. Run JSON_builder.py to create a JSON based on the structure of anime/ and then copy the contents of the created file called 
'anime_JSON.txt' to the anime-anthology repo in src/managers/anime-manager
  
5. Run createAnimeData.py to copy the website's resources from the anime/ folder to a new folder called uploadToWebsite/

6. Copy uploadToWebsite/ to anime-anthology repo /assets and rename uploadToWebsite/ to anime/

7. Run the website using au run --watch (see anime-anthology repo for details)
