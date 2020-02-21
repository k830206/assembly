"""Test Case for WeatherRequest class"""
import json
from unittest import TestCase
from unittest.mock import patch
from weather.weather_request import WeatherRequest
import time
import datetime


class MockResponse:
    def __init__(self, status_code=200, reason=None, text=None):
        self.status_code = status_code
        self.reason = reason
        self.text = text


class TestWeatherRequest(TestCase):
    """Test Case class definition"""

    __PAYLOAD_PATH__ = 'tests/payloads/%s'
    __EXPECTED_PATH__ = 'tests/expected/%s'
    __WEATHER_STACK_FILE__ = 'weather_stack.json'
    __OPEN_WEATHER_MAP_FILE__ = 'open_weather_map.json'

    def setUp(self):
        config = {
            'WEATHER_STACK': {
                'API_KEY': 'testkey',
                'URL': 'http://dummy.local?key=%s&city=%s'
            },
            'OPEN_WEATHER_MAP': {
                'API_KEY': 'testkey',
                'URL': 'http://dummy.local?key=%s&city=%s'
            }
        }

        self.weather_request = WeatherRequest(config)

    def test_get_weather_stack_data(self):
        with open(self.__EXPECTED_PATH__ % self.__WEATHER_STACK_FILE__) as expected_file_obj:
            expected_data = json.load(expected_file_obj)

        with patch('requests.request') as mock_request:
            with open(self.__PAYLOAD_PATH__ % self.__WEATHER_STACK_FILE__, 'r') as file_obj:
                json_str = file_obj.read()

            mock_request.return_value.status_code = 200
            mock_request.return_value.text = json_str

            result_data = self.weather_request.get_weather_stack_data('Melbourne')

        self.assertDictEqual(result_data, expected_data, 'Output JSON object is not matched')

    def test_get_weather_stack_with_server_error(self):
        expected_data = dict()
        expected_data['error_code'] = 500
        expected_data['error_message'] = 'Internal Error'

        with patch('requests.request') as mock_request:
            mock_request.return_value.status_code = expected_data['error_code']
            mock_request.return_value.reason = expected_data['error_message']
            mock_request.return_value.text = ''

            result_data = self.weather_request.get_weather_stack_data('Melbourne')

            self.assertDictEqual(expected_data, result_data,
                                 'It should return error message JSON if a provider is down')

    def test_get_weather_stack_with_empty_response(self):
        with patch('requests.request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.text = ''

            result_data = self.weather_request.get_weather_stack_data('Melbourne')

            self.assertIsNone(result_data, 'It should return None if it gives empty responses')

    def test_get_open_weather_map_data(self):
        with open(self.__EXPECTED_PATH__ % self.__OPEN_WEATHER_MAP_FILE__) as expected_file_obj:
            expected_data = json.load(expected_file_obj)

        with patch('requests.request') as mock_request:
            with open(self.__PAYLOAD_PATH__ % self.__OPEN_WEATHER_MAP_FILE__, 'r') as file_obj:
                json_str = file_obj.read()

            mock_request.return_value.status_code = 200
            mock_request.return_value.text = json_str

            result_data = self.weather_request.get_open_weather_map_data('Melbourne')

        self.assertDictEqual(result_data, expected_data, 'Output JSON object is not matched')

    def test_get_open_weather_map_with_empty_reponses(self):
        with patch('requests.request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.text = ''

            result_data = self.weather_request.get_open_weather_map_data('Melbourne')

            self.assertIsNone(result_data, 'It should return None if it gives empty responses')

    def test_get_open_weather_map_with_server_error(self):
        """Test for server exception for OpenWeatherMap"""
        expected_data = dict()
        expected_data['error_code'] = 500
        expected_data['error_message'] = 'Internal Error'

        with patch('requests.request') as mock_request:
            mock_request.return_value.status_code = expected_data['error_code']
            mock_request.return_value.reason = expected_data['error_message']
            mock_request.return_value.text = ''

            result_data = self.weather_request.get_open_weather_map_data('Melbourne')

        self.assertDictEqual(expected_data, result_data,
                             'It should return error message JSON if a provider is down')

    def test_get_weather_data_from_cache(self):
        with open(self.__EXPECTED_PATH__ % self.__OPEN_WEATHER_MAP_FILE__) as expected_file_obj:
            expected_data = json.load(expected_file_obj)

        self.weather_request.__last_weather_data__ = dict()
        self.weather_request.__last_weather_data__['data'] = expected_data
        self.weather_request.__last_weather_data__['timestamp'] = time.time()

        result_data = self.weather_request.get_weather_data('Melbourne')

        self.assertDictEqual(expected_data, result_data, 'It should return cached data')

    def test_get_weather_data_from_primary(self):
        with open(self.__EXPECTED_PATH__ % self.__WEATHER_STACK_FILE__) as expected_file_obj:
            expected_data = json.load(expected_file_obj)

        with patch('requests.request') as mock_request:
            with open(self.__PAYLOAD_PATH__ % self.__WEATHER_STACK_FILE__, 'r') as file_obj:
                json_str = file_obj.read()

            mock_request.side_effect = [
                MockResponse(200, None, json_str),
                MockResponse(500, 'Dummy Reason', None)
            ]

            result_data = self.weather_request.get_weather_data('Melbourne')

        self.assertDictEqual(result_data, expected_data, 'Output JSON object is not matched')

    def test_get_weather_data_from_secondary(self):
        with open(self.__EXPECTED_PATH__ % self.__OPEN_WEATHER_MAP_FILE__) as expected_file_obj:
            expected_data = json.load(expected_file_obj)

        with patch('requests.request') as mock_request:
            with open(self.__PAYLOAD_PATH__ % self.__OPEN_WEATHER_MAP_FILE__, 'r') as file_obj:
                json_str = file_obj.read()

            mock_request.side_effect = [
                MockResponse(500, 'Dummy Reason', None),
                MockResponse(200, None, json_str)
            ]

            result_data = self.weather_request.get_weather_data('Melbourne')

        self.assertDictEqual(result_data, expected_data, 'Output JSON object is not matched')

    def test_get_weather_data_after_four_seconds(self):
        with open(self.__EXPECTED_PATH__ % self.__OPEN_WEATHER_MAP_FILE__) as expected_file_obj:
            cached_data = json.load(expected_file_obj)

        with open(self.__EXPECTED_PATH__ % self.__WEATHER_STACK_FILE__) as expected_file_obj:
            expected_data = json.load(expected_file_obj)

        self.weather_request.__last_weather_data__ = dict()
        self.weather_request.__last_weather_data__['data'] = cached_data
        self.weather_request.__last_weather_data__['timestamp'] = \
            time.mktime((datetime.datetime.now() - datetime.timedelta(seconds=4)).timetuple())

        with patch('requests.request') as mock_request:
            with open(self.__PAYLOAD_PATH__ % self.__WEATHER_STACK_FILE__, 'r') as file_obj:
                json_str = file_obj.read()

            mock_request.side_effect = [
                MockResponse(200, None, json_str),
                MockResponse(500, 'Dummy Reason', None)
            ]

            result_data = self.weather_request.get_weather_data('Melbourne')

        self.assertDictEqual(result_data, expected_data, 'Output JSON object is not matched')

    def test_get_weather_data_when_both_providers_down(self):
        with open(self.__EXPECTED_PATH__ % self.__WEATHER_STACK_FILE__) as expected_file_obj:
            expected_data = json.load(expected_file_obj)

        with patch('requests.request') as mock_request:
            with open(self.__PAYLOAD_PATH__ % self.__WEATHER_STACK_FILE__, 'r') as file_obj:
                json_str = file_obj.read()

            mock_request.side_effect = [
                MockResponse(200, None, json_str),
                MockResponse(500, 'Dummy Reason', None),
                MockResponse(500, 'Dummy Reason', None)
            ]

            self.weather_request.get_weather_data('Melbourne')
            result_data = self.weather_request.get_weather_data('Melbourne')

        self.assertDictEqual(result_data, expected_data, 'Output JSON object is not matched')

    def test_get_error_data_when_both_providers_down_and_no_cache(self):
        with patch('requests.request') as mock_request:
            mock_request.side_effect = [
                MockResponse(500, 'Dummy Reason 1', None),
                MockResponse(500, 'Dummy Reason 2', None)
            ]

            result_data = self.weather_request.get_weather_data('Melbourne')

            error_data = dict()
            error_data['error_code'] = 500
            error_data['error_message'] = 'Dummy Reason 2'

        self.assertDictEqual(result_data, error_data, 'Error data is not populated')



