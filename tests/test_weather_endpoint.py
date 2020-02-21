import json


def test_full_data(client):
    res = client.get('/v1/weather?city=melbourne')

    assert res.status_code == 200

    json_obj = json.loads(res.data)

    assert 'wind_speed' in json_obj.keys()
    assert 'temperature_degrees' in json_obj.keys()


def test_empty_city_name(client):
    res = client.get('/v1/weather?city=')

    assert res.status_code == 200
    assert res.data.decode('utf-8') == 'Empty city name'


def test_no_parameters(client):
    res = client.get('/v1/weather')

    assert res.status_code == 200
    assert res.data.decode('utf-8') == 'Empty city name'
