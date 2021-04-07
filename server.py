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
from MongoUtils import initMongoFromCloud
from FleetManagerClass import FleetManager


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

        if '/fleet':
            # HACKING THE SYSTEM

        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        responseString = json.dumps(responseBody).encode('utf-8')
        self.wfile.write(responseString)
        client.close()

    def do_GET(self):
        path = self.path
        print(path)
        status = 404
        cloud = 'supply'
        client = initMongoFromCloud(cloud)
        db = client['team22_' + cloud]
        response = {}
        # Get token
        fleetManager = getFleetManagerFromToken()

        # TODO Move to POST
        if '/dispatch' in path:
            parse.urlsplit(path)
            parse.parse_qs(parse.urlsplit(path).query)
            parameters = dict(parse.parse_qsl(parse.urlsplit(path).query))

            try:
                response = {'orderNum': parameters.get('orderNum')}
                status = 200 #request is found
            except:
                 status = 404

        elif '/returnVehicle' in path:
            status = 403 # Not Authorized
            response = {
                "message": "Not authorized"
            }
 
            if fleetManager is not None:
                # Validate
                cursor = db.Fleet.find({}, {'_id': 1, 'status': 1})
                vehicles = []
                response = vehicles

                status = 200
                response = {
                    "fname": fleetManager.fname,
                    "lname": fleetManager.lname,
                    "email": fleetManager.email,
                    "username": fleetManager.username
                }

        else:
            status = 400
            response = {'received': 'nope'}

        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        responseString = json.dumps(response).encode('utf-8')
        self.wfile.write(responseString)
        client.close()

    def getFleetManagerFromToken():
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
