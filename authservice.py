#import uuid
import time
import os, sys
import re
import boto
import redis
from flask import Flask, jsonify, render_template, redirect, request, url_for, make_response
import flask
from werkzeug import secure_filename
from PIL import Image, ImageOps
#import hashlib
import json

app = Flask(__name__)


@app.route('/api/v1/auth', methods=['GET','POST'])
def auth():

    username = ""
    password = ""

    data = request.form # get credentials from login page

    print("data is: %s" % data)

    data = request.form.to_dict()
    username = data['username']
    password = data['password']

    # username = request.form.get('username[]')
    # print("USERNAME IS: %s" % username)
    #
    #
    # username = data['username'][0]
    # username = json.loads(username)
    # print("USERNAME IS: %s" % user)

    # items = request.form.viewitems(data)
    # password = data['password']


    # print password

    if username == "admin" and password == "secret":
        userstatus  = "1"
        userrole    = "admin"
        print "User login successful"

    else:
        userstatus  = "0"
        userrole    = "none"
        print "User login failed"

    response = {'userstatus' : userstatus, 'userrole' : userrole}

    return jsonify(response)

    return resp



if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', '5010')), threaded=True)
