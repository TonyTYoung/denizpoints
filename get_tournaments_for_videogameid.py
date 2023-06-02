import csv
from datetime import datetime
import json
import requests
import time
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import Timeout, RequestException
from requests.structures import CaseInsensitiveDict
import sys, os
from os import walk
import logging

logging.basicConfig(filename="log.log", format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger("get_tournaments_for_videogameid")

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Prepare request to start.gg
url = "https://api.start.gg/gql/alpha"
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
with open("auth_token.txt") as auth_token_file:
    auth_token = auth_token_file.read()
headers["Authorization"] = "Bearer " + auth_token
headers["Content-Type"] = "application/json"

# Define input/output locations
output_path = os.path.join(application_path, "output")
if not os.path.exists(output_path):
    os.makedirs(output_path)

with open("get_tournaments_for_videogameid_query.txt") as query_file:
    query = query_file.read()

videogameid_timestamp_pairs = []
with open("videogameid_timestamp.txt") as slug_file:
    for line in slug_file:
        videogameid_timestamp_pairs.append(line.strip().split(","))

try:
    with open(os.path.join(output_path, "output.csv"), mode="w", encoding="utf-8", newline="") as data_file:
        csv_writer = csv.writer(data_file)

        for videogameid_timestamp in videogameid_timestamp_pairs:
            variables = {
                "page": "1",
                "perPage": 100,
            }
            variables["videogameId"] = videogameid_timestamp[0]
            variables["afterDate"] = int(videogameid_timestamp[1])
            make_request = True

            while make_request:
                try:
                    s = requests.Session()
                    retries = Retry(total=5,
                                    backoff_factor=0.1,
                                    status_forcelist=[ 500, 502, 503, 504 ])
                    s.mount("https://", HTTPAdapter(max_retries=retries))
                    r = s.post(url, headers=headers, json={"operationName": "TournamentsByVideogame", "query": query, "variables": variables})
                    if r.status_code == 200:
                        data = json.loads(r.text)
                        nodes = data["data"]["tournaments"]["nodes"]
                        tournament_count = 0
                        for tournament in nodes:
                            tournament_count += 1
                            events = tournament["events"]
                            for event in events:
                                row = []
                                tournament_slug = tournament["slug"][len("tournament/"):]
                                row.append(tournament_slug)
                                row.append(variables["videogameId"])
                                if event["state"] == "COMPLETED":
                                    entrant_count = event["numEntrants"]
                                    if entrant_count > 0:
                                        row.append(event["slug"][len("tournament/" + tournament_slug + "/event/"):])
                                        row.append(entrant_count)
                                        row.append(tournament["city"])
                                        row.append(tournament["addrState"])
                                        row.append(tournament["countryCode"])
                                        row.append(event["isOnline"])
                                        csv_writer.writerow(row)
                        make_request = tournament_count > 0
                        if make_request:
                            variables["page"] = str(int(variables["page"]) + 1)
                            time.sleep(1)
                    else:
                        make_request = False
                        logger.error("Unable to pull data from source for videogameId %s at %s", variables["videogameId"], variables["afterDate"])
                        logger.error(r.status_code)
                except Timeout:
                    make_request = False
                    logger.error("Request timeout for videogameId %s at %s", variables["videogameId"], variables["afterDate"])
                except RequestException:
                    make_request = False
                    logger.exception("RequestException for videogameId %s at %s", variables["videogameId"], variables["afterDate"])
except Exception:
    logger.exception("Unable to process file")
