#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import operator
import json

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

from flask import Flask, make_response, request, Response, jsonify
from flask_httpauth import HTTPTokenAuth


app = Flask(__name__)
auth = HTTPTokenAuth("Token")

@auth.verify_token
def verify_token(token):
    return token == os.getenv("BY7_KEY")

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route('/', methods = ['GET'])
def index():
    """Welcome to Ansible API"""
    return jsonify({'hello': 'What would you like to automate today?'})

@app.route('/api', methods=['GET', 'POST'])
@auth.login_required
def main_route():
    if request.json:
        json_data = request.get_json()
        firesult = main_process(json_data)
        return firesult
    else:
        return "No json received"

def main_process(json_data):


if __name__ == "__main__":
	app.run("0.0.0.0",use_reloader=True,port=9900)

class ResultCallback(CallbackBase):
    def main_callback_on_ok(self, result, **kwargs):
        host = result._host
        data = {'status' : '200', 'itens' : host}
        return jsonify(data)
