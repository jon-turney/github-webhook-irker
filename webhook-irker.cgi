#!/usr/bin/env python3

import cgitb
import hashlib
import hmac
import json
import os
import sys
import traceback

import config
import events


def process(data):
    j = json.loads(data)

#    basedir = os.path.dirname(os.path.realpath(__file__))
#    with open(os.path.join(basedir, 'last.json'), 'w') as f:
#        print(json.dumps(j, sort_keys=True, indent=4), file=f)

    event_type = os.environ['HTTP_X_GITHUB_EVENT']
    events.handle_event(event_type, j)


def hook():
    if os.environ['REQUEST_METHOD'] != 'POST':
        return '400 Bad Request', ''

    if os.environ['CONTENT_TYPE'] != 'application/json':
        return '400 Bad Request', ''

    data = sys.stdin.read()

    secret = config.secret
    if not secret:
        return '401 Unauthorized', ''

    sig = 'sha256=' + hmac.new(secret.encode(), data.encode(),
                               hashlib.sha256).hexdigest()
    trysig = os.environ.get('HTTP_X_HUB_SIGNATURE_256', '')
    if trysig != sig:
        return '401 Unauthorized', ''

    process(data)

    return '200 OK', ''


if __name__ == '__main__':
    cgitb.enable()
    try:
        status, content = hook()
        print('Status: %s' % status)
        print()
        print(content)
    except BaseException:
        # log exception to stderr
        traceback.print_exc()
        # allow cgitb to do it's thing
        print('Content-Type: text/plain')
        print('Status: 422')
        print()
        raise
