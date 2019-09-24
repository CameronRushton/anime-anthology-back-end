# This file will run each script and orchestrate everything
from Step1 import anilistScrape

scraper = anilistScrape.AnilistScraper()
scraper.download_anime("./Step1/animeToDownload.txt")

