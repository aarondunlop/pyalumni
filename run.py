from __future__ import absolute_import
#from flask_bootstrap import Bootstrap
#from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_login import *
from wtforms import Form, TextField, SelectField, BooleanField, StringField, PasswordField, validators, TextAreaField, IntegerField, HiddenField
#from wtforms.widgets import TextArea
#from wtforms.validators import Required, Length, InputRequired, EqualTo, Email
from flask import * #flash, current_app, request, render_template, redirect, url_for, flask, jsonify
import csv, os, time, json
import logging
#from collections import OrderedDict
from argon2 import PasswordHasher, exceptions
from itsdangerous import Signer, TimedSerializer, TimestampSigner, URLSafeTimedSerializer
from pprint import pprint
from types import *
import operator
from time import strftime
from datetime import datetime
from operator import itemgetter, attrgetter, methodcaller
import ConfigParser
from urlparse import urlparse, urljoin
from flask import request, url_for
#import decimal
from sqlalchemy.ext.serializer import loads, dumps
#import json

#from os import sys
#sys.path.append('/var/www/pyalumni/app')

from pyalumni.app import app

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=9045)
