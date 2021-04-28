import unittest
import sys

sys.path.insert(1, sys.path[0] + "/../")

from fleet import Fleet

class FleetTestCase(unittest.TestCase):

    def test_Fleet_creation(self):
        data = {
            "_id": "123",
            "totalVehicles": 1,
            "vType":"food"
        }
        fleet = Fleet(data)
        self.assertIsNotNone(fleet)

    def test_fleetManager_data_equals(self):
        data = {
            "_id": "123",
            "totalVehicles": 1,
            "vType": "food"
        }
        fleet = Fleet(data)
        self.assertIsNotNone(fleet)
        self.assertEqual(fleet.id, "123")
        self.assertEqual(fleet.totalVehicles, 1)
        self.assertEqual(fleet.vType, "food")


    def test_fleetManager_data_change(self):
        data = {
            "_id": "123",
            "totalVehicles": 1,
            "vType": "food"
        }
        fleet = Fleet(data)
        fleet.totalVehicles = 3
        self.assertEqual(fleet.totalVehicles, 3)
        fleet.vType = "storage"
        self.assertEqual(fleet.vType, "storage")


if __name__ == '__main__':
    unittest.main()
