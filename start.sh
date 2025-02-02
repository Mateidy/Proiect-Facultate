#!/bin/sh
gunicorn -k eventlet -w 1 main:app
