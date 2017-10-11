import uuid

from flask import request
from flask import current_app
from flask_restful import Resource

from ..models import db, Accounts

class Account(Resource):
    """
    Handles the (webhook) subscriptions table interactions
    """

    def post(self):
        """
        Creates new subscription
        An account registration is supposed to be submitted via a POST
        request of the type
        $ curl -X POST \
          > -H "Authorization: Bearer <your registration token>" \
          > -H "Content-Type: application/json" \
          > -d '{"user_id": "<your user identifier>"}' \
          > http://<some url here>/account
        """
        if 'Bearer' not in request.headers['Authorization']:
            return {'error': '"{Bearer}" missing from "Authorization" header'}, 401
        # We received an access token
        try:
            access_token = request.headers['Authorization'].split()[1]
        except:
            return {'error': 'Improperly formatted "Authorization" header'}, 401
        REGISTRATION_TOKEN = current_app.config.get('WEBHOOK_REGISTRATION_TOKEN')
        # Is it the correct token?
        if access_token != REGISTRATION_TOKEN:
            return {'error': 'incorrect registration token was provided'}, 401
        # The token supplied was correct: accept the subscription
        # First check if there is an account already for the email provided
        # Check is the account exists
        try:
            user_id = request.json['user_id']
        except:
            return {'error': 'No "user_id" provided in authentication request'}, 401
        account = Accounts.query.filter(Accounts.user_id == user_id).first()
        token = str(uuid.uuid4())
        if not account:
            try:
                acc = Accounts(user_id = user_id, access_token = token)
                db.session.add(acc)
                db.session.commit()
            except Exception, e:
                sys.stderr.write('Failed creating user account: {0}\n'.format(e))
                return  {'error': 'Failed creating user account'}, 500
        else:
            token = account.access_token

        return token
