import unittest
import sys

sys.path.insert(1, sys.path[0] + "/../")

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

    def test_getCoordinateFromGeocodeResponse_type(self):
        data = {
            "_id": "1234",
            "orderId": "4321",
            "pluginType": "1",
            "orderDestination": "12501 N Mopac Expy, Austin, TX 78758",
            "status": "available",
            "vehicleId": "4567"
        }
        dispatch = Dispatch(data)
        geocode_response = dispatch.requestForwardGeocoding()
        actual_answer = type(Dispatch.getCoordinateFromGeocodeResponse(geocode_response))
        expected_answer = type("-97.70323908466139,30.419022366177018")
        self.assertEqual(actual_answer, expected_answer)
    # test case: checks if there is a comma in the getCoordinateFromGeocodeResponse return value
    def test_getCoordinateFromGeocodeResponse_comma(self):
        comma_character = ","
        data = {
            "_id": "1234",
            "orderId": "4321",
            "pluginType": "1",
            "orderDestination": "801 Red River St, Austin, TX 78701",
            "status": "available",
            "vehicleId": "4567"
        }
        dispatch = Dispatch(data)
        geocode_response = dispatch.requestForwardGeocoding()
        coordinate = Dispatch.getCoordinateFromGeocodeResponse(geocode_response)
        expected_answer = True
        actual_answer = False
        if comma_character in coordinate:
            actual_answer = True
        self.assertEqual(actual_answer, expected_answer)

    # test case: checks if there is a space in the getCoordinateFromGeocodeResponse return value
    def test_getCoordinateFromGeocodeResponse_space(self):
        space_character = " "
        data = {
            "_id": "1234",
            "orderId": "4321",
            "pluginType": "1",
            "orderDestination": "801 Red River St, Austin, TX 78701",
            "status": "available",
            "vehicleId": "4567"
        }
        dispatch = Dispatch(data)
        geocode_response = dispatch.requestForwardGeocoding()
        coordinate = Dispatch.getCoordinateFromGeocodeResponse(geocode_response)
        expected_answer = False
        actual_answer = False
        if space_character in coordinate:
            actual_answer = True
        self.assertEqual(actual_answer, expected_answer)
if __name__ == '__main__':
    unittest.main()
