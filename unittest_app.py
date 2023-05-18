import unittest
from flask import Flask
import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_get_weather(self):
        with self.app.test_request_context('/api/weather?date=19850101&station_id=110072'):
            response = app.get_weather()
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data[0].get('precipitation'), 94)


    def test_get_weather_stats(self):
        with self.app.test_request_context('/api/weather/stats?date=2000&station_id=252020'):
            response = app.get_weather_stats()
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data[0].get('avg_max_temp'), -1609.473)


if __name__ == '__main__':
    unittest.main()
