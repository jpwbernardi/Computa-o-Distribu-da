# -*- coding: utf-8 -*-
from bottle import run, get, post, view, request, redirect, route, static_file, template
from frozendict import frozendict
import bottle
import json
import threading
import requests
import time
import sys
from urllib.parse import parse_qs

class VC:
    def __init__(self, name):
        self.name = name
        self.vectorClock = { self.name: 0 }

    def __repr__(self):
        return "V%s" % repr(self.vectorClock)

    def __str__(self):
        ret = ""
        for k, v in self.vectorClock.items():
            ret += "&" + k[17:] +"=" + str(v)
        return ret;
        #return "V%s" % repr(self.vectorClock)

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


def menor(a, b):
    keys  = list(set(a[2].keys()).union(b[2].keys()))
    keys.sort()
    a = tuple(a[2][k] if k in a[2] else 0 for k in keys)
    b = tuple(b[2][k] if k in b[2] else 0 for k in keys)
    for i in range(0, len(a)):
        if a < b: return True
        if b < a: return False
    return False

allmsg = []

def ordenar():
    global allmsg
    for i in range(1, len(allmsg)):
        chave = allmsg[i]
        k = i
        while k > 0 and menor(chave, allmsg[k - 1]):
            allmsg[k] = allmsg[k - 1]
            k -= 1
            allmsg[k] = chave

@get('/chat')
@view('chat')
def chat():
    global allmsg
    name = request.query.name
    allmsg = list(messages)
    ordenar()
    return dict(msg=list(allmsg), name=name)

@route('/')
def index():
    redirect('chat')


@post('/send')
def sendmsg():
    name = request.forms.getunicode('name')
    msg = request.forms.getunicode('msg')
    global messages
    if name != None and msg != None:
        vc.increment()
        a = (name, msg, frozendict(vc.vectorClock))
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

def prepare():
    #Fazemos o inverso: pede para todo mundo "E aí? Vamo fechá?"
    ack = 0
    total = len(peers)
    for p in peers:
        link = p + "/time?id=" + sys.argv[1]  + str(vc)
        print(link)
        try:
            r = requests.get(link)
            if r.status_code == 200:
                if r.text == "ACK":
                    ack += 1
        except:
            print("Connection Error")

@get('/time')
def promise():
    dic = parse_qs(request.query_string)
    #print(dicc)
    propid = dic['id']
    propvc = ['', '', {}]
    for k, v in dic.items():
        if k == 'id':
            continue
        else:
            propvc[2][k] = v
    myvc = ['', '', vc.vectorClock]
    print(myvc[2]);
    return "ACK" if menor(myvc, propvc) else "NACK";
    

def attmessage():
    while True:
        time.sleep(1)
        prepare();
        global messages
        for p in peers:
            time.sleep(1)
            m = getMessagesFrom(p)
            for (n, m, t) in m.difference(messages):
                vc.update(t)
                messages.add((n, m, t))

t = threading.Thread(target=client)
t.start()

t1 = threading.Thread(target=attmessage)
t1.start()

run(host='localhost', port=int(sys.argv[1]))


