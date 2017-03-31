#from . import app
import boto3
from itsdangerous import Signer, TimedSerializer, TimestampSigner, URLSafeTimedSerializer
from flask import *
from urlparse import urlparse, urljoin
import functools

import yaml
from config import *

#boto3.set_stream_logger(name='botocore')
#boto3.set_stream_logger('boto3.resources', logging.DEBUG)
#print(main.aws_region)

s=TimestampSigner(app_secret, salt=app_salt)
ts = URLSafeTimedSerializer(app_secret)

def exit_if_last(id, opt):
    try:
        opt.pop(0)
    except:
        return True
    if opt is None or not opt:
        print('opt is empty')
        return True
    return False

def check_token(login,token):
    #print 'login is %s, token is %s' % (login, token)
    try:
        #s=TimestampSigner(app.secret_key, salt=app.salt)
        unsigned = s.unsign(token, max_age=900)
        return True
    except:
        print 'Session is invalid.'
        return False
        return redirect(url_for('logout'))

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)


class SendEmail(object):
    def __init__(self, to, subject, from_addr=from_address, charset='utf-8'):
        self.to = to #list
        self.from_addr = from_addr #list
        self.subject = '' #dict
        self._html = None
        self._text = None
        self._format = 'text'
        self._message = {}
        self._message['Subject']={}
        self._message['Subject']['Data']=self.subject
        self._message['Subject']['Charset']=charset
        self._message['Body']={}
        self._message['Body']['Text']={}
        self._message['Body']['Text']['Data']=''
        self._message['Body']['Text']['Charset']=charset
        self._message['Body']['Html']={}
        self._message['Body']['Html']['Data']=''
        self._message['Body']['Html']['Charset']=charset
        self._destination={}
        self._destination['ToAddresses']=[]
        self._destination['ToAddresses'].append(to)
        self.charset=charset

    def emailsubject(self, subject):
        print(self, subject)
        self._message['Subject']['Data']=subject

    def html(self, html):
        self._html=html
        self._message['Body']['Html']['Data']=html
        print(self._message)

    def text(self, text):
        self._text=text
        self._message['Body']['Text']['Data']=text

    def send(self, from_addr=None):
        #body.append( self._html)

        if isinstance(self.to, basestring):
            self.to = [self.to]
        if not from_addr:
            from_addr = app.from_address
        if not self._html and not self._text:
            raise Exception('You must provide a text or html body.')
        if not self._html:
            self._format = 'text'
            body = self._text
        client = boto3.client('ses', region_name=app.aws_region, aws_access_key_id=app.aws_access_key, aws_secret_access_key=app.aws_secret_key)

        print(self._message)
        print(self._destination)

        return client.send_email(
            Source= self.from_addr,
            Destination = self._destination,
            Message=self._message,
            )

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

#email = SendEmail(to='alumni@dunlops.us', subject='testing123')
#email.text('This is a text body. Foo bar.')
#email.emailsubject('Last test.')
##email.html('<html><body>This is a text body. <strong>Foo bar.</strong></body></html>')  # Optional
#email.send()
