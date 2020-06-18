#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module loads the WSGI application specified by FQN in `.serverless-wsgi` and invokes
the request when the handler is called by AWS Lambda.

Author: Logan Raarup <logan@logan.dk>
"""
import importlib
import json
import os
import sys
import traceback
import logging
import azure.functions as func

# Call decompression helper from `serverless-python-requirements` if
# available. See: https://github.com/UnitedIncome/serverless-python-requirements#dealing-with-lambdas-size-limitations
try:
    import unzip_requirements  # noqa
except ImportError:
    pass

root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, root)

def load_config():
    """ Read the configuration file created during deployment
    """
    root = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(root, ".serverless-wsgi"), "r") as f:
        return json.loads(f.read())


def import_app(config):
    """ Load the application WSGI handler
    """
    wsgi_fqn = config["app"].rsplit(".", 1)
    wsgi_fqn_parts = wsgi_fqn[0].rsplit("/", 1)

    if len(wsgi_fqn_parts) == 2:
        root = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(0, os.path.join(root, wsgi_fqn_parts[0]))

    try:
        wsgi_module = importlib.import_module(wsgi_fqn_parts[-1])

        return getattr(wsgi_module, wsgi_fqn[1])
    except:  # noqa
        traceback.print_exc()
        raise Exception("Unable to import {}".format(config["app"]))


# Read configuration and import the WSGI application
config = load_config()
wsgi_app = import_app(config)
main = func.WsgiMiddleware(wsgi_app).main