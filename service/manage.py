"""
Alembic migration management file
"""
import os
import sys
PROJECT_HOME = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_HOME)
from flask.ext.script import Manager, Command, Option
from flask.ext.migrate import Migrate, MigrateCommand
from models import db, Resend, Events
from service.app import create_app

# Load the app with the factory
app = create_app()


class CreateDatabase(Command):
    """
    Creates the database based on models.py
    """
    @staticmethod
    def run(app=app):
        """
        Creates the database in the application context
        :return: no return
        """
        with app.app_context():
            db.create_all()
            db.session.commit()


class DestroyDatabase(Command):
    """
    Creates the database based on models.py
    """
    @staticmethod
    def run(app=app):
        """
        Creates the database in the application context
        :return: no return
        """
        with app.app_context():
            db.drop_all()
            # db.session.remove()

class ResendEvents(Command):
    """
    Goes through previously failed attempts and tries again
    """
    @staticmethod
    def run(app=app):
        """
        Creates the database in the application context
        :return: no return
        """
        with app.app_context():
            event2descr = app.config.get('EVENT_DESCRIPTIONS')
            retries = Resend.query.all()
            for retry in retries:
                event = Events.query.filter(Events.id == retry.event_id).first()
                evt = "{0}.{1}.{2}".format(event.data_type, event.record_type, event.event)
                event_data = {
                    "event": event2descr.get(evt),
                    "citing_bibcode": event.citing_bibcode,
                    "cited_bibcode": event.cited_bibcode,
                    "cited_id": event.cited_id
                }
                data = app.config.get('DEFAULT_PAYLOAD')
                data["account_id"] = retry.user_id
                data["event"] = evt
                data["time_stamp"] = event.event_time.strftime('%s')
                data["event_data"] = event_data
#                data = {
#                    "account_id":retry.user_id,
#                    "event": evt,
#                    "description": "ADS citation events",
#                    "time_stamp": event.event_time.strftime('%s'),
#                    "event_data": event_data,           
#                }
                


# Set up the alembic migration
migrate = Migrate(app, db, compare_type=True)

# Setup the command line arguments using Flask-Script
manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('createdb', CreateDatabase())
manager.add_command('destroydb', DestroyDatabase())
manager.add_command('resend', ResendEvents())

if __name__ == '__main__':
    manager.run()
