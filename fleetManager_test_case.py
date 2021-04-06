import unittest
import sys
sys.path.insert(1, "../")
from FleetManagerClass import FleetManager


class FleetManagerTestCase(unittest.TestCase):

    def test_fleetManger_creation(self):
        data = {
            "fname": "firstname",
            "lname": "lastname",
            "phoneNumber": "11111",
            "email": "email@email.com",
            "username": "user",
            "password": "pwdtest",
            "fleetManagerID": "testID",
            "dockNumber": "testDockNum",
            "dockAddress": "testAddress"
        }
        fleetManager = FleetManager(data)
        self.assertIsNotNone(fleetManager)

    def test_fleetManager_data_equals(self):
        data = {
            "fname": "firstname",
            "lname": "lastname",
            "phoneNumber": "11111",
            "email": "email@email.com",
            "username": "user",
            "password": "pwdtest",
            "fleetManagerID": "testID",
            "dockNumber": "testDockNum",
            "dockAddress": "testAddress"
        }
        fleetManager = FleetManager(data)
        self.assertIsNotNone(fleetManager)
        self.assertEqual(fleetManager.fname, "firstname")
        self.assertEqual(fleetManager.lname, "lastname")
        self.assertEqual(fleetManager.phoneNumber, "11111")
        self.assertEqual(fleetManager.email, "email@email.com")
        self.assertEqual(fleetManager.username, "user")
        self.assertEqual(fleetManager.password, "pwdtest")
        self.assertEqual(fleetManager.fleetManagerID, "testID")
        self.assertEqual(fleetManager.dockNumber, "testDockNum")
        self.assertEqual(fleetManager._dockAddress, "testAddress")


    def test_fleetManager_data_change(self):
        data = {
            "fname": "firstname",
            "lname": "lastname",
            "phoneNumber": "11111",
            "email": "email@email.com",
            "username": "user",
            "password": "pwdtest",
            "fleetManagerID": "testID",
            "dockNumber": "testDockNum",
            "dockAddress": "testAddress"
        }
        fleetManager = FleetManager(data)
        fleetManager.username = "new_username"
        self.assertEqual(fleetManager.username, "new_username")
        fleetManager.password = "new_pwdtest"
        self.assertEqual(fleetManager.password, "new_pwdtest")
        fleetManager.email = "new@new.com"
        self.assertEqual(fleetManager.email, "new@new.com")
        fleetManager.fname = "newfirstname"
        self.assertEqual(fleetManager.fname, "newfirstname")
        fleetManager.lname = "newlastname"
        self.assertEqual(fleetManager.lname, "newlastname")
        fleetManager.phoneNumber = "00000"
        self.assertEqual(fleetManager.phoneNumber, "00000")
        fleetManager.fleetManagerID = "A123"
        self.assertEqual(fleetManager.fleetManagerID, "A123")
        fleetManager.dockNumber = "W123"
        self.assertEqual(fleetManager.dockNumber, "W123")
        fleetManager.dockAddress = "123 test"
        self.assertEqual(fleetManager.dockAddress, "123 test")


if __name__ == '__main__':
    unittest.main()
