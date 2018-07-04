#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import operator
import json
import logging
from listroles import listRoles

from flask import Flask, make_response, request, Response, jsonify
from flask_httpauth import HTTPTokenAuth

class LoggingCallbacks(Flask):
    def log(self, level, msg, *args, **kwargs):
        logging.log(level, msg, *args, **kwargs)

    def on_task_start(self, name, is_conditional):
        self.log(logging.INFO, 'task: {0}'.format(name))
        super(LoggingCallbacks, self).on_task_start(name, is_conditional)

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
    """Welcome to BySeven Ansible API"""
    return jsonify({'hello': 'What would you like to automate today?'})

@app.route('/api', methods=['GET'])
@auth.login_required
def api_index():
    """These are the available APIS."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)

@app.route('/api/roles/', methods = ['GET'])
def getRoles():
    """A list of installed Roles"""
    return jsonify(listRoles(ROLES_DIR))

@app.route('/api/roles/github/get', methods = ['GET','POST'])
def getRole():
    """Run an Ansible Playbook"""
    if request.method == 'POST':
        r_u = request.values.get("username")
        r_r = request.values.get("role")
        process = subprocess.Popen(["/usr/bin/git", "clone", "https://git.byseven.com.br/byseven/Automation/Ansible/playbooks/"+ str(r_u) + '/' + str(r_r) + ".git", os.path.join(ROLES_DIR,r_r)])
        return jsonify({'RunningPlay': {'name': r_r}})
    else:
       return '''Currently only github is supported
curl --request POST \
  --url http://127.0.0.1:8080/api/run/ \
  --data 'username=donnydavis' \
  --data 'role=ansible-rh-subscription-manager'
       '''

if __name__ == "__main__":
	app.run("0.0.0.0",use_reloader=True,port=9900)

