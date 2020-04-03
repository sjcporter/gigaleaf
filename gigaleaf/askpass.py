#!/usr/bin/env python3
#
# Script to configure git credentials.
# Requires GIT_USERNAME and GIT_PASSWORD environment variables,
# intended to be called by Git via GIT_ASKPASS.
#

from sys import argv
from os import environ


def askpass() -> None:
    """Helper method that is automatically called when running git commands that may need credentials"""
    if 'username' in argv[1].lower():
        print(environ['OVERLEAF_EMAIL'])
        exit()

    if 'password' in argv[1].lower():
        print(environ['OVERLEAF_PASSWORD'])
        exit()

    exit(1)
