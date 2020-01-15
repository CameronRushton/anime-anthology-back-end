# anime-anthology-back-end

Prerequisites:
Docker

If running without Docker:
install and run mongodb https://docs.mongodb.com/v3.4/tutorial/install-mongodb-on-windows/
chromedriver.exe for your version of chrome
python 3.6+

This is the Flask-Mongo backend for the anime anthology.

run 'docker-compose build'
'docker-compose up'
to start mongodb and web app

to log into the mongo db,
'docker ps'
copy the container ID
'docker exec -it <containerID> bash'
'mongo'
You can now issue mongo commands to see the db(s)
See the following link for more info
https://docs.mongodb.com/manual/reference/mongo-shell/

Quick reference:
db -> shows all dbs
use <db name> -> switches db
show collections -> shows collections
db.<collection name>.find() -> shows all entries in collection (table)

MAL DB snapshot from 2018, the anilist api, scraping tool integration and REST endpoints are still under development
