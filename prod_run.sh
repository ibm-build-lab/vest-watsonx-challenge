#!/bin/bash

# Quick and dirty, start slack app as background process.
# Ideally should maybe be 2 Docker containers ? (future problem)
exec python ./server/slack_app.py &
exec python ./server/server.py
