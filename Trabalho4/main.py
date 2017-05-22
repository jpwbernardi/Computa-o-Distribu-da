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
        try:
            self.vectorClock[self.name] += 1
        except:
            self.vectorClock[self.name] = 1;
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

_lock = 0

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
    global _lock
    name = request.forms.getunicode('name')
    msg = request.forms.getunicode('msg')
    global messages
    if name != None and msg != None:
        while _lock == 1:
            continue
        _lock = 1
        vc.increment()
        _lock = 0
        a = (name, msg, frozendict(vc.vectorClock))
        messages.add(a)
        redirect('chat?name=' + name)
    else:
        redirect('chat')

@get('/peers')
def dora():
    return json.dumps(peers)

@get('/max')
def maxvc():
    global _lock
    while _lock == 1:
        continue
    _lock = 1;
    ret = json.dumps(vc.vectorClock)
    _lock = 0;
    return ret

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
    print(">>>>>>>>>>>" + link)
    try:
        r = requests.get(link)
        if r.status_code == 200:
            obj = json.loads(r.text)
            setT = set((a, b, frozendict(t)) for [a,b,t] in obj)
        return setT
    except:
        print("Connection Error5")
    return set([])

def prepare():
    global _lock
    #Fazemos o inverso: pede para todo mundo "E aí? Vamo fechá?"
    setpeer = set(peers)
    ack = 0
    total = len(setpeer) - 1 #Eu não me conto
    for p in setpeer:
        link = p + "/time?id=" + sys.argv[1]  + str(vc)
        print(link)
        try:
            r = requests.get(link)
            if r.status_code == 200:
                for line in r:
                    r = line.strip()
                r = r.decode('utf-8');
                print(r)
                if r == "ACK":
                    ack += 1
                    print("AAAAAAAEEEEEE")
                else:
                    while _lock == 1:
                        continue
                    _lock = 1
                    vc.increment() #Vamo ve onde incrementar... Aqui parece errado. MUDEM ISSOOO!!!!
                    _lock = 0
        except:
            print("Connection Error4")
    print(">>>>>>>> "+ str(ack) + " >= "+ str(total * 0.75))
    if (ack >= total * 0.75): #Contatinhos o suficiente
        accept();

@get('/time')
def promise():
    global vc
    dic = parse_qs(request.query_string)
    #print(dic)
    propid = dic['id'] #ID é quem mandou o "E aí? Vamo fechá?"
    propvc = ['', '', {}]
    for k, v in dic.items():
        if k == 'id':
            continue
        else:
            propvc[2]['http://localhost:' + k] = int(v[0]);
    myvc = ['', '', vc.vectorClock]
    #print("+++++")
    #print(myvc);
    #print("-----")
    #print(propvc);
    #print('*****');
    #return 'ACK';
    if menor(myvc, propvc):
        #vc.vectorClock = myvc;
        return "ACK";
    else:
        return "NACK";

def accept():
    global _lock, vc
    maior = vc.vectorClock
    for p in peers:
        #try:
        pvc = None
        obj = {}
        try:
            pvc = requests.get(p + "/max")
        except:
            print("Connection Error3");
        if pvc == None:
            continue
        if pvc.status_code == 200:
            obj = json.loads(pvc.text)
        if menor(['', '', maior], ['', '', obj]):
            maior = obj;
        print("++++")
        print(maior)
        print("----")
        print(obj)
        print("****")
    while _lock == 1:
        continue
    _lock = 1;
    vc.vectorClock = maior;
    vc.increment()
    _lock = 0;
    for p in peers:
        try:
            requests.get(p + '/att?id=' + sys.argv[1])
        except:
            print("Connection Error2")
    print("ASHAIOOO" + str(maior))

@get('/att')
def att():
    print("VLADIMIR, COMO VC N VIU ANTES O ERRO?")
    global messages, _lock, vc
    id = request.query.id
    if id == None:
        return
    print(id)
    mvc = None
    try:
        mvc = requests.get('http://localhost:' + str(id) + '/max');
    except:
        print("Connection Error1")
    print("\n" + str(mvc) + "\n")
    if mvc != None and mvc.status_code == 200:
        obj = json.loads(mvc.text)
        #Hm... Caso esteja vazio, vamos transformar obj em um dict
        try:
            obj.keys();
        except:
            obj = {}
            print("Ebaaaaaaaa")
        try:
            vc.vectorClock.keys()
        except:
            print("\nCagou :)\n")
        if menor(['', '', vc.vectorClock], ['', '', obj]):
            while _lock == 1:
                continue
            _lock = 1
            vc.vectorClock = obj
            _lock = 0
            m = getMessagesFrom('http://localhost:' + id)
            for (n, m, t) in m.difference(messages):
                vc.update(t)
                messages.add((n, m, t))
            

def attmessage():
    while True:
        time.sleep(1)
        prepare();

t = threading.Thread(target=client)
t.start()

t1 = threading.Thread(target=attmessage)
t1.start()

run(host='localhost', port=int(sys.argv[1]))


