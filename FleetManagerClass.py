import sys

sys.path.insert(1, '../team22-common-services-backend')
sys.path.insert(1, '../common-services-backend')

from User import User


class FleetManager(User):
    # class constructor, takes data from postData and populates class attributes
    # inherents parent attributes
    def __init__(self, postData):
        super().__init__(postData)
        self._dockNumber = postData["dockNumber"]
        self._dockAddress = postData["dockAddress"]

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



