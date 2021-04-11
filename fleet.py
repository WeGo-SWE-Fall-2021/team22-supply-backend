import uuid
import time

class Fleet():
    # class constructor, receives a dictionary and populates class attributes
    def __init__(self, dict):
        self.id = str(dict.get('_id', uuid.uuid4()))
        self.pluginIds = dict["pluginIds"]
        self.totalVehicles = dict["totalVehicles"]
        self.vType = dict["vType"]

    #---------- setters & getters -----------
    @property
    def id(self):
        return self.id

    @id.setter
    def id(self, id):
        self.id = id

    @property
    def pluginIds(self):
        return self.pluginIds

    @pluginIds.setter
    def pluginsIds(self, pluginIds):
        self.pluginIds = pluginIds

    @property
    def totalVehicles(self):
        return self.totalVehicles

    @totalVehicles.setter
    def totalVehicles(self, totalVehicles):
        self.totalVehicles = totalVehicles

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
            '_id': uuid.uuid4(),
            'fleetId': self.id,
            'status' : 'available',
            'location': vehicleInfo['location'],
            'dock': vehicleInfo['dock'],
            'lastHeartbeat': str(time.time())
        })
        self.totalVehicles += 1
        update = db.Vehicle.update_one({'fleetId': self.id}, {"$set" : {'totalVehicles': int(self.totalVehicles)}})





