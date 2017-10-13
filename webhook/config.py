# encoding: utf-8
"""
Configuration file. Please prefix application specific config values with
the application name.
"""

import os
import pwd

# This token is to allow processes to submit even data to this service
WEBHOOK_TRIGGER_TOKEN = 'very secret token'
# Token necessary to create a user account (temporary - will need better solution)
WEBHOOK_REGISTRATION_TOKEN = 'another very secret token'
# The service will attempt this amount of delivery attempts before a callback
# URL is deactivated
MAX_SEND_ATTEMPTS = 5
# Keep definition of event data out of application?
# This will be used in more than one place of the service, so it makes sense
# to define the structure only once. Alternative: define it in a module/class?
DEFAULT_EVENT_DATA = {
    "id":"will hold user id",
    "event": "will hold event string",
    "creator": "ADS",
    "source": "ADS.Discovery",
    "description": "ADS events",
    "time": "time stamp of event",
    "payload": [{}],
}
# Database backend used by service
SQLALCHEMY_BINDS = {
    'webhooks': 'sqlite:////tmp/testdb.db'
}
# Allow definition of deployment type through environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'staging').lower()
# Logging definitions
# Define where the application will log to
LOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')
)
LOG_PATH = '{home}/logs/'.format(home=LOG_PATH)
# and create the directory if it isn't there
if not os.path.isdir(LOG_PATH):
    os.mkdir(LOG_PATH)
# 
WEBHOOKS_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s\t%(process)d '
                      '[%(asctime)s]:\t%(message)s',
            'datefmt': '%m/%d/%Y %H:%M:%S',
        }
    },
    'handlers': {
        'file': {
            'formatter': 'default',
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/{0}/webhooks.app.{1}.log'.format(LOG_PATH, ENVIRONMENT),
        },
        'console': {
            'formatter': 'default',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
