import json
import sys
import time
from bson.objectid import ObjectId
# Allow importing files from other directories
sys.path.insert(1, '../team22-common-services-backend')
sys.path.insert(1, '../common-services-backend')
from urllib import parse
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from mongoutils import initMongoFromCloud
from fleetmanager import FleetManager
from dispatch import Dispatch
from fleet import Fleet

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    version = '0.1.0'

    # Reads the POST data from the HTTP header
    def extract_POST_Body(self):
        postBodyLength = int(self.headers['content-length'])
        postBodyString = self.rfile.read(postBodyLength)
        postBodyDict = json.loads(postBodyString)
        return postBodyDict

    # handle post requests
    def do_POST(self):
        status = 404  # HTTP Request: Not found
        postData = self.extract_POST_Body()  # store POST data into a dictionary
        path = self.path
        cloud = 'supply'
        client = initMongoFromCloud(cloud)
        db = client['team22_' + cloud]

        responseBody = {
            'status': 'failed',
            'message': 'Request not found'
        }

        if '/vehicleHeartbeat' in path:
            status = 401
            responseBody = {
                'status': 'failed',
                'message': 'Heartbeat Failed'
            }
            # Vehicle heartbeating / top update in DB
            vehicleId = postData.pop("vehicleId", None)
            lastHeartbeat = time.time()

            postData["lastHeartbeat"] = lastHeartbeat

            # Update document in DB
            result = db.Vehicle.replace_one({"_id" : ObjectId(vehicleId)}, postData)

            if result.matched_count == 1 and result.modified_count == 1:
                responseBody = {
                    'Heartbeat': 'Received'
                }
                status = 200 # DatabaseUpdated 

        elif '/fleet' in path:
            status = 401
            # Get token so we can get the fleet manager
            fleetManager = self.get_fleet_manager_from_token(db)

            # add fleet to fleet manager and Fleet collection
            if fleetManager is not None:
                fleetManager.addFleet(client, postData)
                status = 200
                responseBody = {
                    "fleetManager": fleetManager.id,
                    "fleetIds": fleetManager.fleetIds
                }

        elif '/vehicle' in path:
            status = 401
            # Get token so we can get the fleet manager
            fleetManager = self.get_fleet_manager_from_token(db)
            #get correct fleet and add vehicle to it
            if fleetManager is not None:
                status = 200
                fleet = fleetManager.accessFleet(client, postData['vType'])
                fleet.addVehicle(client, postData)
                responseBody = {
                    "totalVehicles": fleet.totalVehicles
                }

        elif '/dispatch' in path:
            status = 401
            dispatch_data = {
                "orderId": postData["orderId"],
                "vehicleId": "0",
                "orderDestination": postData["orderDestination"],
                "status": "processing",
                "pluginType": postData["pluginType"]
            }

            dispatch = Dispatch(dispatch_data)
            fleet_data = db.Fleet.find_one({"pluginIds": dispatch.pluginType})

            if fleet_data is not None:
                # Convert data to Fleet Object and request a vehicle
                fleet = Fleet(fleet_data)
                vehicleDict = fleet.findAvailableVehicle(client)

                dispatch.vehicleId = vehicleDict['vehicleId']
                db.Dispatch.insert_one({
                    "_id": dispatch.id,
                    "orderId": dispatch.orderId,
                    "vehicleId": dispatch.vehicleId,
                    "status": dispatch.status,
                    "orderDestination": dispatch.orderDestination,
                    "pluginType": dispatch.pluginType
                })
                status = 201 # request is created
                responseBody = {
                    'dispatch_status': dispatch.status,
                    'vehicleId': dispatch.vehicleId
                }
        elif '/status' in path:
            status = 401
            cursor = db.Dispatch.find({'orderId': postData["orderId"]})
            for dis in cursor:
                dispatch_data = dis
            if dispatch_data is not None:
                dispatch = Dispatch(dispatch_data)
                # Get directions API and geocde API responses stored in variables
                directions_response = dispatch.requestDirections(client)
                geocode_response = dispatch.requestForwardGeocoding()

                vehicle_starting_coordinate = dispatch.getVehicleLocation(client)
                destination_coordinate = Dispatch.getCoordinateFromGeocodeResponse(geocode_response)
                geometry = Dispatch.getGeometry(directions_response)
                status = 201
                responseBody = {
                    'order_status': "progress",
                    'vehicle_starting_coordinate': vehicle_starting_coordinate,
                    'destination_coordinate': destination_coordinate,
                    'geometry': geometry
                }
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        responseString = json.dumps(responseBody).encode('utf-8')
        self.wfile.write(responseString)
        client.close()

    def do_GET(self):
        path = self.path
        status = 400
        cloud = 'supply'
        client = initMongoFromCloud(cloud)
        db = client['team22_' + cloud]
        response = {}
        # Get token
        fleetManager = self.get_fleet_manager_from_token(db)

        if '/returnVehicles' in path:
            status = 403 # Not Authorized
            response = {
                "message": "Not authorized"
            }
 
            if fleetManager is not None:
                # Validate
                fleetIds = fleetManager.fleetIds
                vehicles = []
                for fleetId in fleetIds:
                    cursor = db.Vehicle.find({"fleetId": fleetId},
                                             {
                                                 "_id": 1,
                                                 "fleetId":  1,
                                                 'status' : 1,
                                                 "vType": 0,
                                                 "location": 0,
                                                 "dock": 0,
                                                 "lastHeartbeat": 1
                                             })
                    for vehicle in cursor:
                        vehicles = vehicles.append(vehicle)

                response = vehicles

                status = 200
                response = {
                    "fname": fleetManager.firstName,
                    "lname": fleetManager.lastName,
                    "email": fleetManager.email,
                    "username": fleetManager.username
                }
        elif '/getAllVehicles' in path:
            vehicles = []
            try:
                cursor = db.Vehicle.find({})
                for vehicle in cursor:
                    vehicles.append(vehicle)
                status = 200
                response = vehicles
                
            except:
                response = {'request': 'failed'}

        else:
            status = 400
            response = {'received': 'nope'}

        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        responseString = json.dumps(response).encode('utf-8')
        self.wfile.write(responseString)
        client.close()

    def get_fleet_manager_from_token(self, db):
        tokenStr = self.headers["Cookie"]
        if tokenStr is not None:
            token = tokenStr.split('=')[1]
            user = db.FleetManager.find_one({"token": token})
            if user is not None:
                return FleetManager(user)
        return None

def main():
    port = 4001  # Port 4001 reserved for demand backend
    server = HTTPServer(('', port), SimpleHTTPRequestHandler)
    print('Server is starting... Use <Ctrl+C> to cancel. Running on Port {}'.format(port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped server due to user interrupt")
    print("Server stopped")


if __name__ == "__main__":
    main()
