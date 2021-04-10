import unittest
import sys
import time
import requests

from threading import Thread

sys.path.insert(1, "../")
sys.path.insert(2, "../../team22-common-services-backend")
sys.path.insert(2, "../../common-services-backend")
from mongoutils import initMongoFromCloud
from http.server import HTTPServer
from server import SimpleHTTPRequestHandler

# Global variables used in the unittest

port = 4001

##### READ HERE, On bitbucket, this data is already on mongo db because mongodb 
# inserted a user when unit testing common services backend. You can use this data with the token once it's fetched
user_data_payload = {
    "_id": "1515646454",
    "firstName": "test_firstName",
    "lastName": "test_lastName",
    "phoneNumber": "test_phoneNumber",
    "email": "test@test.com",
    "username": "test_username",
    "password": "test_password"
}


# This is a demo that unittests the python endpoints. Beware, order matters in this case since we are
# dealing witht the database, might vary depending on how you're tesing

# TEST METHOD ORDER STRUCTURE $
# def test_(number here)_(subject here):

class ServerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up server
        cls._server = HTTPServer(('', port), SimpleHTTPRequestHandler)
        cls._server_thread = Thread(None, cls._server.serve_forever)
        cls._server_thread.start()

    # Add token to user_data_payload. Reasons being because server.py will not allow any data unless if a token is provided via cookies
    def test_1_get_token_from_db_and_test_(self):
        client = initMongoFromCloud("supply")
        db = client["team22_supply"]
        collection = db.FleetManager
        fleet_manager = collection.find_one({ "_id": user_data_payload["_id"]})
        token = fleet_manager["token"]
        self.assertIsNotNone(token, "Token was found")
        user_data_payload["token"] = token

    def test_2_add_fleet_to_fleet_manager_request(self):
        payload = {
            # json data to send
        }
        token = user_data_payload["token"]
        cookies = {
            'token': token
         }
        response = requests.post(f"http://localhost:{port}/fleet", cookies=cookies, json=payload, timeout=5)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        # tear down server
        cls._server.shutdown()
        cls._server_thread.join()

if __name__ == '__main__':
    unittest.main()
