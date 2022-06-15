#!python

from http.server import BaseHTTPRequestHandler, HTTPServer
from flask import Flask
import urllib.parse as urlparse
import json
import os #for logging

PORT = 1337

  # HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

  def logToFile(msg):
    writepath = './out.txt'

    mode = 'a' if os.path.exists(writepath) else 'w'
    with open(writepath, mode) as f:
      f.write(msg + "\n")
    return
 
  # An Http Get is the challenge or subscription denial, a POST - the notification
  def do_GET(self):
    #Parse request for challenge GET
    message=""
    params=urlparse.urlparse(self.path).query 
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
        logMessage = logMessage + mode + " successful. Echoing challenge: " +challenge + "\n"
        
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
    self.send_response(200)

    # Send headers
    self.send_header('Content-type','text/html')
    self.end_headers()

    logMessage = logMessage + "\n" + "HTTP Body: \n " + message + "\n"

    
    # Send message back to client
    # Write content as utf-8 data
    self.wfile.write(bytes(message, "utf8"))
    print(logMessage)
    return

    
  # An Http POST is the the notification that a relevent event has occurred for a subscribed topic
  def do_POST(self):
  
    logMessage = "Handling HTTP Post\n"
  
    # get X-Hub-Signature header value and validate
    params=urlparse.urlparse(self.path).query 
    logMessage = logMessage + "notification: " + params + "\n"
    
    content_length = int(self.headers['Content-Length'])
    post_body = self.rfile.read(content_length)
    body = json.loads(post_body)
    
    #message = body.event.hub.event
    logMessage = logMessage + "\n" + "HTTP Body: \n " + json.dumps(body) + "\n"
    
    # Send response status code
    self.send_response(200)

    # Send headers
    self.send_header('Content-type','text/html')
    self.end_headers()

    # Send message back to client
    # Write content as utf-8 data
    #self.wfile.write(bytes(message, "utf8"))
    print(logMessage)
    return
    
#def run():
#  print('starting server...')
 
#  # Server settings
#  server_address = ('127.0.0.1', PORT)
#  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
#  print('running server...')
#  httpd.serve_forever()
 
 
#run()