import yaml

with open("pyalumni.conf", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

app_secret = cfg['flask']['secret']
app_salt = cfg['flask']['secret']

db_engine = cfg['schema']['engine']
db_database = cfg['mysql']['database']
db_user = cfg['mysql']['user']
db_pass = cfg['mysql']['pass']
db_port = cfg['mysql']['port']
db_host = cfg['mysql']['host']
aws_access_key = cfg['email']['sesaccess']
aws_secret_key = cfg['email']['sespass']
from_address = cfg['email']['from']
aws_region = cfg['email']['region']

pyalumni_first = cfg['pyalumni']['first']
