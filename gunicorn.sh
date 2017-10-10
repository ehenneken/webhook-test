#!/bin/bash

mkdir -p /tmp/cache
rm -fr /tmp/cache/*

# if stale, gunicorn refuses to start
rm /tmp/gunicorn*.pid

pushd /app
gunicorn -c gunicorn.conf.py wsgi:application
