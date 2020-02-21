"""
Weather Request class definition
"""
import logging
import json
import time
import requests
from weather.messages import EMPTY_CITY_NAME


class WeatherRequest:
    """
    Weather Request implementation
    """
    __DEFAULT_CITY__ = 'Melbourne'
    __REQUEST_METHOD__ = 'GET'
    __WEATHER_STACK_KEY__ = 'WEATHER_STACK'
    __OPEN_WEATHER_KEY__ = 'OPEN_WEATHER_MAP'
    __API_KEY__ = 'API_KEY'
    __URL_KEY__ = 'URL'

    __WIND_SPEED_KEY__ = 'wind_speed'
    __TEMPERATURE_DEGREES__ = 'temperature_degrees'
    __ERROR_MESSAGE__ = 'error_message'
    __ERROR_CODE__ = 'error_code'

    __config__ = dict()
    __last_weather_data__ = None

    __WEATHER_DATA__ = 'data'
    __WEATHER_TIMESTAMP__ = 'timestamp'
    ___REFRESH_INTERVAL__ = 3.0

    def __init__(self, config):
        self.__config__ = config

    @staticmethod
    def get_celsius(kelvin):
        """Convert Kelvin to Celsius"""
        return float(format(float(kelvin) - 273.15, '.2f'))

    @staticmethod
    def get_hourly_wind_speed(meter_sec_data):
        """Covert meter/sec to kilometer/hour"""
        return float(format(float(meter_sec_data) * 60 * 60 / 1000, '.2f'))

    def get_weather_stack_data(self, city_name):
        """Get data from WeatherStack"""
        config = self.__config__[self.__WEATHER_STACK_KEY__]

        if city_name is not None:
            request_url = config[self.__URL_KEY__] % (config[self.__API_KEY__], city_name)

            res = requests.request(self.__REQUEST_METHOD__, request_url)

            if res.status_code == 200:
                if (res.text is not None) and (len(res.text) > 2):
                    logging.debug('Response from WeatherStack: %s', res.text)

                    weather_data = json.loads(res.text)
                    current_data = weather_data['current']

                    result_data = dict()
                    result_data[self.__WIND_SPEED_KEY__] = int(current_data['wind_speed'])
                    result_data[self.__TEMPERATURE_DEGREES__] = int(current_data['temperature'])

                    logging.debug('Result: %s', str(result_data))

                    return result_data
            else:
                result_data = dict()
                result_data[self.__ERROR_CODE__] = res.status_code
                result_data[self.__ERROR_MESSAGE__] = res.reason

                return result_data

        return None

    def get_open_weather_map_data(self, city_name):
        """Get data from OpenWeatherMap"""
        config = self.__config__[self.__OPEN_WEATHER_KEY__]

        if city_name is not None:
            request_url = config[self.__URL_KEY__] % (config[self.__API_KEY__], city_name)

            res = requests.request(self.__REQUEST_METHOD__, request_url)

            if res.status_code == 200:
                if (res.text is not None) and (len(res.text) > 2):
                    logging.debug('Response from OpenWeatherMap: %s', res.text)

                    weather_data = json.loads(res.text)

                    result_data = dict()
                    result_data[self.__WIND_SPEED_KEY__] = \
                        self.get_hourly_wind_speed(weather_data['wind']['speed'])
                    result_data[self.__TEMPERATURE_DEGREES__] = \
                        self.get_celsius(weather_data['main']['temp'])

                    logging.debug('Result: %s', str(result_data))

                    return result_data
            else:
                result_data = dict()
                result_data[self.__ERROR_CODE__] = res.status_code
                result_data[self.__ERROR_MESSAGE__] = res.reason

                return result_data

        return None

    def get_weather_data(self, city_name=__DEFAULT_CITY__):
        """Get data from primary/secondary providers"""
        error_response = dict()

        if city_name is None:
            error_response[self.__ERROR_CODE__] = 500
            error_response[self.__ERROR_MESSAGE__] = EMPTY_CITY_NAME

            return error_response

        if (self.__last_weather_data__ is None) or \
                (time.time() - self.__last_weather_data__[self.__WEATHER_TIMESTAMP__]) > 3.0:
            try:
                weather_data = self.get_weather_stack_data(city_name)
            # pylint: disable=broad-except
            except BaseException:
                weather_data = None

            if weather_data is None or self.__ERROR_CODE__ in weather_data.keys():
                try:
                    weather_data = self.get_open_weather_map_data(city_name)
                # pylint: disable=broad-except
                except BaseException:
                    weather_data = None

            if weather_data is None or self.__ERROR_CODE__ in weather_data.keys():
                if self.__last_weather_data__ is None:
                    return weather_data
            else:
                self.__last_weather_data__ = dict()
                self.__last_weather_data__[self.__WEATHER_DATA__] = weather_data
                self.__last_weather_data__[self.__WEATHER_TIMESTAMP__] = time.time()

        return self.__last_weather_data__[self.__WEATHER_DATA__]
