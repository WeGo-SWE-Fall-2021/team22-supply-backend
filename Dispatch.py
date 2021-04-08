import urllib.request
import json
import requests

from uuid import uuid4

class Dispatch:
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
        self._customerId = dict["customerId"]
        self._orderDestination = dict["orderDestination"]
        self._status = dict["status"]
        self._vehicleId = dict["vehicleId"]

    # Read only property of Dispatch Id
    @property
    def id(self):
        return self._id

    # Read only property of order Id
    @property
    def orderId(self):
        return self._orderId

    # Read only property of customer Id
    @property
    def customerId(self):
        return self._customerId

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

    # Method Description: Sends a HTTP Request of Forward Geocoding Mapbox API
    # pre-condition: "nothing??"
    # post-condition: returns the JSON response of Forward Geocoding Mapbox API
    def requestForwardGeocoding(self):
        destination = self.getOrderDestination()
        forwardGeocodingURL = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + destination +".json?types=address&access_token=" + api_key
        response = requests.get(forwardGeocodingURL)
        forwardGeocodeData = json.loads(response.text)
        return forwardGeocodeData

    def getCoordinateFromGeocodeResponse(self, json_response):
        coordinate = json_response["features"][0]["geometry"]["coordinates"]
        return coordinate

    # Method Description: Sends a HTTP Request of Directions Mapbox API
    # pre-condition: "nothing??"
    # post-condition: returns the JSON response of Directions Mapbox API
    def requestDirections(self):
        json_response = self.requestForwardGeocoding()
        destination_coordinate = self.parseForwardGeocodingResponse(json_response)

    def getRouteStepsFromDirectionsResponse(self):
        pass

    def sendDirections(self):
        pass

    def getETAFromDirectionsResponse(self):
        pass

    def __str__(self):
        return f"Dispatch (\nid: {self.id} \norderId: {self.orderId} \ncustomerId: {self.customerId} \norderDestination: {self.orderDestination} \nstatus: {self.status} \nvehicleId: {self.vehicleId} \n)"