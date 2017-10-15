# Webhook test
## Introduction
This repo represents a skeleton webhook implementation. It is modeled after a Flask-based microservice. Different usage modes correspond with different endpoint/views. The idea is to subscribe to particular events by providing a definition of the event you receive data for and the URL on which you want to receive that data. This data (JSON) will be submitted through a POST request by the webhook service to the specified URL.

## implementation details
For testing purposes, you can run the service by setting up a virtual environment (we used Python 2.7 in our development), installing all the modules in requirements.txt and then run
```
python wsgi.py
```
in the application directory. You may want to set both `use_reloader` and `use_debugger` to True, when developing. Alternatively, you can run the service in a Docker container (see instructions below).

The intended use of this webhook service is the following. From the `consumer` perspective:

1. First create a user account, which will return a access token if successful
2. With the access token, create one or more subscriptions by providing an event type and an associated callback URL to which event data,  corresponding to the event type, will be posted

Clearly, the account creation flow needs to be replaced by something else, unless the service needs to be kept `closed`, where only prior knowledge of the proper token will allow the creation of a user account. Alternatively, an OAuth-based authentication system could be implemented or, in at the other extreme end of the permission spectrum, the account creation can be left completely open. Within the specific context of an existing service, like the ADS, any user with a service account could be allowed to subscribe to events.

In the current implementation, no form of authentication can be specified in conjunction with the callback URL. If there is e.g. an access token needed for posts to that URL, the token will have to be part of the URL provided. Extending the system to allow the specification of the most common types of authentication should not be hard.

There is also a `provider` perspective:

1. With the right token, a provider can post event data (the `payload`), which will then be wrapped in some top level metadata and sent on to callback URLs that subscribed to this kind of event

Currently, all submitted events are stored in an `events` table in the SQLite database. Specifically SQLite is not a suitable choice for production implementations, but even higher-end SQL solutions (like PostgreSQL) may not be the best choice either. Storing event data in a store like `Redis` is probably the preferred solution, for scalability and functionality reasons.

With the service running locally, you can do
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

Currently the only database backend is a SQLite database.

## Endpoints
# Accounts endpoint: /account

The data submitted to the `account` endpoint is stored in the `Accounts` table in the database. Currently, a user identifier (a string, like e.g. the user name), an email account (where a user wants to receive notifications) and the access token, generated for the user, will be stored in this table. In the prototype webhook service, only POST requests are accepted on this endpoint, for the creation of user accounts.

# Subscription endpoint: /subscribe

The `subscribe` endpoint, accepts POST data that will be used to define subscriptions for a particular user to specific events; one subscription for per event type. If a user wants one particular event type to be sent to multiple callback URLs, they will have to submit as many subscriptions. The data will be stored in the `Subscriptions` table. Besides the data submitted by the user, this table has two additional columns: the column `failure_count` that tallies the number of failed attempts when posting event data to the callback URL defined for this subscription and the column `is_active` which will be set to `False` when the failure count exceeds the maximum allowable count. A `failed attempt` is defined as a POST request to the callback URL that returns an HTTP status code other than `200`. Lastly, the `Subscriptions` table contains a user identifier column which is a foreign key to the corresponding column in the `Accounts` table.

# Event trigger endpoint: /trigger

When a service submits event data to the `trigger` endpoint (with the correct token), an entry in the `Events` table is created, before data is sent out to the appropriate callback URLs. A entry in the `Events` column consists of a string containing the `event type` (like "relation_added"), a time of the event (in UTC), the serialized JSON of the event and the md5sum of payload contents. The md5sum entry will be used to check whether an event was already submitted. If the webhook service is not required to make any decision on whether or not to send out data to callback URLs, this functionality is not necessary. Especially, if events are to be kept from "day 1", this is not a desirable feature, since the re-emission of events must be supported; after a relation is deleted, it may get added again if its deletion turned out to be incorrect. From a implementation and scalability point of view, storing events in a database table may not be the best solution, even if the underlying database is capable of dealing with large amounts of data. Since filtering of events may be a desirable requirement, a solution like `Redis` may be more appropriate.

In addition to the `Events` table, there is a `Resend` table. This table is there to support the resending of event data to certain callback URLs after a failed attempt. In the prototype implementation of the webhook service, the resending of events is implemented as a `Flask-Script` command, which will allow this functionality to be implemented as a cron job.

## Docker

The most convenient way to test or implement the prototype webhook service is virtualize it, for example using `Vagrant` or `Docker`, or a combination of both. A `Dockerfile` has been included. The Flask application uses some configuration variables that will contain sensitive information; a `local_config.py` can be used to override the default settings set in `config.py`. Below are the steps to build and deploy the Docker container.

Caveat: some anomalous behavior was observed when deploying the Docker container under MacOS. The Docker image was built successfully and when the Docker container was created, it seemed to be running. However, `gunicorn` was in an anomalous state, where it was re-starting continuously. Following the exact same building procedure on CentOS and Ubuntu systems, a fully functional Docker container was created with the webhook service functioning as intended and described above.

### Build image

```
docker build -t webhooktest:latest .
```

### Run container

```
mkdir $HOME/tmp/
docker run -d -p 9000:9000 -v $HOME/tmp:/tmp --name webhooktest webhooktest
```
