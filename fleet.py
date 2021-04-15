from uuid import uuid4
import time

class Fleet():
    # class constructor, receives a dictionary and populates class attributes
    def __init__(self, dict):
        self._id = str(dict.get('_id', uuid4()))
        self._pluginIds = dict["pluginIds"]
        self._totalVehicles = dict["totalVehicles"]
        self._vType = dict["vType"]

    #---------- setters & getters -----------
    @property
    def id(self):
        return self._id

    @property
    def pluginIds(self):
        return self._pluginIds

    @pluginIds.setter
    def pluginIds(self, value):
        self._pluginIds = value

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
    def findAvailableVehicle(self,client):
        returnDict = {}
        status = 'ready'
        db = client['team22_' + 'supply']

        vehicle = db.Vehicle.find_one({'status': status, 'fleetId': self.id})

        if vehicle is not None:
            vehicleId = vehicle['_id']
            currentLocation = vehicle['location']
            # update vehicle status to 'busy'
            #myquery = {"_id": vehicleId}

            #status = 'busy'
            #newvalues = {"$set": {"status": status}}

            #update = db.Vehicle.update_one(myquery, newvalues)

            #fill the return dict with vehicle id and current location
            returnDict['vehicleId'] = vehicleId
            returnDict['location'] = currentLocation
        else:
            return returnDict

        return returnDict

    #addes vehicle to vehicle collection
    def addVehicle(self, client, postData):
        vehicleInfo = postData
        db = client['team22_' + 'supply']
        vehicle = db.Vehicle.insert_one({
            '_id': str(uuid4()),
            'fleetId': self._id,
            'status' : vehicleInfo['status'],
            'location': vehicleInfo['dock'],
            'dock': vehicleInfo['dock'],
            'lastHeartbeat': str(time.time()),
            'vType' : vehicleInfo['vType']
        })
        totalVehiclesInt = int(self._totalVehicles) + 1
        self.totalVehicles = str(totalVehiclesInt)
        db.Fleet.update_one({'fleetId': self.id}, {"$set": {'totalVehicles': int(self.totalVehicles)}})
