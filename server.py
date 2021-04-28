import json
import sys
import time
import jwt

from bson.objectid import ObjectId
from urllib import parse
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from utils.mongoutils import initMongoFromCloud
from fleetmanager import FleetManager
from dispatch import Dispatch
from fleet import Fleet
from os import getenv
from dotenv import load_dotenv
from queue import PriorityQueue

load_dotenv()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    version = '0.2.0'

    # Reads the POST data from the HTTP header
    def extract_POST_Body(self):
        postBodyLength = int(self.headers['content-length'])
        postBodyString = self.rfile.read(postBodyLength)
        postBodyDict = json.loads(postBodyString)
        return postBodyDict

    # This method handles and data updated that already exists on the database,
    def do_PUT(self):
        status = 400  # HTTP Request: Bad request
        postData = self.extract_POST_Body()  # store POST data into a dictionary
        path = self.path
        cloud = 'supply'
        client = initMongoFromCloud(cloud)
        db = client['team22_' + cloud]

        responseBody = {
            'status': 'failed',
            'message': 'Bad request'
        }

        if '/vehicleHeartbeat' in path:
            status = 401
            responseBody = {
                'status': 'failed',
                'message': 'Heartbeat Failed'
            }
            # Vehicle heartbeating / top update in DB
            vehicleId = postData.pop("vehicleId", None)
            location = postData.pop("location", None)
            vehicleStatus = postData.pop("status", None)
            lastHeartbeat = time.time()

            # Update document in DB
            vehicleStatusUpdate = db.Vehicle.update_one({"_id" : vehicleId}, {'$set' : {"status" : vehicleStatus}})
            vehicleLocationUpdate = db.Vehicle.update_one({"_id" : vehicleId}, {'$set' : {"location" : location}})
            lastHearbeatUpdate = db.Vehicle.update_one({"_id" : vehicleId}, {'$set' : {"lastHeartbeat" : lastHeartbeat}})


            statusUpdated = False
            locationUpdated = False
            lastHearbeatUpdated = False

            if vehicleStatusUpdate.matched_count == 1 and vehicleStatusUpdate.modified_count == 1:
                statusUpdated = True

            if vehicleLocationUpdate.matched_count == 1 and vehicleLocationUpdate.modified_count == 1:
                locationUpdated = True

            if lastHearbeatUpdate.matched_count == 1 and lastHearbeatUpdate.modified_count == 1:
                lastHearbeatUpdated = True

            if statusUpdated or locationUpdated or lastHearbeatUpdated:
                responseBody = {
                    'Heartbeat': 'Received'
                }
                # DatabaseUpdated
                # Find a dispatch document from DB where vehicleId = vehicleId from postData that is not complete
                dispatch_data = db.Dispatch.find_one({"vehicleId": vehicleId, "status": {'$ne': "complete"}})

                if dispatch_data == None:
                    '''if vehicle is not assigned to a dispatch that says either 'processing' or 'in progress', 
                    then check if there is a dispatch with no vehicle ID assigned
                    '''
                    vehicle_data = db.Vehicle.find_one({ "_id": vehicleId, "status": "ready" })
                    dispatch_data = db.Dispatch.find_one({ "vehicleId": "" });
                    if vehicle_data is not None and dispatch_data is not None and vehicle_data["vType"] == dispatch_data["vehicleType"]:
                        db.Dispatch.update_one({ "_id": dispatch_data["_id"] }, { "$set": { "vehicleId": vehicleId } })
                        dispatch_data["vehicleId"] = vehicleId

                # dispatch status is processing responseBody -> heartbeat received, send coordinates
                # dispatch status is in progress responseBody -> heartbeat received, send coordinates
                # dispatch status is complete responseBody -> heartbeat received
                if dispatch_data is not None and dispatch_data["vehicleId"] is not None and dispatch_data["vehicleId"] != "":
                    dispatch = Dispatch(dispatch_data)
                    directions_response = dispatch.requestDirections(db)
                    coordinates = Dispatch.getRouteCoordinates(directions_response)
                    last_coordinate = coordinates[len(coordinates)-1]
                    last_coordinate_string = f"{last_coordinate[0]},{last_coordinate[1]}"
                    dispatch.status= "in progress" # Change dispatch status -> in progress

                    # check if vehicle coordinate == order location
                    if location == last_coordinate_string:
                        dispatch.status = "complete"

                    db.Dispatch.update_one({"_id": dispatch.id}, {'$set': {"status": dispatch.status, "vehicleId": vehicleId }})

                    responseBody = {
                        'Heartbeat': 'Received',
                        'coordinates': coordinates,  # [ [90.560,45.503], [90.560,45.523] ]
                        'duration': directions_response["routes"][0]["legs"][0]["duration"]
                    }

                status = 200 # DatabaseUpdated 

        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        responseString = json.dumps(responseBody).encode('utf-8')
        self.wfile.write(responseString)
        client.close()


    # handle post requests
    def do_POST(self):
        status = 400  # HTTP Request: Not found
        postData = self.extract_POST_Body()  # store POST data into a dictionary
        path = self.path
        cloud = 'supply'
        client = initMongoFromCloud(cloud)
        db = client['team22_' + cloud]

        responseBody = {
            'status': 'failed',
            'message': 'Bad request'
        }

        if '/fleet' in path:
            status = 401
            # Get token so we can get the fleet manager
            fleetManager = self.get_fleet_manager_from_token(db)

            # add fleet to fleet manager and Fleet collection
            if fleetManager is not None:
                status = 200
                fleetManager.addFleet(db, postData)
                responseBody = {
                    "fleetManager": fleetManager.id,
                    "fleetIds": fleetManager.fleetIds
                }

        elif '/deleteVehicle' in path:
            status = 401
            vehicleId = postData.get('_id')
            vType = postData.get('vType')

            fleetManager = self.get_fleet_manager_from_token(db)

            # add fleet to fleet manager and Fleet collection
            if fleetManager is not None:
                status = 200
                fleet = fleetManager.accessFleet(db, vType)
                deleteResponse = fleet.deleteVehicle(db, vehicleId)
                responseBody = {
                    "totalVehicles" : fleet.totalVehicles,
                    "alertResponse" : deleteResponse
                }


        elif '/vehicle' in path:
            status = 401
            # Get token so we can get the fleet manager
            fleetManager = self.get_fleet_manager_from_token(db)
            #get correct fleet and add vehicle to it
            if fleetManager is not None:
                status = 200
                dockCoordinates = fleetManager.dockCoordinates
                fleet = fleetManager.accessFleet(db, postData['vType'])
                fleet.addVehicle(db, postData,dockCoordinates)
                responseBody = {
                    "totalVehicles": fleet.totalVehicles
                }

        elif '/dispatch' in path:
            dispatch_data = {
                "orderId": postData.get("orderId", None),
                "vehicleId": "",
                "orderDestination": postData.get("orderDestination", None),
                "status": "processing"
            }

            dispatch = Dispatch(dispatch_data)
            vehicleType = postData.get("vehicleType", None)

            # Check and make sure order ID is not none and order destination is not none
            if dispatch.orderId is not None and dispatch.orderDestination is not None and vehicleType is not None:
                # Avoid multiple duplicate dispatch of same order ID
                if db.Dispatch.find_one({ "orderId": dispatch.orderId }) == None:
                    vehicle_id = ""
                    cursor = db.Fleet.find({ "vType": vehicleType })
                    for fleet_data in cursor:
                        fleet = Fleet(fleet_data)
                        vehicle_data = fleet.findAvailableVehicle(db)
                        if vehicle_data != {}:
                            # once it finds a vehicle then save the id
                            vehicle_id = vehicle_data.get("vehicleId", "")
                            break

                    dispatch.vehicleId = vehicle_id
                    db.Dispatch.insert_one({
                        "_id": dispatch.id,
                        "orderId": dispatch.orderId,
                        "vehicleId": dispatch.vehicleId,
                        "status": dispatch.status,
                        "orderDestination": dispatch.orderDestination,
                        "vehicleType": vehicleType
                    })

                    status = 201 # request is created
                    responseBody = {
                        'status': 'success',
                        'message': 'Successfully dispatched order',
                        'dispatchStatus': dispatch.status,
                        'vehicleId': dispatch.vehicleId
                    }
                else:
                    # if order id has already been dispatch, throw error
                    status = 409
                    responseBody = {
                        'status': 'failed',
                        'message': 'already dispatched order'
                    }

        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        responseString = json.dumps(responseBody).encode('utf-8')
        self.wfile.write(responseString)
        client.close()

    # handle get requests
    def do_GET(self):
        path = self.path
        status = 400
        cloud = 'supply'
        client = initMongoFromCloud(cloud)
        db = client['team22_' + cloud]
        response = {
            'status': 'failed',
            'message': 'Bad request'
        }

        parameters = dict(parse.parse_qsl(parse.urlsplit(path).query))

        # Get token
        fleetManager = self.get_fleet_manager_from_token(db)

        #front end request for tables
        if '/returnVehicles' in path:
            status = 403 # Not Authorized
            response = {
                "message": "Not authorized"
            }

            if fleetManager is not None:
                # Validate
                fleetIds = fleetManager.fleetIds
                fleetArray = []
                vehicles = []
                for fleetId in fleetIds:
                    cursor = db.Vehicle.find({"fleetId": fleetId},
                                             {
                                                 "fleetId": 0,
                                                 "dock": 0,
                                             })
                    for vehicle in cursor:
                        vehicles.append(vehicle)

                    fleetArray.append(vehicles)
                    vehicles = []
                response = fleetArray
                status = 200

        # getting vTypes of current fleets
        elif '/getAllvTypes' in path:
            status = 403  # Not Authorized
            response = {
                "message": "Not authorized"
            }
            if fleetManager is not None:
                fleetIds = fleetManager.fleetIds
                vTypes = []
                if len(fleetIds) == 0:
                    vTypes.append("There are no fleets yet")
                else:
                    for fleetId in fleetIds:
                        fleet = db.Fleet.find_one({'_id': fleetId})
                        vType = fleet['vType']
                        vTypes.append(vType)

                status = 200
                response = vTypes

        elif '/getKPIS' in path:
            status = 403  # Not Authorized
            response = {
                "message": "Not authorized"
            }
            if fleetManager is not None:
                kpiDict = {}
                fleetManagerId = fleetManager.id
                fleetIds = fleetManager.fleetIds
                kpiDict["vehicleCount"] = 0
                kpiDict["vehiclesReady"] = 0
                kpiDict["vehiclesOOS"] = 0
                kpiDict["vehiclesBusy"] = 0
                kpiDict["fleetCount"] = 0
                if len(fleetIds) == 0:
                    foodFleetInfo = {
                        "totalVehicles": 0,
                        "vType": "food"
                    }
                    fleetManager.addFleet(db, foodFleetInfo)
                    kpiDict["fleetCount"] += 1
                    storageFleetInfo = {
                        "totalVehicles": 0,
                        "vType": "storage"
                    }
                    fleetManager.addFleet(db, storageFleetInfo)
                    kpiDict["fleetCount"] += 1
                    refrigeratedFleetInfo = {
                        "totalVehicles": 0,
                        "vType": "refrigerated"
                    }
                    fleetManager.addFleet(db, refrigeratedFleetInfo)
                    kpiDict["fleetCount"] += 1
                else:
                    for fleetId in fleetIds:
                        kpiDict["fleetCount"] += int(db.Fleet.find({"_id": fleetId}).count())
                        kpiDict["vehicleCount"] += int(db.Vehicle.find({"fleetId": fleetId}).count())
                        kpiDict["vehiclesReady"] += int(db.Vehicle.find({"status": "ready", "fleetId": fleetId}).count())
                        kpiDict["vehiclesOOS"] += int(db.Vehicle.find({"status": "oos", "fleetId": fleetId}).count())
                        kpiDict["vehiclesBusy"] += int(db.Vehicle.find({"status": "busy", "fleetId": fleetId}).count())
                response = kpiDict
                status = 200

        # vehicle request
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

        # This request handles multiple dispatch orders status
        elif '/status' in path:
            parameters = parse.parse_qs(parse.urlsplit(path).query)

            # Receives an array of order ids
            orderids_dict = parameters.get('orderId', None) 

            if orderids_dict is not None and len(orderids_dict) != 0:
                cursor = db.Dispatch.find({ "orderId": { "$in": orderids_dict } })
                dispatches_data = []

                for dispatch_data in cursor:
                    dispatch = Dispatch(dispatch_data)
                    # Get directions API and geocde API responses stored in variables
                    vehicle_current_location = ""
                    dock_location = ""
                    eta = 0
                    geometry = {}
                    destination_coordinate = ""
                    if dispatch.vehicleId != "":
                        directions_response = dispatch.requestDirections(db)
                        geocode_response = dispatch.requestForwardGeocoding()
                        vehicle_current_location = dispatch.getVehicleLocation(db)
                        dock_location = dispatch.getDock(db)
                        destination_coordinate = Dispatch.getCoordinateFromGeocodeResponse(geocode_response)
                        geometry = Dispatch.getGeometry(directions_response)
                        eta = Dispatch.getETAFromDirectionsResponse(directions_response)

                    dispatches_data.append({
                        'orderId': dispatch.orderId,
                        'dispatchStatus': dispatch.status,
                        'dock': dock_location,
                        'vehicleLocation': vehicle_current_location,
                        'destinationCoordinate': destination_coordinate,
                        'geometry': geometry,
                        'eta': eta
                    })
                if len(dispatches_data) != 0:
                    status = 200
                    response = {
                        'status': 'success',
                        'message': 'Retrieved dispatches information',
                        'dispatches': dispatches_data
                    }
                else:
                    status = 404 # Yes, I know this is used for files not found but technically this data wasnt found either
                    response = {
                        'status':  'failed', # Was able to parse request but there was no data found
                        'message': 'There was no dispatches within the given order ids.'
                    }
        elif '/getVehicleLocation' in path:
            vehicleid = parameters.get('vehicleId', None)
            if vehicleid is not None:
                vehicle_data = db.Vehicle.find_one({'_id': vehicleid})
                if vehicle_data is not None:
                    response = {
                        'location': vehicle_data['location']
                    }
                    status = 200

        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        responseString = json.dumps(response).encode('utf-8')
        self.wfile.write(responseString)
        client.close()

    def get_fleet_manager_from_token(self, db):
        try:
            tokenStr = self.headers["Cookie"]
            if tokenStr is not None:
                token = tokenStr.split('token=')[1].split(";")[0]
                if token != "":
                    token_secret = getenv("TOKEN_SECRET")
                    token_decoded = jwt.decode(token, token_secret, algorithms="HS256")
                    user_data = db.FleetManager.find_one({ "_id": token_decoded["user_id"]})
                    return FleetManager(user_data)
        except:
            pass
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
