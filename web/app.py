# https://www.dvt.co.za/news-insights/insights/item/355-restful-web-services-using-python-flask-docker-and-mongodb

# This file will run each script and orchestrate everything
# from Step1 import anilistScrape
# from Step2 import JSON_builder

# scraper = anilistScrape.AnilistScraper()
# scraper.download_anime("./Step1/animeToDownload.txt")
#
# # I want to only call create_anime_json and that function will scrape/download stuff as needed.
# builder = JSON_builder.JsonBuilder()
# builder.create_anime_json_from_file("../SAA.txt")

from flask import Flask, jsonify, request
# from flask_restful import Api, Resource
from flask_restplus import Api, Resource, fields
from flask_cors import CORS
from hashids import Hashids #https://github.com/davidaurelio/hashids-python & https://hashids.org/python/
from bson.json_util import dumps
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# api = Api(app)
hashids = Hashids()

client = MongoClient("mongodb://saadb:27017")
db = client.saa
users = db["Users"]
anime = db["Anime"]

"""
Helper Functions
"""


def userExist(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True


def verifyUser(username, password):
    if not userExist(username):
        return False

    user_hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    if bcrypt.checkpw(password.encode('utf8'), user_hashed_pw):
        return True
    else:
        return False


def getUserMessages(username):
    # get the messages
    return users.find({
        "Username": username,
    })[0]["Messages"]


def getAnime(name):
    # get the messages
    return anime.find_one({
        "name": name,
    })


# https://www.google.com/search?q=making+an+api+flask+and+pymongo&rlz=1C1CHBF_enCA862CA862&oq=making+an+api+flask+and+pymongo&aqs=chrome..69i57.6443j0j4&sourceid=chrome&ie=UTF-8
@app.route("/api/admin/anime", methods=['POST'])
def add_anime():
    # Get posted data from request
    data = request.get_json()
    # data = request.args
    if not data or not data["name"]:
        retJson = {
            "status": 400,
            "msg": "Failed to read data. " + data
        }
        return retJson

    # get data
    name = data["name"]
    description = data["description"]

    # check if anime already exists
    # if animeExist(name):
    #     retJson = {
    #         "status": 301,
    #         "msg": "Invalid Username"
    #     }
    #     return jsonify(retJson)

    # Insert record
    anime.insert({
        "name": name,
        "description": description
    })

    # Return successful result
    retJson = {
        "status": 200,
        "msg": "Anime " + name + " added successfully."
    }
    return jsonify(retJson)

# Using the anime name in the url
@app.route("/api/admin/anime/<name>", methods=['GET'])
def get_anime(name):
    details = getAnime(name)
    if not details:
        retJson = {
            "status": 404,
            "obj": dumps(name + " not found.")
        }
        return retJson

    # Build successful response
    retJson = {
        "status": 200,
        "obj": dumps(details)
    }

    return jsonify(retJson)


# Using a query for the db like: /api/admin/anime?name=myanime
@app.route("/api/admin/anime", methods=['GET'])
def search_anime():
    # Get posted data from request
    # data = request.get_json()

    if 'name' in request.args:
        name = request.args['name']
    else:
        return "Error: No id field provided. Please specify an id."

    details = getAnime(name)
    if not details:
        return name + " not found."

    # Build successful response
    retJson = {
        "status": 200,
        "obj": dumps(details)
    }

    return jsonify(retJson)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

# from app.api import WeatherHistory, WeatherLive, Webcam
# from app.models import init_db
# from flask import Flask, Blueprint
# from flask_cors import CORS

# def create_app(system):
#     app = Flask(__name__)
#
#     # Setup configuration
#     app.config.from_pyfile('../config/{}.cfg'.format(system))
#     app.config["BASE_PATH"] = str(Path(__file__).parents[1])
#     app.logger.setLevel(logging.NOTSET)
#
#     # Setup SQLAlchemy database
#     init_db(app)
#
#     # Setup FLask-RESTful API
#     bp_api = Blueprint('api', __name__, url_prefix='/api')
#     api = Api(bp_api)
#     api.add_resource(WeatherHistory, '/weather/history')
#     api.add_resource(WeatherLive, '/weather/live')
#     api.add_resource(Webcam, '/webcam')
#     app.register_blueprint(bp_api)
#
#     # Configure CORS for REST API
#     CORS(app, resources={r"/api/*": {"origins": "*"}})
#
#     return app


# if __name__ == '__main__':
#     if len(sys.argv) == 1:
#         exit(-1)
#
#     # Setup Flask app
#     app = create_app(sys.argv[1])
#     app.run(host=app.config["HOST"], port=app.config["PORT"])
