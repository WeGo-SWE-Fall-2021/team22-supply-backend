import unittest
import sys
import time
import requests
import json
import jwt

sys.path.insert(1, sys.path[0] + "/../")

from threading import Thread
from utils.mongoutils import initMongoFromCloud
from http.server import HTTPServer
from server import SimpleHTTPRequestHandler
from dispatch import Dispatch
from dotenv import load_dotenv
from os import getenv


load_dotenv()

# Global variables used in the unittest
port = 4001

# Defined data
fleet_manager_data_one = {
    "_id": "1515646454",
    "firstName": "test_firstName",
    "lastName": "test_lastName",
    "phoneNumber": "test_phoneNumber",
    "email": "test@test.com",
    "username": "test_username",
    "password": "test_password",
    "dockAddress": "addy",
    "dockNumber": "number", 
    "fleetIds": ["123"]
}

fleet_one = {
    "_id": "123",
    "fleetManagerId": fleet_manager_data_one["_id"],
    "totalVehicles": 1,
    "pluginIds": ["1", "2"],
    "vType":"food"
}

vehicle_one = {
    "_id": "HUSERFEF-R3242-3453535-SFSFSFER242Y",
    "fleetId": fleet_one["_id"],
    'status' : 'ready',
    "vType": "food",
    "location": "-97.731010,30.283930",
    "dock": "uhhh fix me pls",
    "lastHeartbeat": "1234892919.655932"
}

vehicle_two = {
    "_id": "HUSERFEF-R3242-3453535-SFSFSFER2420",
    "fleetId": fleet_one["_id"],
    'status' : 'ready',
    "vType": "food",
    "location": "-97.731010,30.283930",
    "dock": "uhhh fix me pls",
    "lastHeartbeat": "1234892919.655932"
}
vehicle_three = {
    "_id": "HUSERFEF-R3242-3453535-SFSFSFER243Z",
    "fleetId": fleet_one["_id"],
    'status' : 'busy',
    "vType": "food",
    "location": "-97.731010,30.283930",
    "dock": "uhhh fix me pls",
    "lastHeartbeat": "1234892919.655932"
}
dispatch_one = {
    "_id": "454",
    "orderId": "123",
    "vehicleId": vehicle_one["_id"],
    "status": "in progress",
    "orderDestination": "3001 S Congress Ave, Austin, TX 78704"
}
dispatch_two = {
    "_id": "455",
    "orderId": "124",
    "vehicleId": vehicle_two["_id"],
    "status": "processing",
    "orderDestination": "3001 S Congress Ave, Austin, TX 78704"
}

dispatch_three = {
    "_id": "456",
    "orderId": "124",
    "vehicleId": vehicle_three["_id"],
    "status": "in progress",
    "orderDestination": "3001 S Congress Ave, Austin, TX 78704"
}

client = initMongoFromCloud("supply")
db = client["team22_supply"]

# This is a demo that unittests the python endpoints. Beware, order matters in this case since we are
# dealing with the database, might vary depending on how you're tesing

# TEST METHOD ORDER STRUCTURE $
# def test_(number here)_(subject here):

class ServerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up server
        cls._server = HTTPServer(('', port), SimpleHTTPRequestHandler)
        cls._server_thread = Thread(None, cls._server.serve_forever)
        cls._server_thread.start()

        db.FleetManager.insert_one(fleet_manager_data_one)
        db.Fleet.insert_one(fleet_one)
        db.Dispatch.insert_one(dispatch_one)
        db.Dispatch.insert_one(dispatch_two)
        db.Dispatch.insert_one(dispatch_three)
        db.Vehicle.insert_one(vehicle_one)
        db.Vehicle.insert_one(vehicle_two)
        db.Vehicle.insert_one(vehicle_three)
    def test_1_add_fleet_to_fleet_manager_1_request(self):
        payload = {
            "totalVehicles": 0,
            "pluginIds": ["3", "4"],
            "vType": "medicine"
        }

        # Generate a jwt token
        token_secret = getenv("TOKEN_SECRET")
        token = jwt.encode({ 
            "user_id": fleet_manager_data_one["_id"]
            }, token_secret, algorithm="HS256")
        cookies = {
            'token': token
         }
        response = requests.post(f"http://localhost:{port}/fleet", cookies=cookies, json=payload, timeout=5)
        fleetCount = db.Fleet.count()
        fleetManager1 = db.FleetManager.find_one({"_id": "1515646454"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.text)["fleetIds"], fleetManager1.get("fleetIds"))
        self.assertEqual(fleetCount, 2)


    def test_1_add_vehicle_to_fleet_1_request(self):
        payload = {
            'status': 'ready',
            "vType": "food",
            "dock": "dock address",
        }

        # Generate a jwt token
        token_secret = getenv("TOKEN_SECRET")
        token = jwt.encode({ 
            "user_id": fleet_manager_data_one["_id"]
            }, token_secret, algorithm="HS256")
        cookies = {
            'token': token
         }
        response = requests.post(f"http://localhost:{port}/vehicle", cookies=cookies, json=payload, timeout=5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.text)["totalVehicles"], 2)
        fleet = db.Fleet.find_one({"_id": "123", "vType": "food"})
        self.assertIsNotNone(fleet)
        self.assertEqual(fleet["totalVehicles"], 2)

    def test_vehicle_1_location_dispatch_1(self):
        dispatch = Dispatch(dispatch_one)
        location = dispatch.getVehicleLocation(client)
        self.assertEqual(location, vehicle_one["location"])

    def test_dispatch_one_get_eta_1(self):
        dispatch = Dispatch(dispatch_one)
        dir_response = dispatch.requestDirections(client)
        expected_eta = 11
        # print(dir_response)
        actual_eta = Dispatch.getETAFromDirectionsResponse(dir_response)
        self.assertEqual(actual_eta, expected_eta)

    def test_dispatch_one_get_routes_1(self):
        dispatch = Dispatch(dispatch_one)
        dir_response = dispatch.requestDirections(client)
        expected_routes = type([[]])
        # print(dir_response)
        actual_routes = type(Dispatch.getRouteCoordinates(dir_response))
        self.assertEqual(actual_routes, expected_routes)

    def test_order_create_new_dispatch_with_vehicle_request(self):
        payload = {
            "orderId": "8965",
            "orderDestination": "Austin, TX",
            "vehicleType": "food"
        }
        response = requests.post(f"http://localhost:{port}/dispatch", json=payload, timeout=5)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.text)["dispatch_status"], "processing")
        self.assertEqual(json.loads(response.text)["vehicleId"], "HUSERFEF-R3242-3453535-SFSFSFER242Y")

    def test_order_status_1(self):
        payload = {
            "orderId": "123"
        }
        client = initMongoFromCloud("supply")
        db = client["team22_supply"]
        dispatch = Dispatch(dispatch_one)
        geocode_response = dispatch.requestForwardGeocoding()
        directions_response = dispatch.requestDirections(client)
        response = requests.get(f"http://localhost:{port}/status?orderId=123")
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(json.loads(response.text)['orderId'], "123")
        self.assertEqual(json.loads(response.text)['order_status'], "in progress")
        self.assertEqual(json.loads(response.text)["vehicle_starting_coordinate"], dispatch.getVehicleLocation(client))
        self.assertEqual(json.loads(response.text)["destination_coordinate"], Dispatch.getCoordinateFromGeocodeResponse(geocode_response))
        self.assertEqual(json.loads(response.text)["geometry"], Dispatch.getGeometry(directions_response))

    def test_VSIM_getAllVehicles_GET_Endpoint(self):
        vehicleResponse = requests.get(f'http://localhost:{port}/getAllVehicles')
        self.assertEqual(vehicleResponse.status_code, 200)
        vehicles = json.loads(vehicleResponse.text)
        self.assertTrue(vehicle_one in vehicles)

    def test_1_returnVehicle_GET(self):
        # Generate a jwt token
        token_secret = getenv("TOKEN_SECRET")
        token = jwt.encode({ 
            "user_id": fleet_manager_data_one["_id"]
            }, token_secret ,algorithm="HS256")
        cookies = {
            'token': token
         }
        response = requests.get(f'http://localhost:{port}/returnVehicles', cookies=cookies)
        self.assertEqual(response.status_code, 200)
        fleets = json.loads(response.text)
        print(fleets)

    def test_vehicleHeartbeat_POST(self):
        payload = {
            "vehicleId": "HUSERFEF-R3242-3453535-SFSFSFER243Z",
            'status': 'busy',
            "location": "-97.731010,30.283930",
            "dock": "uhhh fix me pls"
        }
        response = requests.post(f'http://localhost:{port}/vehicleHeartbeat', json=payload, timeout=10)
        self.assertEqual(response.status_code, 200)
        expectedResponse = {
            'Heartbeat': 'Received'
            }
        self.assertEqual(json.loads(response.text), expectedResponse)
        updatedVehicle = db.Vehicle.find_one({"_id" : payload["vehicleId"]})
        self.assertEqual(updatedVehicle["status"], 'busy')
        self.assertEqual(updatedVehicle["location"], '-97.731010,30.283930')

        # return db to original state
        payload = {
            "vehicleId": "HUSERFEF-R3242-3453535-SFSFSFER242Y",
            'status' : 'ready',
            "location": "-97.731010,30.283930",
            "dock": "uhhh fix me pls"
            }
        requests.post(f'http://localhost:{port}/vehicleHeartbeat', json=payload, timeout=10)

    def test_vehicleHeartbeat_POST_responses(self):
        payload = {
            "vehicleId": "HUSERFEF-R3242-3453535-SFSFSFER2420",
            'status': 'ready',
            "location": "-97.731010,30.283930",
            "dock": "uhhh fix me pls"
        }
        db.Dispatch.update_one({"_id": "455"}, {'$set': {"status": "processing"}})
        response = requests.post(f'http://localhost:{port}/vehicleHeartbeat', json=payload, timeout=10)
        actualTypeCoordinates = type(json.loads(response.text)["coordinates"])
        expectedTypeCoordinates = type([])
        self.assertEqual(actualTypeCoordinates, expectedTypeCoordinates)
    def test_vehicleHeartbeat_POST_2(self):
        payload = {
            "vehicleId": "HUSERFEF-R3242-3453535-SFSFSFER243Z",
            'status': 'busy',
            "location": "-97.731010,30.283930",
            "dock": "uhhh fix me pls"
        }
        response = requests.post(f'http://localhost:{port}/vehicleHeartbeat', json=payload, timeout=10)
        expectedResponse = {
            'Heartbeat': 'Received'
        }
        self.assertEqual(json.loads(response.text), expectedResponse)
        #self.assertEqual(json.loads(response.text)['cursor'], expectedResponse)

    def test_vehicleHeartbeat_change_dispatch_status_1(self):
        payload = {
            "vehicleId": "HUSERFEF-R3242-3453535-SFSFSFER2420",
            'status': 'ready',
            "location": "-97.731010,30.283930",
            "dock": "uhhh fix me pls"
        }
        db.Dispatch.update_one({"_id": "455"}, {'$set': {"status": "processing"}})
        response = requests.post(f'http://localhost:{port}/vehicleHeartbeat', json=payload, timeout=10)
        expectedStatus = "in progress"
        disDoc = db.Dispatch.find_one({"_id": "455"})
        actualStatus = disDoc["status"]
        self.assertEqual(expectedStatus, actualStatus)

    def test_vehicleHeartbeat_change_dispatch_status_2(self):
        db.Dispatch.update_one({"_id": "456"}, {'$set': {"status": "in progress"}})
        dispatchObj = Dispatch(dispatch_three)
        geo_response = dispatchObj.requestForwardGeocoding()
        dest = Dispatch.getCoordinateFromGeocodeResponse(geo_response)
        payload = {
            "vehicleId": "HUSERFEF-R3242-3453535-SFSFSFER243Z",
            'status': 'busy',
            "location": dest,
            "dock": "uhhh fix me pls"
        }
        response = requests.post(f'http://localhost:{port}/vehicleHeartbeat', json=payload, timeout=10)
        expectedStatus = "complete"
        disDoc = db.Dispatch.find_one({"_id": "456"})
        actualStatus = disDoc["status"]
        self.assertEqual(expectedStatus, actualStatus)

    def test_vehicleHeartbeat_change_dispatch_status_3(self):
        db.Dispatch.update_one({"_id": "456"}, {'$set': {"status": "in progress"}})
        payload = {
            "vehicleId": "HUSERFEF-R3242-3453535-SFSFSFER243Z",
            'status': 'busy',
            "location": '-97.731010,30.283930',
            "dock": "uhhh fix me pls"
        }
        response = requests.post(f'http://localhost:{port}/vehicleHeartbeat', json=payload, timeout=10)
        expectedStatus = "in progress"
        disDoc = db.Dispatch.find_one({"_id": "456"})
        actualStatus = disDoc["status"]
        self.assertEqual(expectedStatus, actualStatus)
    def test_getvehicleLocation_1(self):
        response = requests.get(f"http://localhost:{port}/getVehicleLocation?vehicleId=HUSERFEF-R3242-3453535-SFSFSFER2420")
        expectedLocation = '-97.731010,30.283930'
        actualLocation = json.loads(response.text)['location']
        self.assertEqual(actualLocation, expectedLocation)
    @classmethod
    def tearDownClass(cls):
        # tear down server
        cls._server.shutdown()
        cls._server_thread.join()

if __name__ == '__main__':
    unittest.main()
