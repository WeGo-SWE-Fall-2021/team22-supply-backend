import unittest
import sys
import time
import requests
import json

from threading import Thread

sys.path.insert(1, "../")
sys.path.insert(2, "../../team22-common-services-backend")
sys.path.insert(2, "../../common-services-backend")
from mongoutils import initMongoFromCloud
from http.server import HTTPServer
from server import SimpleHTTPRequestHandler
from dispatch import Dispatch

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
    "token": "tokennnnn",
    "dockAddress": "addy",
    "dockNumber": "number", 
    "fleetIds": ["123"]
}

fleet_one = {
    "_id": "123",
    "fleetManagerId": fleet_manager_data_one["_id"],
    "totalVehicles": "1",
    "pluginIds": ["1", "2"],
    "vType":"food"
}

vehicle_one = {
    "_id": "789",
    "fleetId": fleet_one["_id"],
    'status' : 'ready',
    "vType": "food",
    "location": "-97.731010, 30.283930",
    "dock": "uhhh fix me pls",
    "lastHeartbeat": "1234892919.655932"
}

dispatch_one = {
    "_id": "454",
    "orderId": "123",
    "vehicleId": vehicle_one["_id"],
    "status": "in progress",
    "orderDestination": "3001 S Congress Ave, Austin, TX 78704",
    "pluginType": "1"
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
        db.Vehicle.insert_one(vehicle_one)


    def test_1_add_fleet_to_fleet_manager_1_request(self):
        payload = {
            "totalVehicles": 0,
            "pluginIds": ["3", "4"],
            "vType": "medicine"
        }

        token = fleet_manager_data_one["token"]
        cookies = {
            'token': token
         }
        response = requests.post(f"http://localhost:{port}/fleet", cookies=cookies, json=payload, timeout=5)
        client = initMongoFromCloud("supply")
        db = client["team22_supply"]
        fleetCount = db.Fleet.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.text)["fleetIds"], fleet_manager_data_one["fleetIds"])
        self.assertEqual(fleetCount, 2)


    def test_1_add_vehicle_to_fleet_1_request(self):
        payload = {
            'status': 'ready',
            "vType": "food",
            "dock": "dock address",
        }

        token = fleet_manager_data_one["token"]
        cookies = {
            'token': token
         }
        response = requests.post(f"http://localhost:{port}/vehicle", cookies=cookies, json=payload, timeout=5)
        client = initMongoFromCloud("supply")
        db = client["team22_supply"]
        vehicleCount = db.Vehicle.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.text)["totalVehicles"], '2')
        self.assertEqual(vehicleCount, 2)

    def test_vehicle_1_location_dispatch_1(self):
        dispatch = Dispatch(dispatch_one)
        location = dispatch.getVehicleLocation(client)
        self.assertEqual(location, vehicle_one["location"])

    def test_dispatch_one_get_eta_1(self):
        dispatch = Dispatch(dispatch_one)
        dir_response = dispatch.requestDirections(client)
        expected_eta = 694.097
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
            "pluginType": "1"
        }
        response = requests.post(f"http://localhost:{port}/dispatch", json=payload, timeout=5)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.text)["dispatch_status"], "processing")
        self.assertEqual(json.loads(response.text)["vehicleId"], "789")

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
        self.assertEqual(response.status_code, 201)
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


    @classmethod
    def tearDownClass(cls):
        # tear down server
        cls._server.shutdown()
        cls._server_thread.join()

if __name__ == '__main__':
    unittest.main()
