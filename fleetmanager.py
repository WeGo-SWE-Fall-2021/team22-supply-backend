import sys

if '../' in sys.path:
    # Current working firectory is unittest, so go back from directory twice
    sys.path.insert(2, '../../team22-common-services-backend')
    sys.path.insert(2, '../../common-services-backend')
else:
    # current working directory is team22-supply-backend so go back once
    sys.path.insert(1, '../team22-common-services-backend')
    sys.path.insert(1, '../common-services-backend')

from user import User
from fleet import Fleet


class FleetManager(User):
    # class constructor, receives a dictionary and populates class attributes
    # inherents parent attributes
    def __init__(self, dict):
        super().__init__(dict)
        self._dockNumber = dict["dockNumber"]
        self._dockAddress = dict["dockAddress"]
        self._fleetIds = dict["fleetIds"]

    #---------- setters & getters -----------
    @property
    def dockNumber(self):
        return self._dockNumber

    @dockNumber.setter
    def dockNumber(self, dockNum):
        self._dockNumber = dockNum

    @property
    def dockAddress(self):
        return self._dockAddress

    @dockAddress.setter
    def dockAddress(self, dockAddy):
        self._dockAddress = dockAddy

    @property
    def fleetIds(self):
        return self._fleetIds

    @fleetIds.setter
    def fleetIds(self, value):
        self._fleetIds = value


    def __str__(self):
        return f"FleetManager (\nid: {self.id} \nfirstName: {self.firstName} \nlastName: {self.lastName} \nphoneNumber: {self.phoneNumber} \nemail: {self.email} \nusername: {self.username} \npassword: {self.password} \ndockNumber: {self.dockNumber} \ndockAddress: {self.dockAddress} \n fleetIds: {self.fleetIds} \n)"

    #adds a new fleet to Fleet Collection and to FleetManager plugins array
    def addFleet(self, client, postData):
        fleetInfo = postData
        db = client['team22_' + 'supply']
        fleet = Fleet(postData)
        fleetID = fleet.id
        fleet = db.Fleet.insert_one({
            '_id': fleetID,
            'fleetManagerId': self._id,
            'totalVehicles': fleetInfo['totalVehicles'],
            'pluginIds' : fleetInfo['pluginIds'],
            'vType' : fleetInfo['vType']
        })

        #adding the fleet to the FleetManagers fleet array
        db.FleetManager.update({'_id': self._id}, {'$addToSet': {'pluginIds': fleetID}})

    # find and return the correct fleet based on the vType it is given
    def accessFleet(self, client, vType):
        db = client['team22_' + 'supply']

        fleet_data = db.Fleet.find_one({'fleetManagerId': self._id, 'vType': vType})
        if fleet_data is not None:
            returnFleet = Fleet(fleet_data)


        return returnFleet



