
from flask import request
from flask import current_app
from flask_restful import Resource
from datetime import datetime
import requests
import hashlib
import json
import sys
from ..models import db, Subscriptions, Events, Resend

class Triggering(Resource):

    def post(self):
        """
        Submits new webhook event
        """
        if 'Bearer' not in request.headers['Authorization']:
            return {'error': '"{Bearer}" missing from "Authorization" header'}, 401
        # We received an access token
        try:
            access_token = request.headers['Authorization'].split()[1]
        except:
            return {'error': 'Improperly formatted "Authorization" header'}, 401
        TRIGGER_TOKEN = current_app.config.get('WEBHOOK_TRIGGER_TOKEN')
        # Is it the correct token?
        if access_token != TRIGGER_TOKEN:
            return {'error': 'incorrect trigger token was provided'}, 401
        # The token supplied was correct: accept the event
        # Do some basic checking regarding acceptability
        try:
            event = request.json['event']
        except:
            return {'error': 'no event was provided'}, 500
        try:
            event_payload = request.json['payload']
        except:
            return {'error': 'no payload was provided'}, 500
        # Maximum number of attempts to send events to a certain callback URL
        max_tries = current_app.config.get('MAX_SEND_ATTEMPTS')
        # Add an entry to the events database
        event_time = datetime.utcnow()
        # Did we already see this event:
        new_event = True
        e = Events.query.filter(Events.event_md5 == hashlib.md5(json.dumps(request.json, sort_keys=True)).hexdigest()).first()
        # If the above query returned a result, we already have this event
        if e:
            sys.stderr.write('Already saw this event. Skipping...\n')
            new_event = False
        # If we have a new event, add it to the Events table
        if new_event:
            try:
                ne = Events(
                    event = event,
                    event_time = event_time,
                    event_data = json.dumps(request.json, sort_keys=True),
                    event_md5  = hashlib.md5(json.dumps(request.json, sort_keys=True)).hexdigest()
                )
                db.session.add(ne)
                db.session.commit()
            except Exception, e:
                return {'error':'error adding event to database: {0}'.format(e)}, 500
        # Get all the subscriptios for this event
        subs_list = []
        res = Subscriptions.query.filter(Subscriptions.event == event).all()
        for r in res:
            if r.is_active:
                subs_list.append(r)
        # Send the event of to its subscribers
        if new_event:
            # we are just proxying whatever was submitted
            for s in subs_list:
                # prepare the data to be POST-ed
                # First get the default values for the payload
                data = current_app.config.get('DEFAULT_EVENT_DATA')
                # Now update it with actual values
                data["id"] = ne.id
                data["description"] = "ADS citation events"
                data["creator"] = "ADS"
                data["source"] = "ADS.Discovery"
                data["time"] = str(event_time.strftime('%s'))
                data["event"] = event
                data["payload"] = event_payload
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                success = True
                try:
                    r = requests.post(s.feedback_url, data=json.dumps(data), headers=headers)
                except:
                    success = False
                if not success or r.status_code != 200:
                    # Something went wrong, so we need to keep track of this
                    # Update the user subscription
                    failures = s.failure_count + 1
                    if failures < max_tries:
                        # Failure, but we'll try again
                        # Update the database
                        s.failure_count = failures
                        db.session.commit()
                        # Add an entry to the Resend table
                        try:
                            rs = Resend(
                                event_id = ne.id,
                                user_id = s.user_id,
                                feedback_url = s.feedback_url
                            )
                            db.session.add(rs)
                            db.session.commit()
                        except:
                            sys.stderr.write('error updating Resend table\n')
                            continue
                    else:
                        # Too many failures, subscription will get deactivated
                        s.is_active = False
                        db.session.commit()

        return 200
