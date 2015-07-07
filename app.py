#!/usr/bin/env python
from __future__ import print_function
import json
import requests
import sys
import os
import time
from flask import Flask, request, Response, jsonify
from functools import wraps

Flask.get = lambda self, path: self.route(path, methods=['get'])


##################################The Setup###############################################
vcap_services = json.loads(os.getenv("VCAP_SERVICES"))
client_id = None
client_secret = None
uaa_uri = None
api = None
port = 8003
expire_time = 0
token = None

if 'PORT' in os.environ:
    port = int(os.getenv("PORT"))

app = Flask(__name__)

for service in vcap_services['user-provided']:
    if 'uaa' == service['name']:
        client_id = service['credentials']['client_id']
        client_secret = service['credentials']['client_secret']
        uaa_uri = service['credentials']['uri']
    elif 'cloud_controller' == service['name']:
        api = service['credentials']['uri']

###################################The Auth##############################################

def check_auth(user, password):
    return user == client_id and password == client_secret


def authenticate():
    return Response('You must be authenticated to use this application', 401,
                    {"WWW-Authenticate": 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


##############################The bidness logic##########################################
def get_token():
    global expire_time, token
    if expire_time < time.time():
        client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        r = requests.get(url=uaa_uri, headers={'accept': 'application/json'},
                         params={'grant_type': 'client_credentials'}, auth=client_auth, verify=False)
        expire_time = time.time() + (int(r.json()['expires_in']) - 60)
        token = r.json()['access_token']
        print("Token expires at " + str(expire_time))
    return token


def cf(path):
    access_token = "bearer " + get_token()
    hdr = {'Authorization': access_token}
    r = requests.get(api + path, headers=hdr, verify=False)
    if r.status_code != 200:
        print("Failed to call CF API (" + path + ")", file=sys.stderr)
    return r.json()


def get_events():
    return cf('/v2/events')


###################################Controllers#################################

@app.get('/events')
@requires_auth
def events():
    return jsonify(get_events())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
