
from flask import request
from flask import current_app
from flask_restful import Resource

from ..models import db, Subscriptions, Accounts

class Subscription(Resource):
    """
    Handles the (webhook) subscriptions table interactions
    There can be multiple subscriptions for one user
    """

    def post(self):
        """
        Creates new subscription
        A subscription is supposed to be submitted via a POST
        request of the type
        $ curl -X POST \
          > -H "Authorization: Bearer <your access token>" \
          > -H "Content-Type: application/json" \
          > -d '{"event": "citation.*", "url": "<your callback URL>"}' \
          > http://<some url here>/subscription
        """
        if 'Bearer' not in request.headers['Authorization']:
            return {'error': '"{Bearer}" missing from "Authorization" header'}, 401
        # We received an access token
        try:
            access_token = request.headers['Authorization'].split()[1]
        except:
            return {'error': 'Improperly formatted "Authorization" header'}, 401
        # Check if we know this token
        account = Accounts.query.filter(Accounts.access_token == access_token).first()
        if not account:
            return {'error': 'incorrect subscription token was provided'}, 401
        # The token supplied was correct: accept the subscription
        try:
            url = request.json['url']
            event = request.json['event']
        except:
            return {'error': 'incorrect submission data was provided'}, 401
        # Check if we already have this subscription
        subscriptions = Subscriptions.query.filter(Subscriptions.user_id == account.user_id).all()
        for s in subscriptions:
            if s.event == event and s.feedback_url == url:
                return {'warning': 'subscription already exists'}, 200
        # Check if the subscriber subscribes to a supported event type
        AVAILABLE_EVENTS = current_app.config.get('AVAILABLE_EVENTS')
        if event not in AVAILABLE_EVENTS:
            return {'error': 'unsupported event'}, 401
        # We're good to go
        subs = Subscriptions(
            feedback_url = url,
            event = event,
            user_id = account.user_id,
            failure_count = 0,
            is_active = True
        )
        
        db.session.add(subs)
        db.session.commit()

        return 200
