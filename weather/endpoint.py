"""
Weather endpoint /v1
"""
from flask import Blueprint
from flask import request
from flask import current_app as app
from weather.messages import EMPTY_CITY_NAME
from weather.weather_request import WeatherRequest

# pylint: disable=invalid-name
bp = Blueprint('v1', __name__, url_prefix='/v1')

__CITY_KEY__ = 'city'


@bp.route('/weather', methods=['GET'])
def get_weather_data():
    """
    Endpoint: /v1/weather?city=<City name>
    :return:
    """
    if __CITY_KEY__ in request.args.keys():
        weather_request = WeatherRequest(app.config)
        city_name = request.args.get('city')

        if len(city_name) > 0:
            return weather_request.get_weather_data(city_name)

    return EMPTY_CITY_NAME
