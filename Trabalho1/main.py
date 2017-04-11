# -*- coding: utf-8 -*-
from bottle import run, get, post, view, request, redirect, route, static_file, template
import bottle
import json
import threading
import requests
import time
import sys

messages = set([])

@bottle.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')

@get('/chat')
@view('chat')
def chat():
    name = request.query.name
    return dict(msg=list(messages), name=name)

@route('/')
def index():
    redirect('chat')

@post('/send')
def sendmsg():
    name = request.forms.getunicode('name')
    msg = request.forms.getunicode('msg')
    global messages
    if name != None and msg != None:
        messages.add((name, msg))
        redirect('chat?name=' + name)
    else:
        redirect('chat')

run(host='localhost', port=int(sys.argv[1]))


