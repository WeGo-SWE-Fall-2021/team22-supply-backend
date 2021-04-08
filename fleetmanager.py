import sys

sys.path.insert(1, '../team22-common-services-backend')
sys.path.insert(1, '../common-services-backend')

from user import User


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


