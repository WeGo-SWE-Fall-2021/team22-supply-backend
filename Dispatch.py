import urllib.request
import json
import requests

class Dispatch:
    # Constructor. Initializes a attributes : dispatchID
    def __init__(self):
        self.dispatchID = 0
        self.orderDestination = ""
    # Method Description: Sets a dispatchID attribute
    # pre-condition: Takes an int into parameter. aDispatchID > 0.
    # post-condition: self.dispatch = aDispatchID
    def setDispatchID(self, aDispatchID):
        self.dispatchID = aDispatchID

    # Method Description: Modifies order destination string by
        # replacing a whitespace with a "%"
    # pre-condition: nothing
    # post-condition: returns string with white spaces " " replaced -> "%"
    # STRAIGHTFORWARD ex: "3001 S Congress Ave, Austin, TX 78704" -> "3001%S%Congress%Ave,%Austin,%TX%78704"
    # EXTREME ex: "NoWhiteSpaces" -> "NoWhiteSpaces"
    # BIZZARE/ EXOTIC ex: "" -> ""
    def getOrderDestination(self):
        pass

    # Method Description: Sends a HTTP Request of Forward Geocoding Mapbox API
    # pre-condition: "nothing??"
    # post-condition: returns the JSON response of Forward Geocoding Mapbox API
    def requestForwardGeocoding(self):
        destination = self.getOrderDestination()
        forwardGeocodingURL = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + destination +".json?types=address&access_token=" + api_key
        response = requests.get(forwardGeocodingURL)
        forwardGeocodeData = json.loads(response.text)

        coordinate = forwardGeocodeData["features"][0]["geometry"]["coordinates"]
        return coordinate

    def parseForwardGeocodingResponse(self, json_response):
        pass
    # Method Description: Sends a HTTP Request of Directions Mapbox API
    # pre-condition: "nothing??"
    # post-condition: returns the JSON response of Directions Mapbox API
    def requestDirections(self):
        json_response = self.requestForwardGeocoding()
        destination_coordinate = self.parseForwardGeocodingResponse(json_response)

    def parseDirectionsResponse(self):
        pass

    def sendDirections(self):
        pass