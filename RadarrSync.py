import json
import logging
import os
import sys

import requests

VER = "1.3.0"

########################################################################################################################
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
)

file_handler = logging.FileHandler("./Output.txt")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
########################################################################################################################
logger.debug("RadarSync Version {}".format(VER))

# ENV VARS
radarr_url = os.environ["RADARR_URL"]
radarr_key = os.environ["RADARR_KEY"]
radarr_folder = os.environ["RADARR_FOLDER"]
radarr4k_url = os.environ["RADARR4K_URL"]
radarr4k_key = os.environ["RADARR4K_KEY"]
radarr4k_folder = os.environ["RADARR4K_FOLDER"]
quality_profile_id = os.environ["PROFILE_ID"]


# Sync with normal server
radarr_session = requests.Session()
radarr_session.trust_env = False
radarr_movies = radarr_session.get(
    "{0}/api/movie?apikey={1}".format(radarr_url, radarr_key)
)
if radarr_movies.status_code != 200:
    logger.error("Radarr server error - response {}".format(radarr_movies.status_code))
    sys.exit(0)

# Sync with 4k server
logger.debug("syncing with 4k server")
radarr4k_session = requests.Session()
radarr4k_session.trust_env = False
radarr4k_movies = radarr4k_session.get(
    "{0}/api/movie?apikey={1}".format(radarr4k_url, radarr4k_key)
)
if radarr4k_movies.status_code != 200:
    logger.error(
        "4K Radarr server error - response {}".format(radarr4k_movies.status_code)
    )
    sys.exit(0)

# build a list of movied IDs already in the sync server, this is used later to prevent readding a movie that already
# exists.
# TODO refactor variable names to make it clear this builds list of existing not list of movies to add
# TODO #11 add reconciliation to remove movies that have been deleted from source server

radarr4k_movie_ids = []
for radarr4k_movie in radarr4k_movies.json():
    radarr4k_movie_ids.append(radarr4k_movie["tmdbId"])
    # logger.debug('found movie to be added')

radarr4k_movies_to_search = []
for radarr_movie in radarr_movies.json():
    if radarr_movie["profileId"] == int(quality_profile_id):
        if radarr_movie["tmdbId"] not in radarr4k_movie_ids:
            logging.debug("title: {0}".format(radarr_movie["title"]))
            logging.debug("qualityProfileId: {0}".format(radarr_movie["qualityProfileId"]))
            logging.debug("titleSlug: {0}".format(radarr_movie["titleSlug"]))
            images = radarr_movie["images"]
            for image in images:
                image["url"] = "{0}{1}".format(radarr_url, image["url"])
                logging.debug(image["url"])
            logging.debug("tmdbId: {0}".format(radarr_movie["tmdbId"]))
            logging.debug("path: {0}".format(radarr_movie["path"]))
            logging.debug("monitored: {0}".format(radarr_movie["monitored"]))

            new_path = str(radarr_movie["path"]).replace(radarr_folder, radarr4k_folder)

            payload = {
                "title": radarr_movie["title"],
                "qualityProfileId": radarr_movie["qualityProfileId"],
                "titleSlug": radarr_movie["titleSlug"],
                "tmdbId": radarr_movie["tmdbId"],
                "path": new_path,
                "monitored": radarr_movie["monitored"],
                "images": images,
                "profileId": radarr_movie["profileId"],
                "minimumAvailability": radarr_movie["minimumAvailability"],
            }

            radarr4k_add_movie_request = radarr4k_session.post(
                "{0}/api/movie?apikey={1}".format(radarr4k_url, radarr4k_key),
                data=json.dumps(payload),
            )
            radarr4k_movies_to_search.append(int(radarr4k_add_movie_request.json()["id"]))
            logger.info("adding {0} to server".format(radarr_movie["title"]))
        else:
            logging.debug("{0} already in library".format(radarr_movie["title"]))
    else:
        logging.debug(
            "Skipping {0}, wanted profile: {1} found profile: {2}".format(
                radarr_movie["title"], quality_profile_id, radarr_movie["profileId"]
            )
        )


if len(radarr4k_movies_to_search):
    payload = {"name": "MoviesSearch", "movieIds": radarr4k_movies_to_search}
    radarr4k_session.post(
        "{0}/api/command?apikey={1}".format(radarr4k_url, radarr4k_key),
        data=json.dumps(payload),
    )
