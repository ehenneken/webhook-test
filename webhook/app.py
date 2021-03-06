# encoding: utf-8
"""
Application
"""
# General modules
import logging.config
from flask import Flask
from flask_restful import Api
# We want to support resource inspection
from flask_discoverer import Discoverer
# application-specific modules
from views import Account
from views import Subscription
from views import Triggering
from models import db

def create_app():
    """
    Create the application and return it to the user
    :return: application
    """

    app = Flask(__name__, static_folder=None)
    app.url_map.strict_slashes = False

    load_config(app)
    logging.config.dictConfig(
        app.config['WEBHOOKS_LOGGING']
    )

    # Register extensions
    api = Api(app)
    Discoverer(app)
    db.init_app(app)

    # Add the end resource end points
    # The account end-point supports interactions with user accounts
    api.add_resource(Account,
                     '/account',
                     methods = ['POST'])
    # The subscribe end-point allows users to suubscribe to events
    api.add_resource(Subscription,
                     '/subscribe',
                     methods = ['POST'])
    # The trigger endpoint is where event-producing entities send their data to
    api.add_resource(Triggering,
                     '/trigger',
                     methods = ['POST'])

    return app


def load_config(app):
    """
    Loads configuration in the following order:
        1. config.py
        2. local_config.py (ignore failures)
    :param app: flask.Flask application instance
    :return: None
    """

    app.config.from_pyfile('config.py')

    try:
        app.config.from_pyfile('local_config.py')
    except IOError:
        app.logger.warning('Could not load local_config.py')

if __name__ == '__main__':
    app_ = create_app()
    app_.run(debug=True, use_reloader=False)
