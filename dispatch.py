import urllib.request
import json
import requests
import sys

if '../' in sys.path:
    # Current working firectory is unittest, so go back from directory twice
    sys.path.insert(2, '../../team22-common-services-backend')
    sys.path.insert(2, '../../common-services-backend')
else:
    # current working directory is team22-supply-backend so go back once
    sys.path.insert(1, '../team22-common-services-backend')
    sys.path.insert(1, '../common-services-backend')

from mongoutils import initMongoFromCloud
from uuid import uuid4

class Dispatch:
    # constant variable (class variable) api key:
    API_KEY = "pk.eyJ1IjoibmRhbHRvbjEiLCJhIjoiY2tsNWlkMHBwMTlncDJwbGNuNzJ6OGo2ciJ9.QbcnC4OnBjZU6P6JN6m3Pw"
    # Constructor. Initializes Dispatch from parameter values *** CAN ONLY ALLOW ONE CONSTRUCTOR ***
    # def __init__(self, orderId, customerId, orderDestination, status, vehicleId):
    #     self._id = uuid4()
    #     self._orderId = orderId
    #     self._customerId = customerId
    #     self._orderDestination = orderDestination
    #     self._status = status
    #     self._vehicleId = vehicleId

    # Constructor. Initializes class from dictionary, usually used to convert data from
    # mongo to object
    def __init__(self, dict):
        # Id is automatically generated if it's not in dictionary
        # useful when creating first time dispatches
        self._id = str(dict.get('_id', uuid4()))
        self._orderId = dict["orderId"]
        self._vehicleId = dict["vehicleId"]
        self._orderDestination = dict["orderDestination"]
        self._status = dict["status"]
        self._pluginType = dict["pluginType"]

    # Read only property of Dispatch Id
    @property
    def id(self):
        return self._id

    # Read only property of order Id
    @property
    def orderId(self):
        return self._orderId

    # Method Description: Modifies order destination string by
        # replacing a whitespace with a "%"
    # pre-condition: nothing
    # post-condition: returns string with white spaces " " replaced -> "%"
    # STRAIGHTFORWARD ex: "3001 S Congress Ave, Austin, TX 78704" -> "3001%S%Congress%Ave,%Austin,%TX%78704"
    # EXTREME ex: "NoWhiteSpaces" -> "NoWhiteSpaces"
    # BIZZARE/ EXOTIC ex: "" -> ""
    @property
    def orderDestination(self):
        return self._orderDestination

    # Sets value to orderDestination
    @orderDestination.setter
    def orderDestination(self, value):
        self._orderDestination = value

    # Read property for dispatch status
    @property
    def status(self):
        return self._status
    
    # Set status value
    @status.setter
    def status(self, value):
        self._status = value 

    # Read property for vehicle id
    @property
    def vehicleId(self):
        return self._vehicleId
    
    # Set vehicle id
    @vehicleId.setter
    def vehicleId(self, value):
        self._vehicleId = value 

    @property
    def pluginType(self):
        return self._pluginType

    # Set vehicle id
    @pluginType.setter
    def pluginType(self, value):
        self._pluginType = value 


    # Method Description: Sends a HTTP Request of Forward Geocoding Mapbox API
    # pre-condition: "nothing??"
    # post-condition: returns the JSON response of Forward Geocoding Mapbox API
    def requestForwardGeocoding(self):
        destination = self.orderDestination.replace(" ", "%")
        forwardGeocodingURL = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + destination +".json?types=address&access_token=" + self.API_KEY
        response = requests.get(forwardGeocodingURL)
        forwardGeocodeData = json.loads(response.text)
        return forwardGeocodeData

    # Method Description: Static method that parses the Forward Geocoding Mapbox Response to just get coordinates
    def getCoordinateFromGeocodeResponse(json_response):
        coordinate_in_array = json_response["features"][0]["geometry"]["coordinates"]
        coordinate_string = str(coordinate_in_array[0]) + "," + str(coordinate_in_array[1])
        return coordinate_string

    # Method Description: Grabs the vehicle location from the supply database
    #
    def getVehicleLocation(self, client):
        db = client['team22_'+'supply']
        dictionary = db.Vehicle.find_one({'_id' : self.vehicleId})
        location = ""
        if dictionary is not None:
            location = dictionary["location"]
        return location

    # Method Description: Sends a HTTP Request of Directions Mapbox API
    # pre-condition: "nothing??"
    # post-condition: returns the JSON response of Directions Mapbox API
    def requestDirections(self, client):
        forward_geocoding_json = self.requestForwardGeocoding()
        destination_coordinate = Dispatch.getCoordinateFromGeocodeResponse(forward_geocoding_json)
        directionsURL = "https://api.mapbox.com/directions/v5/mapbox/driving/" + self.getVehicleLocation(client) + ";" + destination_coordinate + "?geometries=geojson&overview=full&steps=true&access_token=" + self.API_KEY
        response = requests.get(directionsURL)
        directionsData = json.loads(response.text)
        return directionsData

    def getRouteCoordinates(json_response):
        steps = json_response["routes"][0]["legs"][0]["steps"]
        listOfListCoordinates = []
        for i in range(0, len(steps)):
            listOfListCoordinates.append(steps[i]["geometry"]["coordinates"])
        coordinates_list = []
        for i in listOfListCoordinates:
            for j in i:
                coordinates_list.append(j)
        return coordinates_list
        # vehicle will be given "STEPS", which is an array of ROUTE-STEP OBJECTS from the
        # ROUTE-LEG OBJECT, which is contained in the ROUTE OBJECT from the directions response.
        # A nested ROUTE-STEP OBJECT includes ONE-STEP-MANEUVER OBJECT
        # vehicle sim will need to get steps[i]["geometry"]["coordinates"]
 #
    def getGeometry(json_response):
        geometry = json_response["routes"][0]["geometry"]
        return geometry
    # returns a float
    def getETAFromDirectionsResponse(json_response):
        eta = json_response["routes"][0]["legs"][0]["duration"]
        return eta

    def __str__(self):
        return f"Dispatch (\nid: {self.id} \norderId: {self.orderId} \ncustomerId: {self.customerId} \norderDestination: {self.orderDestination} \nstatus: {self.status} \nvehicleId: {self.vehicleId} \n)"