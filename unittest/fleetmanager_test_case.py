import unittest
import sys

sys.path.insert(1, "../")

from fleetmanager import FleetManager


class FleetManagerTestCase(unittest.TestCase):

    def test_fleetManger_creation(self):
        data = {
            "firstName": "firstname",
            "lastName": "lastname",
            "phoneNumber": "11111",
            "email": "email@email.com",
            "username": "user",
            "password": "pwdtest",
            "dockNumber": "testDockNum",
            "dockAddress": "testAddress",
            "fleetIds": ["123", "321"]
        }
        fleetManager = FleetManager(data)
        self.assertIsNotNone(fleetManager)

    def test_fleetManager_data_equals(self):
        data = {
            "firstName": "firstname",
            "lastName": "lastname",
            "phoneNumber": "11111",
            "email": "email@email.com",
            "username": "user",
            "password": "pwdtest",
            "dockNumber": "testDockNum",
            "dockAddress": "testAddress",
            "fleetIds": ["123", "321"]
        }
        fleetManager = FleetManager(data)
        self.assertIsNotNone(fleetManager)
        self.assertEqual(fleetManager.firstName, "firstname")
        self.assertEqual(fleetManager.lastName, "lastname")
        self.assertEqual(fleetManager.phoneNumber, "11111")
        self.assertEqual(fleetManager.email, "email@email.com")
        self.assertEqual(fleetManager.username, "user")
        self.assertEqual(fleetManager.password, "pwdtest")
        self.assertEqual(fleetManager.dockNumber, "testDockNum")
        self.assertEqual(fleetManager.dockAddress, "testAddress")
        self.assertEqual(fleetManager.fleetIds, ["123", "321"])


    def test_fleetManager_data_change(self):
        data = {
            "firstName": "firstname",
            "lastName": "lastname",
            "phoneNumber": "11111",
            "email": "email@email.com",
            "username": "user",
            "password": "pwdtest",
            "dockNumber": "testDockNum",
            "dockAddress": "testAddress",
            "fleetIds": ["123", "321"]
        }
        fleetManager = FleetManager(data)
        fleetManager.username = "new_username"
        self.assertEqual(fleetManager.username, "new_username")
        fleetManager.password = "new_pwdtest"
        self.assertEqual(fleetManager.password, "new_pwdtest")
        fleetManager.email = "new@new.com"
        self.assertEqual(fleetManager.email, "new@new.com")
        fleetManager.firstName = "newfirstname"
        self.assertEqual(fleetManager.firstName, "newfirstname")
        fleetManager.lastName = "newlastname"
        self.assertEqual(fleetManager.lastName, "newlastname")
        fleetManager.phoneNumber = "00000"
        self.assertEqual(fleetManager.phoneNumber, "00000")
        fleetManager.dockNumber = "W123"
        self.assertEqual(fleetManager.dockNumber, "W123")
        fleetManager.dockAddress = "123 test"
        self.assertEqual(fleetManager.dockAddress, "123 test")
        fleetManager.fleetIds = []
        self.assertEqual(fleetManager.fleetIds, [])


if __name__ == '__main__':
    unittest.main()
