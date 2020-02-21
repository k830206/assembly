"""
Initialize Flask App
"""
import os
import logging
from flask import Flask
import yaml
from weather import endpoint    # Register the blueprint

__APPLICATION_CONFIG__ = 'resources/application.yaml'


def create_app(test_config=None):
    """
    Create a Flask instance
    :param test_config:
    :return:
    """
    logging.basicConfig(level=logging.INFO)

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # load the instance config, if it exists, when not testing
    with open(os.path.abspath(__APPLICATION_CONFIG__)) as config_obj:
        app_config = yaml.load(config_obj, Loader=yaml.FullLoader)

    app.config.update(app_config)

    if test_config is not None:
        # load the test config if passed in
        app.config.update(test_config)

    app.register_blueprint(endpoint.bp)

    return app
