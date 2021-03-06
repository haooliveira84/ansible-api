#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import operator
import json
import logging
import git
from settings import ROLES_DIR
import subprocess

from listroles import listRoles

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

@app.route('/api/roles', methods = ['GET'])
@auth.login_required
def getRoles():
    """A list of installed Roles"""
    return jsonify(listRoles(ROLES_DIR))

@app.route('/api/roles/gitlab/get', methods = ['GET','POST'])
@auth.login_required
def getRole():
    """Run an Ansible Playbook"""
    if request.method == 'POST':
        r_r = request.values.get("role")
        if os.path.exists(ROLES_DIR + "/" + r_r):
            git.cmd.Git(ROLES_DIR + "/" + r_r).pull
        else:
            git.Git(ROLES_DIR).clone("https://oauth2:xSSwv5yWh1Qc8CVHGZih@git.byseven.com.br/byseven/Automation/Ansible/playbooks/" + "/" + str(r_r) + ".git")
        return jsonify({'Working in git repo': {'name': r_r}})
    else:
       return '''Currently only BySeven GitLab is supported
curl -XPOST \
  -H 'Authorization: Token Tr8DN93e6MFCrH8fO0BASrRtbTTjDJ5X'
  http://127.0.0.1:9900/api/run/ \
  --data 'role=ping'
       '''

@app.route('/api/run/', methods = ['GET','POST'])
@auth.login_required
def runPlay():
    """Run an Ansible Playbook"""
    if request.method == 'POST':
        p = request.values.get("play")
        r = request.values.get("role")
        h = request.values.get("host")
        process = subprocess.Popen(["/usr/local/bin/ansible-playbook", os.path.join(ROLES_DIR,r,p), "-i " + str(h) + ","], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = process.communicate()[0]
        return stdout
    else:
       return '''To use this API
curl -XPOST \
  --url http://127.0.0.1:8080/api/run/ \
  --data 'role=test' \
  --data 'play=hello.yml' \
  --data 'host=localhost'
       '''

if __name__ == "__main__":
	app.run("0.0.0.0",use_reloader=True,port=9900)

