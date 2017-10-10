"""
Models use to define the database

The database is not initiated here, but a pointer is created named db. This is
to be passed to the app creator within the Flask blueprint.
"""

import uuid
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Accounts(db.Model):
    """
    Accounts table
    """
    __bind_key__ = 'webhooks'
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String)
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
    event = db.Column(db.String) # even type subscribed to, e.g. "citation.software.*"
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
    data_type = db.Column(db.String) # e.g. "citation"
    record_type = db.Column(db.String) # e.g. "software"
    event = db.Column(db.String) # e.g. "detected"
    event_time = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    citing_bibcode = db.Column(db.String)
    cited_bibcode = db.Column(db.String)
    cited_id = db.Column(db.String)
    
    def __repr__(self):
        return '<User {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}>'\
            .format(self.id, self.data_type, self.record_type, self.event, self.event_time, self.citing_bibcode, self.cited_bibcode, self.cited_id)

class Resend(db.Model):
    """
    When sending an event fails, keep track so we can try again
    """
    __bind_key__ = 'webhooks'
    __tablename__ = 'resend'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id  = db.Column(db.String, db.ForeignKey('accounts.user_id'))
    feedback_url = db.Column(db.String, unique=True)
    
    def __repr__(self):
        return '<User {0}, {1}, {2}, {3}>'\
            .format(self.id, self.event_id, self.user_id, self.feedback_url)
