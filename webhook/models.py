"""
Models use to define the database

The database is not initiated here, but a pointer is created named db. This is
to be passed to the app creator within the Flask blueprint.
"""

from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql


db = SQLAlchemy()

class Accounts(db.Model):
    """
    Accounts table
    """
    __bind_key__ = 'webhooks'
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String)
    user_email = db.Column(db.String)
    access_token = db.Column(db.String)

    def __repr__(self):
        return '<User {0}, {1}, {2}>'\
            .format(self.id, self.user_id, self.access_token)

class Subscriptions(db.Model):
    """
    Subscriptions table
    """
    __bind_key__ = 'webhooks'
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    feedback_url = db.Column(db.String)
    event = db.Column(db.String)
    failure_count = db.Column(db.Integer)
    is_active = db.Column(db.Boolean)

    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

    def __repr__(self):
        return '<User {0}, {1}, {2}, {3}, {4}, {5}>'\
            .format(self.id, self.user_id, self.feedback_url, self.event, self.failure_count, self.is_active)

class Events(db.Model):
    """
    Events table
    """
    __bind_key__ = 'webhooks'
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String) # e.g. "citation.software.detected"
    event_time = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    event_data = db.Column(db.String)
    event_md5  = db.Column(db.String)

    def __repr__(self):
        return '<User {0}, {1}, {2}, {3}, {4}>'\
            .format(self.id, self.event, self.event_time, self.event_data, self.event_md5)

class Resend(db.Model):
    """
    When sending an event fails, keep track so we can try again
    """
    __bind_key__ = 'webhooks'
    __tablename__ = 'resend'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id  = db.Column(db.String, db.ForeignKey('accounts.user_id'))
    feedback_url = db.Column(db.String)

    def __repr__(self):
        return '<User {0}, {1}, {2}, {3}>'\
            .format(self.id, self.event_id, self.user_id, self.feedback_url)
