import unittest
import sys

sys.path.insert(1, "../")

from dispatch import Dispatch


class DispatchTestCase(unittest.TestCase):


    def test_dispatch_creation_dictionary(self):
        data = {
            "_id": "1234",
            "orderId": "4321",
            "pluginType": "1",
            "orderDestination": "austin",
            "status": "available",
            "vehicleId": "4567"
        }
        dispatch = Dispatch(data)
        self.assertIsNotNone(dispatch)

    def test_dispatch_data_equals(self):
        data = {
            "_id": "1234",
            "orderId": "4321",
            "pluginType": "1",
            "orderDestination": "austin",
            "status": "available",
            "vehicleId": "4567"
        }
        dispatch = Dispatch(data)
        self.assertIsNotNone(dispatch)
        self.assertEqual(dispatch.id, "1234")
        self.assertEqual(dispatch.orderId, "4321")
        self.assertEqual(dispatch.pluginType, "1")
        self.assertEqual(dispatch.orderDestination, "austin")
        self.assertEqual(dispatch.status, "available")
        self.assertEqual(dispatch.vehicleId, "4567")

    def test_dispatch_data_change(self):
        data = {
            "_id": "1234",
            "orderId": "4321",
            "pluginType": "1",
            "orderDestination": "austin",
            "status": "available",
            "vehicleId": "4567"
        }
        dispatch = Dispatch(data)
        dispatch.orderDestination = "houston"
        self.assertEqual(dispatch.orderDestination, "houston")
        dispatch.status = "oos"
        self.assertEqual(dispatch.status, "oos")
        dispatch.vehicleId = "9453"
        self.assertEqual(dispatch.vehicleId, "9453")


if __name__ == '__main__':
    unittest.main()
