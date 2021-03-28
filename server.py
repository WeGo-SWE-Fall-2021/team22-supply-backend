import sys
# Import common services backend to access database
sys.path.insert(1, '../team22-common-services-backend')
sys.path.insert(1, '../common-services-backend')

from urllib import parse
import json
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from MongoUtils import initMongoFromCloud


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    version = '0.0.1'

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


        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        responseString = json.dumps(responseBody).encode('utf-8')
        self.wfile.write(responseString)
        client.close()



    def do_GET(self):
        path = self.path
        status = 404

        #if '/api/v1/order' in path:
            #url = self.getRequestURI()
            #parse.urlsplit(url)
            #parse.parse_qs(parse.urlsplit(url).query)
            #parameters = dict(parse.parse_qsl(parse.urlsplit(url).query))
            #try:
             #   responseBody = {'orderNum': parameters.get('orderNum')}
            #    status = 200 #request is found

            #except:
             #   status = 404

            #self.send_response(status)
            #self.send_header("Content-Type", "text/html")
            #self.end_headers()
            #esponseString = json.dumps(responseBody).encode('utf-8')
            #self.wfile.write(responseString)

        if '/returnVehicle' in path:
            cloud = 'supply'
            client = initMongoFromCloud(cloud)
            db = client['team22_' + cloud]
            status = 200
            #response = {'hello': 'world', 'received': 'ok'}
            # Now creating a Cursor instance using find() function
            vehicleID = int(123)
            cursor = db.Vehicle.find({"vehicleID": vehicleID})
            # Converting cursor to the list of dictionaries
            list_cur = list(cursor)
            #vehicle = cursor.next()
            response = list_cur
        else:
            status = 400
            response = {'received': 'nope' }

        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        responseString = json.dumps(response).encode('utf-8')
        self.wfile.write(responseString)
        client.close()




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
