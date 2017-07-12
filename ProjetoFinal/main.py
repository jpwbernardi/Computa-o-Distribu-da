# -*- coding: utf-8 -*-
from bottle import run, get, post, view, request, redirect, route, static_file, template
from frozendict import frozendict
import bottle
import json
import threading
import requests
import time
import sys
import datetime

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
peers = [p for p in sys.argv[2:]]
_lock = threading.Lock()
vc = VC('http://localhost:' + sys.argv[1]);


lock = 0
sendNop = True

def getlock():
    global lock
    while lock == 1:
        continue;
    lock = 1;

def unlock():
    global lock;
    lock = 0;

@bottle.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')

def menor(a, b):
    keys = set()
    for k,v in a[1].items():
        keys.add(k);
    for k,v in b[1].items():
        keys.add(k);
    keys = list(keys)
    keys.sort()
    a = tuple(a[1][k] if k in a[1] else 0 for k in keys)
    b = tuple(b[1][k] if k in b[1] else 0 for k in keys)
    for i in range(0, len(a)):
        if a < b: return True
        if b < a: return False
    return False

def ordena(vetor):
    for i in range(1, len(vetor)):
        chave = vetor[i]
        k = i
        while k > 0 and menor(chave, vetor[k - 1]):
            vetor[k] = vetor[k - 1]
            k -= 1
            vetor[k] = chave

bd = {}

@get('/')
@view('chat')
def chat():
    global bd
    bd = {}
    fila = {}
    for m in messages:
        porta = m[0]
        acao = m[1]
        t = m[2]
        if (porta not in fila.keys()):
            fila[porta] = []
        fila[porta].extend(([(acao, t)]));
    for p in fila.keys():
        ordena(fila[p]);
    menor = 112345678;
    while menor > 1: #Se for 1, já foi tudo :P
        if len(fila) == 0:
            break
        for k in fila.keys():
            if len(fila[k]) < menor:
                menor = len(fila[k])
        for k in fila.keys():
            executa(fila[k][0][0])
            del fila[k][0]
    return dict(msg=bd)

def executa(tupla):
    global bd
    acao = tupla[0];
    par1 = tupla[1];
    par2 = tupla[2];
    if acao == 'Nop':
        return
    if par1 not in bd.keys():
        bd[par1] = 0
    if acao == 'c':
        bd[par1] = int(par2);
    elif acao == 'r':
        del bd[par1]
    elif acao == 'a':
        bd[par1] += bd[par2]
    elif acao == 'ai':
        bd[par1] += int(par2)

@post('/send')
def sendmsg():
    getlock()
    sendNop = False;
    unlock()
    action = request.forms.getunicode('select')
    p1 = request.forms.getunicode('par1')
    p2 = request.forms.getunicode('par2')
    global messages
    if action != None and p1 != None and p2 != None:
        vc.increment()
        a = (sys.argv[1], (action, p1, p2), frozendict(vc.vectorClock))
        getlock()
        timestmp[sys.argv[1]] = datetime.datetime.now();
        unlock()
        messages.add(a)
    redirect('/')

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
                r = requests.get('http://localhost:' + p + '/peers')
                np.append(p)
                np.extend(json.loads(r.text))
            except:
                pass
            time.sleep(1)
        with _lock:
            for p in np:
                if p not in peers and p != sys.argv[1]:
                    getlock()
                    timestmp[p] = datetime.datetime.now();
                    unlock()
                    peers.extend([p]);
                

@get('/messages')
def msg():
    return json.dumps([(p, (a,p1,p2), dict(t)) for (p, (a,p1,p2), t) in messages])

def getMessagesFrom(p):
    link = "http://localhost:" +p + "/messages"
    try:
        r = requests.get(link)
        if r.status_code == 200:
            obj = json.loads(r.text)
            setT = set((p, (a,p1,p2), frozendict(t)) for [p,(a,p1,p2),t] in obj)
            return setT
    except:
        print('Connection Error')
    return set([])

timestmp = {};

def attmessage():
    global timestmp
    while True:
        time.sleep(1)
        global messages
        for p in peers:
            time.sleep(1)
            m = getMessagesFrom(p)
            for (p, m, t) in m.difference(messages):
                vc.update(t)
                getlock()
                timestmp[p] = datetime.datetime.now();
                unlock()
                messages.add((p, m, t))


def nop():
    global sendNop, messages
    while True:
        getlock()
        sendNop = True;
        unlock()
        time.sleep(5);
        if (sendNop == False):
            continue;
        vc.increment()
        a = (sys.argv[1], ('Nop', '0', '0'), frozendict(vc.vectorClock))
        messages.add(a)
               

def fingevivo():
    while True:
        time.sleep(1)
        for p in peers:
            try:
                r = getMessagesFrom(p)
                obj = r.text
            except:
                if datetime.datetime.now() - timestmp[p] >= datetime.timedelta(0, 6): #xama u xamu
                    vc.increment()
                    getlock()
                    timestmp[p] = datetime.datetime.now();
                    unlock()
                    messages.add((p, ('Nop', '0', '0'), frozendict(vc.vectorClock)))

t = threading.Thread(target=client)
t.start()

t1 = threading.Thread(target=attmessage)
t1.start()

t2 = threading.Thread(target=nop)
t2.start()

t3 = threading.Thread(target=fingevivo)
t3.start()

for p in peers:
    getlock()
    timestmp[p] = datetime.datetime.now();
    unlock()

run(host='localhost', port=int(sys.argv[1]))


