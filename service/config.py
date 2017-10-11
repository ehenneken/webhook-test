# encoding: utf-8
"""
Configuration file. Please prefix application specific config values with
the application name.
"""

import os
import pwd

LOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')
)
LOG_PATH = '{home}/logs/'.format(home=LOG_PATH)

if not os.path.isdir(LOG_PATH):
    os.mkdir(LOG_PATH)

WEBHOOK_TRIGGER_TOKEN = 'very secret token'
WEBHOOK_REGISTRATION_TOKEN = 'another very secret token'
MAX_SEND_ATTEMPTS = 5
DEFAULT_PAYLOAD = {
    "id":"will hold user id",
    "event": "will hold event string",
    "creator": "ADS",
    "source": "ADS.Discovery",
    "description": "ADS events",
    "time_stamp": "time stamp of event",
    "event_data": {},
}
# sqlite:////tmp/test.db
#SQLALCHEMY_BINDS = {
#    'webhooks': 'postgresql+psycopg2://postgres:postgres@localhost:5433/testdb'
#}

SQLALCHEMY_BINDS = {
    'webhooks': 'sqlite:////Users/edwin/tmp/testdb.db'
}

ENVIRONMENT = os.getenv('ENVIRONMENT', 'staging').lower()
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
            'filename': '/tmp/webhooks.app.{}.log'.format(ENVIRONMENT),
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
