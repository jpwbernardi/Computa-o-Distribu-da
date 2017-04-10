# -*- coding: utf-8 -*-
from bottle import run, get, post, view, request, redirect, route, static_file, template
from frozendict import frozendict
import bottle
import json
import threading
import requests
import time
import sys

class VC:
    def __init__(self, name):
        self.name = name
        self.vectorClock = { self.name: 0 }

    def __repr__(self):
        return "V%s" % repr(self.vectorClock)

    def increment(self):
        self.vectorClock[self.name] += 1
        return self

    def update(self, t):
        self.increment()
        for k, v in t.items():
            if k not in vc.vectorClock or vc.vectorClock[k] < t[k]:
                vc.vectorClock[k] = v

messages = set([])
peers = ['http://localhost:' + p for p in sys.argv[2:]]
lock = threading.Lock()
vc = VC('http://localhost:' + sys.argv[1]);

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
        vc.increment()
        a = (name, msg, frozendict(vc.vectorClock))
        #print(a)
        messages.add(a)
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
    return json.dumps([(n, m, dict(t)) for (n, m, t) in messages])

def getMessagesFrom(p):
    link = p + "/messages"
    try:
        r = requests.get(link)
        if r.status_code == 200:
            obj = json.loads(r.text)
            setT = set((a, b, frozendict(t)) for [a,b,t] in obj)
        return setT
    except:
        print("Connection Error")
    return set([])

def attmessage():
    while True:
        time.sleep(1)
        print("\n\n")
        print(vc.vectorClock)
        print("\n\n")
        N = set([])
        global messages
        for p in peers:
            time.sleep(1)
            m = getMessagesFrom(p)
            print(m)
            for (n, m, t) in m.difference(messages):
                vc.update(t)
                N.add((n, m, t))
        messages = messages.union(N)

t = threading.Thread(target=client)
t.start()

t1 = threading.Thread(target=attmessage)
t1.start()

run(host='localhost', port=int(sys.argv[1]))


