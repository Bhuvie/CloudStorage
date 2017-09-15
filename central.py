import os
import json
import swiftclient
import cf_deployment_tracker
from swiftclient.client import AUTH_VERSIONS_V3
from flask import Flask, render_template, redirect, url_for,request
from flask import make_response
from urllib import localhost
from pyDes import *
from _codecs import decode
from datetime import datetime

#Bhuvanesh Rajakarthikeyan
#CSE6311-001 Programming Assignment 1
#Student ID: 1001410051

# Emit Bluemix deployment event
cf_deployment_tracker.track()
PORT = int(os.getenv('PORT', 5050))

app = Flask(__name__)
#if 'VCAP_SERVICES' in os.environ:
cloudant_service = json.loads(os.environ['VCAP_SERVICES'])['Object-Storage'][0]
objectstorage_creds = cloudant_service['credentials']

if objectstorage_creds:
    auth_url = objectstorage_creds['auth_url'] + '/v3'
    project_name = objectstorage_creds['project']
    password = objectstorage_creds['password']
    user_domain_name = objectstorage_creds['domainName']
    project_id = objectstorage_creds['projectId']
    user_id = objectstorage_creds['userId']
    region_name = objectstorage_creds['region']

    # Get a Swift client connection object
conn = swiftclient.Connection(
            key=password,
            authurl=auth_url,
            auth_version='3',
            os_options={"project_id": project_id,
                        "user_id": user_id,
                        "region_name": region_name})
    
    
            
            
@app.route("/")
def index():
    return render_template('index.html')  


@app.route("/viewcf",methods={'GET','POST'})
def viewcf():
     # List your containers
    print ("\nContainer List:")
    jsondata="<thead>Container Names</thead>"
    for container in conn.get_account()[1]:
        print container
        jsondata=jsondata+"<tr><td>"+'Container: {0} \t Size: {1} \t Count: {2}'.format(container['name'], container['bytes'], container['count'])+"</td></tr>"
    return jsondata  

@app.route("/viewf",methods={'GET','POST'})
def viewf():
    # Retrieve files in all the containers, and returns each file name, the file size, and last modified date
    print ("\nObject List:")
    jsondata1="<thead>File Names</thead>"
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            print 'File: {0}\t size: {1}\t date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
            jsondata1=jsondata1+"<tr><td>"+'File: {0} \t size: {1} \t date: {2}'.format(data['name'], data['bytes'], data['last_modified'])+"</td></tr>"
    return jsondata1    

@app.route("/createc",methods={'GET','POST'})
def createc():
    #Create container
    givencontname = request.form['mydata'] 
    container_name1 = givencontname
    conn.put_container(container_name1)
    print "\nContainer %s created successfully." % container_name1
    return "Container created successfully"

@app.route("/createf",methods={'GET','POST'})
def createf():
    #Create file and check the conditions File Size less than 1MB and Total File Sizes less than 10MB
    givencontname = request.form['mydata'] 
    givenfilename = request.form['mydata1']
    givenfiledata = request.form['mydata2']
    givenkey=request.form['mydata3']
    givenkey=givenkey.encode('ascii')
    givenfiledata=givenfiledata.encode('ascii')
    givenfiledata = encod(givenfiledata,givenkey)
    size=0
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            size=size+data['bytes']
            if(size>10485760):
                return "Error: Total size exceeded 10MB limit"
    if(len(givenfiledata)<=1024000):
        with open(givenfilename, 'w') as example_file:
            conn.put_object(givencontname,givenfilename,
            contents= givenfiledata,
            content_type='text/plain')
    else:
        givenfiledata="Error: Size of the file larger than 1MB"
    return "Encoded Text: "+givenfiledata

@app.route('/uploadajax', methods=['POST'])
def upldfile():
     if request.method == 'POST':
        files1 = request.files['file']
        contname=request.form['textbox5']
        givenkey=request.form['textbox6']
        givenkey=givenkey.encode('ascii')
        filedata=files1.read()
        givenfiledata = encod(filedata,givenkey)
        conn.put_object(contname,files1.filename,
            contents= givenfiledata,
            content_type='text/plain')
     return givenfiledata
        


@app.route("/delcont",methods={'GET','POST'})
def delcont():
    #Delete a container
    givencontname = request.form['mydata'] 
    conn.delete_container(givencontname)
    print "\nContainer %s deleted successfully.\n" % givencontname
    return "Container deleted successfully"

@app.route("/delfile",methods={'GET','POST'})
def delfile():
    #Delete a File
    givencontname = request.form['mydata'] 
    givenfilename = request.form['mydata1']
    conn.delete_object(givencontname, givenfilename)
    print "\nObject %s deleted successfully." % givenfilename
    return "File Deleted Successfully"


@app.route("/downfile",methods={'GET','POST'})
def downfile():
    #Download a file
    givencontname = request.form['mydata'] 
    givenfilename = request.form['mydata1']
    givenkey=request.form['mydata2']
    obj = conn.get_object(givencontname, givenfilename)
    return decod(obj[1],givenkey)

#Encrypt and Decrypt functions
def encod(data,password):
    k = des(password, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    d = k.encrypt(data)
    return d

def decod(data,password):
    password=password.encode('ascii')
    k = des(password, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    d = k.decrypt(data)
    return d

port = os.getenv('VCAP_APP_PORT', '8080')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
