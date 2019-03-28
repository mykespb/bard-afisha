#!/usr/bin/env python
#coding: utf-8


# adapter.wsgi

import sys, os

sys.path = ['/var/www/bard-afisha/'] + sys.path

os.chdir(os.path.dirname(__file__))

import bottle
import main

application = bottle.default_app()
