# Webhook test
## Introduction

## Service description
For testing purposes, you can run the service by setting up a virtual environment (we used Python 2.7 in our development), installing all the modules in requirements.txt and then run
```
python wsgi.py
```
in the application directory. You may want to set both `use_reloader` and `use_debugger` to True, when developing. Alternatively, you can run the service in a Docker container (see instructions below). With the service running locally, you can do
```
curl -H "Authorization: Bearer <WEBHOOK_REGISTRATION_TOKEN>" -H "Content-Type: application/json" -X POST -d '{"user_email":"you@email.bar", "user_id":"blablabla"}' http://localhost:9000/webhooks/account
```
where `WEBHOOK_REGISTRATION_TOKEN` is the one specified in the application configuration. There is probably a better way to do this or just allow anybody to create an account. A successful account creation will return a token. This token can be used next to create subscriptions, like so
```
url -H "Authorization: Bearer <access token>" -H "Content-Type: application/json" -X POST -d '{"event":"<event string>", "url":"<callback URL>"}' http://localhost:9000/webhooks/subscribe
```
where the `access token` is the token provided in the previous step. The `event string` is for example `relation_added`. This is everything that is needed from the subscriber point of view.

The event generator will be using the `trigger` endpoint:
```
url -H "Authorization: Bearer <WEBHOOK_TRIGGER_TOKEN>" -H "Content-Type: application/json" -X POST -d '<post data>' http://localhost:9000/webhooks/trigger
```
where `WEBHOOK_TRIGGER_TOKEN` is the one specified in the application configuration.

## Endpoints
# Accounts endpoint: /account

# Subscription endpoint: /subscribe

# Event trigger endpoint: /trigger
Note: currently events submitted (to be more precise: the event payloads), are currently stored as serialized JSON in a database table.
      A better solution is probably to use Redis

## Docker

### Build image

```
docker build -t webhooktest:latest .
```

### Run container

```
mkdir $HOME/tmp/
docker run -d -p 9000:9000 -v $HOME/tmp:/tmp --name webhooktest webhooktest
```
