from __future__ import division
from flask import Flask, request, redirect, url_for, render_template, jsonify, Markup

import os, requests
import hashlib
import datetime, time, json
from datetime import datetime, timedelta
from os import curdir, sep
from http.server import BaseHTTPRequestHandler, HTTPServer

# from flask_heroku import Heroku

from random import randint
import random

from db_setup import Subject, Portfolio, ChoiceProblem, Selection, db, app

import cgi
import collections, itertools

#from alpha_vantage.timeseries import TimeSeries

#import matplotlib.pyplot as plt
x = [3,3,3,1,1,1,1,2,3,4]
random.shuffle(x)
print(x)
