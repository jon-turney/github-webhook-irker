#!/usr/bin/env python3
#
# Tell irked to send a message to an IRC channel
#
# First argument must be a channel URL. If it does not begin with "irc",
# the base URL for libera.chat is prepended.
#
# SPDX-License-Identifier: BSD-2-Clause

import json
import socket
import sys

import config

DEFAULT_SERVER = ("localhost", 6659)
DEFAULT_TARGET = config.IRC_TARGET


def connect(server=DEFAULT_SERVER):
    return socket.create_connection(server)


def send(s, target, message):
    data = {"to": target, "privmsg": message}
    s.sendall(bytes(json.dumps(data), "ascii"))


def irk(message, target=DEFAULT_TARGET, server=DEFAULT_SERVER):
    if not isinstance(target, list):
        target = [target]

    for t in target:
        try:
            s = connect(server)
            if "irc:" not in t and "ircs:" not in t:
                t = "irc://chat.libera.chat/{0}".format(t)

            send(s, t, message)

            s.close()
        except OSError:
            pass


def main():
    message = " ".join(sys.argv[1:])

    try:
        irk(message)
    except socket.error as e:
        sys.stderr.write("irk: write to server failed: %r\n" % e)
        sys.exit(1)


if __name__ == '__main__':
    main()
