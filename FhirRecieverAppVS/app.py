
from flask import Flask, render_template
from flask import request
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Timer
from flask_socketio import SocketIO, emit
import urllib.parse as urlparse
import json
import os #for logging
import flask
import webbrowser
import time
import requests
#import testHTTPServer_RequestHandler

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

@app.route('/home')
def hello():
    # Render the page
    #print('starting server...')
 
    # Server settings
    #server_address = ('127.0.0.1', 4449)
    #httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    #print('running server...')
    #httpd.serve_forever()
    #return "Hello Python!"
    return render_template('index.html') 


@app.route('/', methods=['GET'])
def do_GET():
    #Parse request for challenge GET
    message=""
    params=urlparse.urlparse(request.url).query 
    mode=urlparse.parse_qs(params).get('hub.mode', None) 
    logMessage = "Handling HTTP Get\n"
    
    if mode: 
      mode=mode[0]
      if mode == 'subscribe' or mode ==  'unsubscribe':
        # validate other GET params here TODO
        challenge=urlparse.parse_qs(params).get('hub.challenge', None)          
        if challenge: 
          challenge=challenge[0]
          message=challenge
        #logMessage = logMessage + mode + " successful. Echoing challenge: " +challenge + "\n"
        
      elif mode == 'denied':
        error="Hub deleted subscription"
        # delete subscription here
        reason=urlparse.parse_qs(params).get('hub.reason', None)
        if reason: 
          reason=reason[0]
          error= error + ": " + reason
        message=error
        logMessage = logMessage + error  + "\n"
      else:
        logMessage = logMessage + "programmer error"  + "\n"
    # Send response status code
    resp = flask.Response(status=200)
    #self.send_response(200)

    # Send headers
    resp.headers['Content-type'] = 'text/html'
    resp.headers['charset'] = 'utf-8'
    resp.data=message

    # Send message back to client
    return resp


@app.route('/', methods=['POST'])
# An Http POST is the the notification that a relevent event has occurred for a subscribed topic
def do_POST():
  
    logMessage = "Handling HTTP Post\n"
  
    # get X-Hub-Signature header value and validate
    params=urlparse.urlparse(request.url).query 
    logMessage = logMessage + "notification: " + params + "\n"
    
    content_length = int(request.headers['Content-Length'])
    #post_body = self.rfile.read(content_length)
    post_body = request.data
    body = json.loads(post_body)
    event = body['event']
    hubEvent = event['hub.event'];
    context = event['context']
    patientResource = context[0]
    imagingResource = context[1]
    patientDetials = patientResource['resource']
    imagingDetails = imagingResource['resource']
    patientId = patientDetials['id']
    accessionId = imagingDetails['id']
    #handle_my_custom_event([patientId,accessionId])
    socketio.emit('processing-finished', json.dumps({'patientId': patientId , 'accessionId': accessionId, 'hubEvent':hubEvent}))
    # Send response status code
    resp = flask.Response(status=200)

    # Send headers
    resp.headers['Content-type'] = 'text/html'
    resp.headers['charset'] = 'utf-8'

    # Send message back to client
    # Write content as utf-8 data
    return resp
    #return "Message recieved";
 

@socketio.on('long-running-event')
def handle_my_custom_event(input_json):
    r = requests.post('http://localhost:5000/api/hub', data = {'hub.callback':'http://localhost:4449','hub.mode':'subscribe','hub.topic':input_json['topic'],'hub.secret':'secret','hub.events':input_json['events'],'hub.lease_seconds':'3600'})
    emit('subscribe', json.dumps({'data': r.status_code}))


@socketio.on('unsubscribe-operation')
def handle_my_custom_event(input_json):
    r = requests.post('http://localhost:5000/api/hub', data = {'hub.callback':'http://localhost:4449','hub.mode':'unsubscribe','hub.topic':input_json['data'],'hub.secret':'secret1','hub.events':'open-patient-chart','hub.lease_seconds':'3600'})
    emit('unsubscribe', json.dumps({'data': r.status_code}))

@socketio.on('update-operation')
def handle_my_custom_event(input_json):
    reqBody = """
    {
  "timestamp": "5/11/2022 3:39:02 PM",
  "id": "d0078d88-7357-4dfd-9c7f-e5e3e739b703",
  "event": {
  "hub.topic": "topic1",
  "hub.event": "%s",
  "context": [
    {
      "key": "patient",
      "resource": {
  "resourceType": "Patient",
  "id": "%s"
}
    },
    {
      "key": "imagingstudy",
      "resource": {
  "resourceType": "ImagingStudy",
  "id": "%s"
}
    }
  ]
}
}
    """

    reqBody=reqBody % (input_json['patientAction'],input_json['patientId'],input_json['accessionId'])

    r = requests.post('http://localhost:5000/api/hub/topic1', data = reqBody)
    emit('update', json.dumps({'data': r.status_code}))

def open_browser():
      webbrowser.open_new('http://127.0.0.1:4449/hello')

if __name__ == '__main__':
    # Run the app server on localhost:4449
    #webbrowser.open_new('http://127.0.0.1:4449/hello')
    #app.run(port=4449);
    #app.run('localhost', 4449)
    #socketio.run(app)
    socketio.run(app, host='localhost', port=4449)
