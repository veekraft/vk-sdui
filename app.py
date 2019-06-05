import uuid
import time
import os, sys
import re
import boto
import redis
import requests
from flask import Flask, jsonify, render_template, redirect, request, url_for, make_response
import flask
from werkzeug import secure_filename
from PIL import Image, ImageOps
#import hashlib
import json

app = Flask(__name__)
my_uuid = str(uuid.uuid1())
username = ""
userstatus = "0"
# uuid = "0"

@app.route('/')
def menu():

    current = int(time.time())-time.timezone
    global userstatus
    # global uuid
    # global my_uuid

    # print("UUID STRING: %s" % my_uuid)

    uuid = request.cookies.get('uuid')
    if uuid and not uuid == "0":
        userstatus = "1"
    else:
        userstatus = "0"


    resp = make_response(render_template('main_menu.html', userstatus=userstatus, uuid=uuid))

    return resp

@app.route('/loginform', methods=['GET','POST'])
def loginform():

    global uuid
    global username
    global userstatus

    uuid        = request.cookies.get('uuid')


    if request.method == 'POST':

        username    = request.form['username']
        password    = request.form['password']


    if not uuid:
        # No UUID, the user need to authenticate OR the user credentials were invalid
        print "uuid cookie was not present"

        if request.method == 'GET':
            # First time user accesses page. Show login form
            resp = make_response(render_template('loginform.html', login="loginform", status=""))

        else:
            # Method is POST. User is trying to authenticate
            # url = 'http://localhost:5010/api/v1/auth'

            # url = 'http://servicedogauth.cfapps.io:5010/api/v1/auth'
            # payload = {"username": username,"password":password}
            # headers = {'content-type': 'application/json'}
            #
            # response = requests.post(url, payload).text
            # response = json.loads(response)
            #
            # userstatus  = response['userstatus']
            # userrole    = response['userrole']

            userstatus  = "1"
            userrole    = "administrator"


            if userstatus == "1":
                # User login successful
                resp = make_response(render_template('logincomplete.html', uuid=my_uuid))
                resp.set_cookie('uuid',str(my_uuid), max_age=1800)

            elif userstatus == "0":
                # User has a failed login
                resp = make_response(render_template('loginform.html', login="loginform", status="Username or password was incorrect. Please try again."))
    else:
        resp = make_response(render_template('logincomplete.html', uuid=my_uuid))
        resp.set_cookie('uuid',str(my_uuid), max_age=1800)

    return resp


@app.route('/logout', methods=['GET','POST'])
def logout():
    global uuid

    uuid = request.cookies.get('uuid')

    if not uuid:
        # No UUID, the user need to authenticate OR the user credentials were invalid
        print "User trying to log out but is not logged in."
        resp = make_response(render_template('logoutform.html', status="Session not active. No need to log out."))

    else:
        resp = make_response(render_template('logoutform.html', status="Your session has been closed."))
        resp.set_cookie('uuid',str(my_uuid), max_age=0)

    return resp



@app.route('/dogs')
def dogs():
    # global userstatus
    resp = make_response(render_template('dogs.html', userstatus=userstatus))
    return resp

@app.route('/searchdog') # search page which submits to viewdog
def searchdog():
    resp = make_response(render_template('searchdog.html', viewdog="viewdog"))
    return resp

@app.route('/viewdog', methods=['POST']) # displays result of dog ID search in searchdog
def viewdog():

    global username

    outstring = ""
    allvalues = sorted(request.form.items())
    for key,value in allvalues:
        outstring += key + ":" + value + ";"
    print outstring


    userid = "admin"
    sd_regid = request.form['dogid']

    url = 'http://servicedogwfe.cfapps.io/api/v1/dog/view'

    # payload = {"userid": username,"sd_regid":sd_regid}
    payload = {"userid": userid,"sd_regid":sd_regid}

    # response = requests.post(url, payload).text
    response = requests.get(url, params=payload)
    print("RESPONSE: %s" % response)

    whatever = json.loads(response.content)
    # print whatever["sd_regid"]
    # print whatever["sd_name"]

    # response = allvalues

    resp = make_response(render_template('viewdog.html', doginfo=whatever))

    return resp


@app.route('/registerdog', methods=['GET','POST'])
def registerdog():
    global uuid
    resp = make_response(render_template('registerdog.html', registrationaction="registrationaction", uuid=uuid))
    return resp

@app.route('/registrationaction', methods=['POST']) # displays result of dog ID search in searchdog
def registrationaction():

    dogname = request.form['dogname']
    dogpic  = request.form['dogpic']

    # Get ID from dog registration service
    dogid = "123abc"

    # Upload pic to S3
    s3_access_key_id    = ''
    s3_secret_key       = ''

    session = boto.connect_s3(s3_access_key_id, s3_secret_key, host='s3.us-east-1.amazonaws.com')

    bname = 'jwr-piedpiper-01'
    b = session.get_bucket(bname)



    k = b.new_key(dogpic)
    k.set_metadata('dogid', dogid)
    k.set_contents_from_filename(dogpic)
    k.set_acl('public-read')

    resp = make_response(render_template('registered.html', dogid=dogid))
    return resp



@app.route('/handlers')
def handlers():
    # global userstatus
    resp = make_response(render_template('handlers.html', userstatus=userstatus))
    return resp


@app.route('/searchhandler') # search page which submits to viewdog
def searchhandler():
    resp = make_response(render_template('searchhandler.html', viewhandler="viewhandler"))
    return resp


@app.route('/viewhandler', methods=['POST']) # displays result of dog ID search in searchdog
def viewhandler():

    global username

    outstring = ""
    allvalues = sorted(request.form.items())
    for key,value in allvalues:
        outstring += key + ":" + value + ";"
    print outstring


    userid = "admin"
    sd_regid = request.form['handlerid']

    url = 'http://servicedogwfe.cfapps.io/api/v1/handler/view'

    # payload = {"userid": username,"sd_regid":sd_regid}
    payload = {"userid": userid,"sd_regid":sd_regid}

    # response = requests.post(url, payload).text
    response = requests.get(url, params=payload)
    print("RESPONSE: %s" % response)

    whatever = json.loads(response.content)
    # print whatever["sd_regid"]
    # print whatever["sd_name"]

    # response = allvalues

    resp = make_response(render_template('viewhandler.html', handlerinfo=whatever))

    return resp




@app.route('/uid')
def uid():
    uuid = request.cookies.get('uuid')
    return "Your user ID is : " + uuid

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', '5000')), threaded=True)
