from uuid import uuid4
import time

class Fleet():
    # class constructor, receives a dictionary and populates class attributes
    def __init__(self, dict):
        self._id = str(dict.get('_id', uuid4()))
        self._totalVehicles = dict["totalVehicles"]
        self._vType = dict["vType"]

    #---------- setters & getters -----------
    @property
    def id(self):
        return self._id

    @property
    def totalVehicles(self):
        return self._totalVehicles

    @totalVehicles.setter
    def totalVehicles(self, value):
        self._totalVehicles = value

    @property
    def vType(self):
        return self._vType

    @vType.setter
    def vType(self, value):
        self._vType = value


    #chooses a ready vehicle with the appropriate plugin
    #returns dict with Vehicle ID and current location
    def findAvailableVehicle(self, db):
        returnDict = {}
        vehicle = db.Vehicle.find_one({'status': 'ready', 'fleetId': self.id})

        if vehicle is not None:
            vehicleId = vehicle['_id']
            currentLocation = vehicle['location']

            returnDict['vehicleId'] = vehicleId
            returnDict['location'] = currentLocation
        else:
            return returnDict

        return returnDict

    #addes vehicle to vehicle collection
    def addVehicle(self, db, postData, dockCoordinates):
        vehicleInfo = postData
        vehicle = db.Vehicle.insert_one({
            '_id': str(uuid4()),
            'fleetId': self._id,
            'status' : vehicleInfo['status'],
            'location': dockCoordinates,
            'dock': dockCoordinates,
            'lastHeartbeat': str(time.time()),
            'vType' : vehicleInfo['vType']
        })
        totalVehiclesInt = self.totalVehicles + 1
        self.totalVehicles = totalVehiclesInt
        db.Fleet.update_one({'_id': self.id}, {"$set": {'totalVehicles': totalVehiclesInt}})

    def deleteVehicle(self, db, vehicleId):
        foundDispatch = list(db.Dispatch.find({"vehicleId" : vehicleId , "status": {"$ne" : "complete"}}))

        if len(foundDispatch) != 0:
            return "This vehicle is on a route \n Please delete after the route is complete"
        else:
            db.Vehicle.delete_one({"_id": vehicleId})
            totalVehiclesInt = self.totalVehicles - 1
            self.totalVehicles = totalVehiclesInt
            db.Fleet.update_one({'_id': self.id}, {"$set": {'totalVehicles': totalVehiclesInt}})
            return "successfully deleted"

