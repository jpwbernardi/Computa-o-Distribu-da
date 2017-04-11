# -*- coding: utf-8 -*-
from bottle import run, get, post, view, request, redirect, route, static_file, template
import bottle
import json
import threading
import requests
import time
import sys

messages = set([])
peers = ['localhost:' + p for p in sys.argv[2:]]
lock = threading.Lock()

@bottle.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')

@get('/chat')
@view('chat')
def chat():
    name = request.query.name
    #print(messages)
    return dict(msg=list(messages), name=name)

@route('/')
def index():
    return


@post('/send')
def sendmsg():
    name = request.forms.getunicode('name')
    msg = request.forms.getunicode('msg')
    global messages
    if name != None and msg != None:
        print(msg)
        messages.add((name, msg))
        print(messages)
        redirect('chat?name=' + name)
    else:
        redirect('chat')

@get('/peers')
def dora():
    return json.dumps(peers)

def client():
    global lock
    time.sleep(5)
    while True:
        time.sleep(1)
        np = []
        for p in peers:
            try:
                r = requests.get(p + '/peers')
                np.append(p)
                np.extend(json.loads(r.text))
            except:
                pass

            time.sleep(1)
        with lock:
            peers.extend(list(set(np)))

@get('/messages')
def msg():
    return json.dumps(list(messages))

def getMessagesFrom(p):
    link = "http://" + p + "/messages"
    try:
        r = requests.get(link)
        if r.status_code == 200:
            obj = json.loads(r.text)
            setT = set((a, b) for [a,b] in obj)
            return setT
    except:
        print("Connection Error")
    return set([])

def attmessage():
    while True:
        time.sleep(1)
        N = set([])
        global messages
        for p in peers:
            time.sleep(1)
            m = getMessagesFrom(p)
            print(m)
            if m.difference(messages):
                N = N.union(m.difference(messages))
        messages = messages.union(N)

t = threading.Thread(target=client)
t.start()

t1 = threading.Thread(target=attmessage)
t1.start()

run(host='localhost', port=int(sys.argv[1]))


