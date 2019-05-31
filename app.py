#import uuid
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



@app.route('/')
def menu():

    current = int(time.time())-time.timezone
    loginstatus = "0"

    uuid = request.cookies.get('uuid')
    if uuid:
        loginstatus = "1"


    resp = make_response(render_template('main_menu.html', loginstatus=loginstatus))

    return resp


@app.route('/loginform', methods=['GET','POST'])
def loginform():

    global uuid

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
            url = 'http://localhost:5010/api/v1/auth'
            payload = {"username": username,"password":password}
            headers = {'content-type': 'application/json'}

            response = requests.post(url, payload).text
            response = json.loads(response)

            userstatus  = response['userstatus']
            userrole    = response['userrole']


            print("Credentials: %s" % response)

            print("USERSTATUS: %s" % userstatus)


            if userstatus == "1":
                # User login successful
                resp = make_response(render_template('logincomplete.html', uuid=uuid))
                resp.set_cookie('uuid',str(uuid), max_age=604800)

            elif userstatus == "0":
                # User has a failed login
                resp = make_response(render_template('loginform.html', login="loginform", status="Username or password was incorrect. Please try again."))
    else:
        resp = make_response(render_template('logincomplete.html', uuid=uuid))
        resp.set_cookie('uuid',str(uuid), max_age=604800)

    return resp



@app.route('/dogs')
def dogs():
    resp = make_response(render_template('dogs.html', suthankyou="stuff.html"))
    return resp

@app.route('/searchdog') # search page which submits to viewdog
def searchdog():
    resp = make_response(render_template('searchdog.html', viewdog="viewdog"))
    return resp

@app.route('/viewdog', methods=['POST']) # displays result of dog ID search in searchdog
def viewdog():

    outstring = ""
    allvalues = sorted(request.form.items())
    for key,value in allvalues:
        outstring += key + ":" + value + ";"
    print outstring

    dogid = request.form['dogid']

    resp = make_response(render_template('viewdog.html', dogid=dogid))
    return resp


@app.route('/registerdog', methods=['GET','POST'])
def registerdog():
    resp = make_response(render_template('registerdog.html', registrationaction="registrationaction"))
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




@app.route('/uid')
def uid():
    uuid = request.cookies.get('uuid')
    return "Your user ID is : " + uuid

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', '5000')), threaded=True)




# @app.route('/upload', methods=['POST'])
# def upload():
#     global size
#     global b
#     global r
#
#     file = request.files['file']
#     if file and allowed_file(file.filename):
#         # Make the filename safe, remove unsupported chars
#         filename = secure_filename(file.filename)
#         justname = filename.rsplit(".",1)[0]
#         justname = justname + str (int (time.time() * 1000))
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#
#         thumbfile = justname + "-thumb.jpg"
#         try:
#             im = Image.open("uploads/" + filename)
#             thumb = ImageOps.fit(im, size, Image.ANTIALIAS)
#             thumb.save("uploads/" + thumbfile, "JPEG")
#             im.close()
#             thumb.close()
#         except IOError:
#             print "cannot create thumbnail for", filename
#
#         print "Uploading " + filename + " as key " + justname
#         k = b.new_key(justname)
#         k.set_contents_from_filename("uploads/" + filename)
#         k.set_acl('public-read')
#
#
#
# @app.route('/suthankyou.html', methods=['POST'])
# def suthankyou():
#
#     uuid = request.cookies.get('uuid')
#     if not uuid:
#         uuid = 0
#     outstring = "uuid:" + str(uuid) + ";"
#
#     allvalues = sorted(request.form.items())
#     for key,value in allvalues:
#         outstring += key + ":" + value + ";"
#     print outstring
#
#     print "the counter is now: ", Counter
#     newsurvey = 'survey' + str(Counter)
#     print "Lets create Redis hash: " , newsurvey
#     r.hmset(newsurvey,{'review_string':outstring})
#
#     resp = make_response(render_template('survey_action.html'))
#     return resp
